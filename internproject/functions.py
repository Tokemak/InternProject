import pandas as pd 
import plotly.express as px 
import plotly.io as pio 
from internproject.constants import ROOT_DATA_DIR
import warnings
from pathlib import Path 
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# read into data of all dataframes 
def read_file(file_name):
    ROOT_DIR = Path(__file__).parent.parent
    ROOT_DATA_DIR = ROOT_DIR / "data"     

    file_path = Path(ROOT_DATA_DIR) / file_name 

    df_you_want_to_read_into = pd.read_csv(file_path, index_col=0, parse_dates=True)
    return df_you_want_to_read_into

# market eth tvl vs raw incentive apr graphs 
def market_tvl_vs_apr(data_frame, x_col, y_col): 
    x_col = data_frame['raw_incentive_apr']
    y_col = data_frame['market_eth_tvl']
    fig = px.Scatter(data_frame, x=x_col, y=y_col)

    fig.show() 

# market eth tvl and raw incentive apr graphed against time with appropriate scales 
def apr_and_tvl_against_time(data_frame, primary_y_col, secondary_y_col): 
    fig = make_subplots(specs=[[{"secondary_y": True}]])

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

    return fig

# benchmark elasticities for all asset pairs 
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

def plot_elasticity(data_frame): 
    fig = px.line(data_frame['elasticity'])
    fig.show() 

# market eth tvl against rolling cur apr 
def tvl_vs_raw_base_apr(data_frame):
    fig = px.scatter(data_frame, x='market_eth_tvl', y='rolling_cur_naive_apr')
    fig.show() 

# read parquet files and plot reward rates  
def read_parquet_files(ROOT_DATA_DIR):
    add_lp = pd.read_parquet(ROOT_DATA_DIR / "stETH_ETH_add_lp.parquet")
    remove_lp = pd.read_parquet(ROOT_DATA_DIR / "stETH_ETH_remove_lp.parquet")
    lp_transfers = pd.read_parquet(ROOT_DATA_DIR / "stETH_ETH_lp_transfers.parquet")
    stETH_ETH_incentive_rewards_df = pd.read_parquet(ROOT_DATA_DIR / 'raw_pool_data/curve_stETH_ETH/extra_rewards_df.parquet')

    return add_lp, remove_lp, lp_transfers, stETH_ETH_incentive_rewards_df

zapper_address = '0x271fbE8aB7f1fB262f81C77Ea5303F03DA9d3d6A'
null_address = "0x0000000000000000000000000000000000000000"

def plot_reward_rate(stETH_ETH_incentive_rewards_df):
    fig = px.line(stETH_ETH_incentive_rewards_df['reward_rate'])
    fig.show() 

def plot_reward_rate_eth(stETH_ETH_incentive_rewards_df):
    fig = px.line(stETH_ETH_incentive_rewards_df['reward_rate_eth'])
    fig.show() 

# create transfer df that takes in both add_lp and withdraw_lp 
lp_transfers = pd.read_parquet(ROOT_DATA_DIR / "stETH_ETH_lp_transfers.parquet")
add_liquidity_transfers = lp_transfers[lp_transfers["from"] == null_address]
withdraw_liquidity_transfers = lp_transfers[lp_transfers["to"] == null_address]

def combine_liquidity(add_liquidity_transfers, withdraw_liquidity_transfers):
    withdraw_liquidity_transfers['value'] = withdraw_liquidity_transfers['value']* -1
    warnings.filterwarnings('ignore')
    add_liquidity_transfers['user'] = add_liquidity_transfers['to']
    withdraw_liquidity_transfers['user'] = withdraw_liquidity_transfers['from']

    transfer_df = pd.concat([add_liquidity_transfers, withdraw_liquidity_transfers])
    transfer_df.columns