import pandas as pd 
from functions import read_file, market_tvl_vs_apr, apr_and_tvl_against_time, calculate_elasticity, plot_elasticity, tvl_vs_raw_base_apr
from functions import read_parquet_files, zapper_address, null_address 

# replace with actual file name
file_name = 'path/to/data/you/want/to/work/with'

x_col = 'raw_incentive_apr'
y_col = 'market_eth_tvl'
primary_y_col = 'market_eth_tvl'
secondary_y_col = 'raw_incentive_apr'

# 1: reading the dataframes 
data_frame = read_file(file_name)

# 2: create scatter plot using dataframe and column names 
market_tvl_vs_apr(data_frame, x_col, y_col)

# 3: create dual axis plot 
fig = apr_and_tvl_against_time(file_name, primary_y_col, secondary_y_col)
fig.show() 

# 4: calculate and plot elasticity
calculate_elasticity(data_frame)
plot_elasticity(calculate_elasticity(data_frame))

# 5: plotting market eth tvl against raw base apr 
tvl_vs_raw_base_apr(data_frame)

# 6: read reward rate data 
add_lp, remove_lp, lp_transfers = read_parquet_files(Path(ROOT_DATA_DIR))