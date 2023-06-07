from internproject.constants import eth_client

from dataclasses import dataclass

@dataclass
class CurveCollectorConfig:
    """
    Predefine the constants to build

    CurveStableSwapCollector
    BaseRewardPoolRewardCollector
    ExtraRewardPoolRewardCollector

    """

    name: str
    curve_pool_address: str
    convex_base_reward_pool_address: str
    convex_extra_reward_pool_address: str | None


# Curve StableSwap pool addresses
stETH_ETH_StableSwap_address = eth_client.toChecksumAddress("0xdc24316b9ae028f1497c275eb9192a3ea0f67022")
frxETH_ETH_StableSwap_address = eth_client.toChecksumAddress("0xa1f8a6807c402e4a15ef4eba36528a3fed24e577")
rocket_rETH_wstETH_StableSwap_address = eth_client.toChecksumAddress("0x447ddd4960d9fdbf6af9a790560d0af76795cb08")
starFi_rETH_ETH_StableSwap_address = eth_client.toChecksumAddress("0xf9440930043eb3997fc70e1339dbb11f341de7a8")


# BaseRewardPools
stETH_ETH_base_reward_pool_address = eth_client.toChecksumAddress("0x0A760466E1B4621579a82a39CB56Dda2F4E70f03")
frxETH_ETH_base_reward_pool_address = eth_client.toChecksumAddress("0xbD5445402B0a287cbC77cb67B2a52e2FC635dce4")
rocket_rETH_wstETH_base_reward_pool_address = eth_client.toChecksumAddress("0x5c463069b99AfC9333F4dC2203a9f0c6C7658cCc")
starFi_rETH_ETH_base_reward_pool_address = eth_client.toChecksumAddress("0x61dB6c2321f784c8fAb8d5eF80f58F27C831dCc8")


# ExtraRewardPools

# LDO rewards
stETH_ETH_extra_reward_pool_address = eth_client.toChecksumAddress("0x99ac10631f69c753ddb595d074422a0922d9056b")

# FIS rewards
starFi_rETH_ETH_extra_reward_pool_address = eth_client.toChecksumAddress("0x681A790debE586A64eea055BF0983CD6629d8359")


stETH_ETH_collector_config = CurveCollectorConfig(
    name="curve_stETH_ETH",
    curve_pool_address=stETH_ETH_StableSwap_address,
    convex_base_reward_pool_address=stETH_ETH_base_reward_pool_address,  # CRV / CONVEX
    convex_extra_reward_pool_address=stETH_ETH_extra_reward_pool_address,  # LDO
)

frxETH_ETH_collector_config = CurveCollectorConfig(
    name="curve_frxETH_ETH",
    curve_pool_address=frxETH_ETH_StableSwap_address,
    convex_base_reward_pool_address=frxETH_ETH_base_reward_pool_address,
    convex_extra_reward_pool_address=None,
)

rocket_rETH_wstETH_collector_config = CurveCollectorConfig(
    name="curve_rETH_wstETH",
    curve_pool_address=rocket_rETH_wstETH_StableSwap_address,
    convex_base_reward_pool_address=rocket_rETH_wstETH_base_reward_pool_address,
    convex_extra_reward_pool_address=None,
)

starFi_rETH_ETH_collector_config = CurveCollectorConfig(
    name="curve_starFi_rETH_ETH",
    curve_pool_address=starFi_rETH_ETH_StableSwap_address,
    convex_base_reward_pool_address=starFi_rETH_ETH_base_reward_pool_address,
    convex_extra_reward_pool_address=starFi_rETH_ETH_extra_reward_pool_address,
)

CURVE_STABLE_POOL_CONFIGS = [
    stETH_ETH_collector_config,
    frxETH_ETH_collector_config,
    rocket_rETH_wstETH_collector_config,
    # starFi_rETH_ETH_collector_config, # exclude this because they don't update thier ratio
]

# https://curve.fi/#/ethereum/pools/factory-crypto-91/deposit
# this is cbETH: ETH
# check for other LSD pools to include later.
