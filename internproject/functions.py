import pandas as pd 
import plotly.express as px 
import plotly.io as pio 
from internproject.constants import ROOT_DATA_DIR
import warnings
from pathlib import Path 
import plotly.graph_objects as go
from plotly.subplots import make_subplots

ZAPPER_ADDRESS = '0x271fbE8aB7f1fB262f81C77Ea5303F03DA9d3d6A'
NULL_ADDRESS = "0x0000000000000000000000000000000000000000"

# 1. read into data of chosen dataframes 
def read_file(file_path):
    ROOT_DIR = Path(__file__).parent.parent
    ROOT_DATA_DIR = ROOT_DIR / "data"     

    file_path = Path(ROOT_DATA_DIR) / file_path 

    data_frame = pd.read_csv(file_path, index_col=0, parse_dates=True)
    return data_frame

# 2. market eth tvl vs raw incentive apr graphs 
def market_tvl_vs_apr(data_frame): 
    x_col = data_frame['raw_incentive_apr']
    y_col = data_frame['market_eth_tvl']
    fig = px.scatter(data_frame, x=x_col, y=y_col)

    fig.show() 


# 3. market eth tvl and raw incentive apr graphed against time with appropriate scales 
def apr_and_tvl_against_time(data_frame): 
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    primary_y_col = 'market_eth_tvl'
    secondary_y_col = 'raw_incentive_apr'

    fig.add_trace(
    go.Scatter(x=data_frame.index, y=data_frame[primary_y_col], name=primary_y_col),
    secondary_y=False,
    )

    fig.add_trace(
    go.Scatter(x=data_frame.index, y=data_frame[secondary_y_col], name=secondary_y_col),
    secondary_y=True,
    )

    # Set x-axis title
    fig.update_xaxes(title_text="time stamp")

    # Set y-axes titles
    fig.update_yaxes(title_text=f"<b>{primary_y_col}</b>", secondary_y=False)
    fig.update_yaxes(title_text=f"<b>{secondary_y_col}</b>", secondary_y=True)

    fig.update_layout(title=f'{primary_y_col} and {secondary_y_col} over time')
    fig.show()



# 4. benchmark elasticities for asset pairs 
def calculate_elasticity(data_frame): 
    # Set price as APR measurement and smoothen it
    data_frame['cur_naive_apr'] = data_frame[['raw_base_apr', 'raw_fee_apr', 'raw_incentive_apr', 'raw_price_apr']].sum(axis=1)
    data_frame['rolling_cur_naive_apr'] = data_frame['cur_naive_apr'].rolling(7).mean()

    # Price shifted back 30 days. This will be our price_1
    data_frame['prev_rolling_cur_naive_apr'] = data_frame['rolling_cur_naive_apr'].shift(-30)

    # Set supply (liquidity) for time delay
    data_frame['prev_token_supply'] = data_frame['lp_token_total_supply'].shift(-30)

    # Set variables for elasticity formula
    quantity_2 = data_frame['lp_token_total_supply']
    quantity_1 = data_frame['prev_token_supply']
    price_2 = data_frame['rolling_cur_naive_apr']
    price_1 = data_frame['prev_rolling_cur_naive_apr']

    # Calculate elasticity
    percent_change_in_supply = (quantity_2 - quantity_1) / ((quantity_2 + quantity_1) / 2) * 100
    percent_change_in_price = (price_2 - price_1) / ((price_2 + price_1) / 2) * 100
    data_frame['elasticity'] = percent_change_in_supply / percent_change_in_price

    return data_frame

# 5. show elasticity graphs 
def plot_elasticity(data_frame): 
    fig = px.line(data_frame['elasticity'])
    fig.show() 


# 6. market eth tvl against rolling cur apr 
def tvl_vs_raw_base_apr(data_frame):
    fig = px.scatter(data_frame, x='market_eth_tvl', y='rolling_cur_naive_apr')
    fig.show() 


# 7. read parquet files   
def read_parquet_files():

    add_lp = pd.read_parquet(ROOT_DATA_DIR / "stETH_ETH_add_lp.parquet")
    remove_lp = pd.read_parquet(ROOT_DATA_DIR / "stETH_ETH_remove_lp.parquet")
    lp_transfers = pd.read_parquet(ROOT_DATA_DIR / "stETH_ETH_lp_transfers.parquet")
    stETH_ETH_incentive_rewards_df = pd.read_parquet(ROOT_DATA_DIR / 'raw_pool_data/curve_stETH_ETH/extra_rewards_df.parquet')

    return add_lp, remove_lp, lp_transfers, stETH_ETH_incentive_rewards_df


# 8. plot reward rates from parquet files (only includes stETH_ETH data)
def plot_reward_rate(stETH_ETH_incentive_rewards_df):
    fig = px.line(stETH_ETH_incentive_rewards_df['reward_rate'])
    fig.show() 

def plot_reward_rate_eth(stETH_ETH_incentive_rewards_df):
    fig = px.line(stETH_ETH_incentive_rewards_df['reward_rate_eth'])
    fig.show() 

# 9. create transfer df that takes in both add_lp and withdraw_lp 
def combine_liquidity():
    lp_transfers = pd.read_parquet(ROOT_DATA_DIR / "stETH_ETH_lp_transfers.parquet")
    add_liquidity_transfers = lp_transfers[lp_transfers["from"] == NULL_ADDRESS]
    withdraw_liquidity_transfers = lp_transfers[lp_transfers["to"] == NULL_ADDRESS]
    withdraw_liquidity_transfers['value'] = withdraw_liquidity_transfers['value']* -1
    warnings.filterwarnings('ignore')
    add_liquidity_transfers['user'] = add_liquidity_transfers['to']
    withdraw_liquidity_transfers['user'] = withdraw_liquidity_transfers['from']

    transfer_df = pd.concat([add_liquidity_transfers, withdraw_liquidity_transfers])
    return transfer_df


# 10. finding users who first added and first removed 
def users_first_add_and_remove(): 
    transfer_df = combine_liquidity()
    # finding those who withdrew before adding 
    users_first_add = transfer_df[transfer_df['value'] > 0].groupby('user')[['timestamp']].min()
    users_first_add.columns = ['date_added']
    users_first_remove = transfer_df[transfer_df['value'] < 0].groupby('user')[['timestamp']].min()
    users_first_remove.columns = ['date_removed']
    users_df = users_first_add.join(users_first_remove, how='outer')
    users_df['date_removed'] = users_df['date_removed'].fillna(pd.to_datetime('2050-01-01'))
   
    users_who_never_added = users_df[users_df['date_added'].isna()].index
    users_who_removed_before_they_added = users_df[users_df['date_removed'] < users_df['date_added']].index
    print("Users who never added liquidity: {}\nUsers who removed liquidity before they added: {}"
        .format((len(users_who_never_added)), len(users_who_removed_before_they_added)))
    
    num_total_unique_users = transfer_df['user'].nunique()
    num_total_unique_users
    print("Total number of unique users: {}".format(num_total_unique_users))

    # this user never added liquidity and only withdrew 
    transfer_df[transfer_df['user'] == users_who_never_added[0]][['from', 'to', 'value']]

    # this person withdrew 20 eth before adding, then added 20 later on
    transfer_df[transfer_df['user'] == users_who_removed_before_they_added[0]][['from', 'to', 'value']]


# 11. whales 
# you can change the y_column in line 204 to simply "reward_rate" if you want the reward rate 
# in terms of LDO instead of eth, which is the default 
def whale_analysis():
    add_lp, remove_lp, lp_transfers, stETH_ETH_incentive_rewards_df = read_parquet_files()
    transfer_df = combine_liquidity()
    transfer_df.sort_index(inplace=True)
    transfer_df['cumsol_col'] = transfer_df.groupby(['user'])['value'].cumsum() 
    whale_df = transfer_df.loc[transfer_df['cumsol_col'] > 50000]
    num_unique_whales = whale_df.groupby(['user']) 
    len(num_unique_whales.groups)

    # cumsol_col sorted largest to smallest 
    transfer_df.groupby('user').max().sort_values('cumsol_col')
    whales_reward_time = transfer_df.groupby('user').max().sort_values('cumsol_col')

    # defining which user is the largest whale
    largest_whale = transfer_df[transfer_df['user'] == '0x43DfFbF34C06EAf9Cd1F9B4c6848b0F1891434b3']
    largest_whale
    # exclude zappers 
    zappers = transfer_df[(transfer_df['to'] == ZAPPER_ADDRESS) | (transfer_df['from'] == ZAPPER_ADDRESS)]
    zappers['user'] = zappers['to']
    # filter out rows matching zapper address 
    transfer_df_filtered = transfer_df[~transfer_df.isin(zappers.to_dict('list')).all(1)]

    # creating cumsol col in filtered transfer df 
    transfer_df_filtered.sort_index(inplace=True)
    transfer_df_filtered['cumsol_col'] = transfer_df_filtered.groupby(['user'])['value'].cumsum()

    # first get balances after 2022
    transactions_after_2022 = transfer_df_filtered[transfer_df_filtered['timestamp'] > '2022-01-01']
    # then select the top 21 whales
    top_21_whales = transactions_after_2022.groupby('user')[['cumsol_col']].max().sort_values('cumsol_col').tail(21)

    for whale in top_21_whales.index:
        print(whale)
        largest_whale = transfer_df_filtered[transfer_df_filtered['user'] == whale]
        largest_whale['date'] = pd.to_datetime(largest_whale['timestamp'].dt.date)

        # to avoid duplicate days, we want the balance over time of 
        largest_whale = largest_whale.groupby('date')[['cumsol_col']].last()
        # resample here reindexes by day and then forward fills the values 
        largest_whale = largest_whale[['cumsol_col']].resample('D').ffill()
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
        go.Bar(x=largest_whale.index, y=largest_whale['cumsol_col'].ffill(), name='balance over time'),
        secondary_y=False,
        )
        fig.add_trace(
        go.Scatter(x=stETH_ETH_incentive_rewards_df.index, y=stETH_ETH_incentive_rewards_df['reward_rate_eth'], name='reward rate (eth)'),
        secondary_y=True, 
        )

        fig.update_xaxes(title_text='timestamp')
        fig.update_yaxes(title_text='balance over time', secondary_y=False)
        fig.update_yaxes(title_text='reward rate (eth)', secondary_y=True)
        fig.show()


# 12. elasticity for LP's who added over 100 eth 
def lp_over_100(stETH_ETH_apr_df):
    add_lp, _, _, _ = read_parquet_files()
    add_lp['date'] = pd.to_datetime(add_lp['timestamp'].dt.date)
    merged_df = pd.merge(add_lp, stETH_ETH_apr_df, left_on='date', right_on='timestamp', how='left') 
    merged_df.set_index('date', inplace=True)

    # sum up tokens provided for each coin and select lp's that provided over 100 
    merged_df['total_tokens'] = merged_df['token_amounts_0'] + merged_df['token_amounts_1']  
    merged_df['cur_naive_apr'] = merged_df[['raw_base_apr', 'raw_fee_apr', 'raw_incentive_apr', 'raw_price_apr']].sum(axis=1)
    merged_df['rolling_cur_naive_apr'] = merged_df['cur_naive_apr'].rolling(7).mean() 
    add_over_100_subgroup = merged_df.loc[merged_df['total_tokens'] > 100]

    subgroup_shift = add_over_100_subgroup.shift(-30, freq='D')
    add_over_100_subgroup = pd.merge_asof(add_over_100_subgroup, subgroup_shift[['rolling_cur_naive_apr', 'token_supply']], left_index=True, right_index=True, direction='forward', suffixes=('', '_prev'))

    # set variables for elasticity formula
    q2 = add_over_100_subgroup['token_supply']
    q1 = add_over_100_subgroup['token_supply_prev']
    p2 = add_over_100_subgroup['rolling_cur_naive_apr']
    p1 = add_over_100_subgroup['rolling_cur_naive_apr_prev']

    # calculate elasticity 
    percent_change_supply = (q2 - q1) / ((q2 + q1) / 2) * 100 
    percent_change_price = (p2 - p1) / ((p2 + p1) / 2) * 100 
    add_over_100_subgroup['elasticity'] = percent_change_supply / percent_change_price 
    add_over_100_subgroup['elasticity']
    warnings.filterwarnings('ignore')

    fig = px.line(add_over_100_subgroup['elasticity'].dropna())
    fig.show()


# 13. number of transations that top 21 whales took part in (both add and withdraw liquidity behaviors)
def num_transactions():
    transfer_df = combine_liquidity()
    lp_transfers = pd.read_parquet(ROOT_DATA_DIR / "stETH_ETH_lp_transfers.parquet")
    add_liquidity_transfers = lp_transfers[lp_transfers["from"] == NULL_ADDRESS]
    withdraw_liquidity_transfers = lp_transfers[lp_transfers["to"] == NULL_ADDRESS]
    added = add_liquidity_transfers[add_liquidity_transfers['to'] == '0x43DfFbF34C06EAf9Cd1F9B4c6848b0F1891434b3']
    withdrew = withdraw_liquidity_transfers[withdraw_liquidity_transfers['from'] == '0x43DfFbF34C06EAf9Cd1F9B4c6848b0F1891434b3']
    num_transactions = len(added) + len(withdrew) 
    transfer_df['cumsol_col'] = transfer_df.groupby(['user'])['value'].cumsum()

    top_21_whales  = transfer_df.groupby('user').max().sort_values('cumsol_col').tail(21)
    for i, whale in enumerate(top_21_whales.index):
        added = add_liquidity_transfers[add_liquidity_transfers['to'] == whale]
        withdrew = withdraw_liquidity_transfers[withdraw_liquidity_transfers['from'] == whale]
        num_transactions = len(added) + len(withdrew) 
        print(i + 1, ":", whale, num_transactions)


# 14. aggregate behavior of multiple whales
def aggregate_whale_behavior(stETH_ETH_incentive_rewards_df, stETH_ETH_apr_df): 
    transfer_df = combine_liquidity()
    incentive_rewards_filtered = stETH_ETH_incentive_rewards_df.loc[stETH_ETH_incentive_rewards_df.index.isin(stETH_ETH_apr_df.index)]
    # get the whales you are interested in. Make sure to change this to exclude the wallets that used the zapper
    transfer_df['cumsol_col'] = transfer_df.groupby(['user'])['value'].cumsum() 
    top_whales = transfer_df.groupby('user')[['cumsol_col']].max().sort_values('cumsol_col').tail(15)

    # get the subset of transactions they are involved in. Only get adds or withdrawal liquidity
    whale_transfers = transfer_df[
        ((transfer_df['to'] == NULL_ADDRESS) | (transfer_df['from'] == NULL_ADDRESS))
        & (transfer_df['user'].isin(top_whales.index))].copy()
    whale_transfers['date'] = pd.to_datetime(whale_transfers['timestamp'].dt.date)
    # now we know the balance at each day, with a transaction
    cumulative_bal_owned_by_whales_sparse = whale_transfers.sort_index()[['value']].cumsum()
    # to make it not sparse we use forward fill
    cumulative_bal_owned_by_whales_dense = cumulative_bal_owned_by_whales_sparse.resample('D').ffill()
    cumulative_bal_owned_by_whales_dense['date'] = pd.to_datetime(cumulative_bal_owned_by_whales_dense.index)
    incentive_rewards_filtered['date'] = pd.to_datetime(incentive_rewards_filtered.index)
    whale_df = pd.merge(incentive_rewards_filtered, cumulative_bal_owned_by_whales_dense, on='date', how='left')
    whale_df.columns = ['lp_token_total_staked', 'reward_rate', 'block', 'reward_rate_eth',       'date', 'lp_tokens_owned_by_whales']
    whale_df

    # graphing lp tokens owned by whales vs reward rate
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=whale_df['date'], y=whale_df['lp_tokens_owned_by_whales'].ffill(), name='lp_tokens_owned_by_whales'),
        secondary_y=False,)
    fig.add_trace(go.Scatter(x=whale_df['date'], y=whale_df['reward_rate_eth'], name='reward_rate_eth'),
        secondary_y=True, 
        )

    fig.update_xaxes(title_text='timestamp')
    fig.update_yaxes(title_text='balance over time', secondary_y=False)
    fig.update_yaxes(title_text='reward rate (eth)', secondary_y=True)
    fig.show() 



# 15. total lp token supply vs reward rate eth 
def total_token_supply_vs_reward_rate(stETH_ETH_apr_df, stETH_ETH_incentive_rewards_df): 

    merged_df = pd.merge_asof(stETH_ETH_apr_df, stETH_ETH_incentive_rewards_df['reward_rate'], left_index=True, right_index=True)
    merged_df_2 = pd.merge_asof(merged_df, stETH_ETH_incentive_rewards_df['reward_rate_eth'], left_index=True, right_index=True)
    # scale appropriately 
    fig = make_subplots(specs=[[{'secondary_y': True}]])
    fig.add_trace(
    go.Bar(x=merged_df_2.index, y=merged_df_2['lp_token_total_supply'], name='lp token total supply'),
        secondary_y=False,
    )

    fig.add_trace(
    go.Scatter(x=merged_df_2.index, y=merged_df_2['reward_rate_eth'].rolling(7).mean(), name='reward rate eth'),
        secondary_y=True,
    )

    fig.update_xaxes(title_text='timestamp')
    fig.update_yaxes(title_text='lp token total supply', secondary_y=False)
    fig.update_yaxes(title_text='reward rate eth', secondary_y=True)
    fig.update_layout(title='LP Token Total Supply vs. Reward Rate ETH')
    fig.show() 



# 16. calculate number of total unique users in a pool 
def num_unique_users():
    transfer_df = combine_liquidity()
    num_total_unique_users = transfer_df['user'].nunique()
    num_total_unique_users
    print("Total number of unique users: {}".format(num_total_unique_users))