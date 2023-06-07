from dataclasses import dataclass
from enum import Enum

from internproject.constants import eth_client

# get these by clicking a pool then "Info" on https://app.aura.finance/


class BalancerPoolType(Enum):
    COMPOSABLE_STABLE_POOL = 1
    META_STABLE_POOL = 2


@dataclass
class BalancerConfig:
    """
    Config addresses for Balancer LP tokens staked for BAL rewards on Aura Finance
    """

    name: str
    balancer_pool_address: str
    aura_reward_pool_address: str
    pool_type: BalancerPoolType

    def __post_init__(self):
        self.balancer_pool_address = eth_client.toChecksumAddress(self.balancer_pool_address)
        self.aura_reward_pool_address = eth_client.toChecksumAddress(self.aura_reward_pool_address)


balancer_wstETH_wETH_config = BalancerConfig(
    name="balancer_wstETH_wETH",
    balancer_pool_address="0x32296969ef14eb0c6d29669c550d4a0449130230",
    aura_reward_pool_address="0xe4683fe8f53da14ca5dac4251eadfb3aa614d528",
    pool_type=BalancerPoolType.META_STABLE_POOL,
)

balancer_wstETH_sfrxETH_rETH_config = BalancerConfig(
    name="balancer_wstETH_sfrxETH_rETH",
    balancer_pool_address="0x8e85e97ed19c0fa13b2549309965291fbbc0048b",
    aura_reward_pool_address="0x60cf485394e83d3879998281faac6a1c3cf218c7",
    pool_type=BalancerPoolType.COMPOSABLE_STABLE_POOL,
)

balancer_wstETH_sfrxETH_rETH_config_2 = BalancerConfig(
    name="balancer_wstETH_sfrxETH_rETH_2",
    balancer_pool_address="0x5aee1e99fe86960377de9f88689616916d5dcabe",
    aura_reward_pool_address="0xd26948e7a0223700e3c3cdea21ca2471abcb8d47",
    pool_type=BalancerPoolType.COMPOSABLE_STABLE_POOL,
)

balancer_wstETH_cbETH_config = BalancerConfig(
    name="balancer_wstETH_cbETH",
    balancer_pool_address="0x4edcb2b46377530bc18bb4d2c7fe46a992c73e10",
    aura_reward_pool_address="0x7d67beb5cf289b015fca7b3fc408860731d826e1",
    pool_type=BalancerPoolType.COMPOSABLE_STABLE_POOL,
)

balancer_wstETH_cbETH_config_2 = BalancerConfig(
    name="balancer_wstETH_cbETH_2",
    balancer_pool_address="0x9c6d47ff73e0f5e51be5fd53236e3f595c5793f2",
    aura_reward_pool_address="0xe35ae62ff773d518172d4b0b1af293704790b670",
    pool_type=BalancerPoolType.META_STABLE_POOL,
)

balancer_rETH_wETH_config = BalancerConfig(
    name="balancer_rETH_wETH",
    balancer_pool_address="0x1e19cf2d73a72ef1332c882f20534b6519be0276",
    aura_reward_pool_address="0x001b78cec62dcfdc660e06a91eb1bc966541d758",
    pool_type=BalancerPoolType.META_STABLE_POOL,
)

balancer_rETH_wETH_config_2 = BalancerConfig(
    name="balancer_rETH_wETH_config_2",
    balancer_pool_address="0xb08885e6026bab4333a80024ec25a1a3e1ff2b8a",
    aura_reward_pool_address="0xb3ca8d6e938354303f60ec8827429b207e7b60a6",
    pool_type=BalancerPoolType.META_STABLE_POOL,
)

BALANCER_COLLECTOR_CONFIGS = [
    balancer_wstETH_wETH_config,
    balancer_wstETH_sfrxETH_rETH_config,
    balancer_wstETH_sfrxETH_rETH_config_2,
    balancer_wstETH_cbETH_config,
    balancer_wstETH_cbETH_config_2,
    balancer_rETH_wETH_config,
    balancer_rETH_wETH_config_2,
]
# these were created after the jan 2022 - jan 2023 window. Fix the window and they ought to work
