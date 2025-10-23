"""
Configuration file for Binance Futures Trading Bot
Store your API credentials here (DO NOT commit to public repositories)
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Binance Testnet API Credentials

API_KEY = os.getenv("BINANCE_API_KEY", "")
API_SECRET = os.getenv("BINANCE_API_SECRET", "")

# Testnet Configuration
TESTNET = True
TESTNET_URL = "https://testnet.binancefuture.com"

# Trading Configuration
DEFAULT_SYMBOL = "BTCUSDT"
DEFAULT_LEVERAGE = 10
MAX_LEVERAGE = 125

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FILE = "logs/trading_bot.log"
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(funcName)-20s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Order Configuration
VALID_ORDER_TYPES = ["MARKET", "LIMIT", "STOP_MARKET", "STOP_LIMIT", "STOP", "TAKE_PROFIT_MARKET"]
VALID_SIDES = ["BUY", "SELL"]
TIME_IN_FORCE = "GTC"  # Good Till Cancelled

# Risk Management
MAX_POSITION_SIZE = 1000  # Maximum position size in USDT
MIN_ORDER_SIZE = 0.001    # Minimum order quantity

# TWAP Configuration
DEFAULT_TWAP_ORDERS = 10
DEFAULT_TWAP_INTERVAL = 60  # minutes

# Grid Trading Configuration
DEFAULT_NUM_GRIDS = 20
GRID_TYPE = "arithmetic"  # or "geometric"