from pathlib import Path
from os import environ

from dotenv import load_dotenv
from web3 import Web3

load_dotenv()

ALCHEMY_URL = environ["ALCHEMY_URL"]

ROOT_DIR = Path(__file__).parent.parent
ROOT_DATA_DIR = ROOT_DIR / "data"

eth_client = Web3(Web3.HTTPProvider(ALCHEMY_URL))

