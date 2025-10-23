"""
Binance Futures Trading Bot - Core Implementation
Supports MARKET, LIMIT, STOP_MARKET, STOP_LIMIT orders
"""

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException
from typing import Dict, Optional, List

from config import (
    API_KEY, API_SECRET, TESTNET, TIME_IN_FORCE, 
    DEFAULT_LEVERAGE, MAX_LEVERAGE
)
from logger import setup_logger
from utils import validate_symbol, validate_quantity, validate_price

class BinanceFuturesBot:
    """
    Binance Futures Trading Bot with comprehensive order management
    """
    
    def __init__(self, api_key: str = API_KEY, api_secret: str = API_SECRET, 
                 testnet: bool = TESTNET):
        """
        Initialize the trading bot
        
        Args:
            api_key (str): Binance API key
            api_secret (str): Binance API secret
            testnet (bool): Use testnet environment
        """
        self.logger = setup_logger()
        self.testnet = testnet
        
        try:
            self.client = Client(api_key, api_secret, testnet=testnet)
            self.logger.info(f"✓ Bot initialized successfully (Testnet: {testnet})")
            
            # Test connection
            self._test_connection()
            
        except Exception as e:
            self.logger.critical(f"✗ Failed to initialize bot: {e}")
            raise
    
    def _test_connection(self):
        """Test API connection and permissions"""
        try:
            account = self.client.futures_account()
            balance = float(account['totalWalletBalance'])
            self.logger.info(f"✓ Connection successful | Wallet Balance: {balance} USDT")
        except BinanceAPIException as e:
            self.logger.error(f"✗ API Error: {e}")
            raise
        except Exception as e:
            self.logger.error(f"✗ Connection test failed: {e}")
            raise
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """
        Get current market price for a symbol
        
        Args:
            symbol (str): Trading pair
            
        Returns:
            Optional[float]: Current price or None
        """
        try:
            ticker = self.client.futures_symbol_ticker(symbol=symbol)
            price = float(ticker['price'])
            self.logger.info(f"Current price for {symbol}: {price}")
            return price
        except Exception as e:
            self.logger.error(f"Failed to get price for {symbol}: {e}")
            return None
    
    def set_leverage(self, symbol: str, leverage: int) -> bool:
        """
        Set leverage for a trading pair
        
        Args:
            symbol (str): Trading pair
            leverage (int): Leverage value (1-125)
            
        Returns:
            bool: Success status
        """
        try:
            if leverage < 1 or leverage > MAX_LEVERAGE:
                self.logger.warning(f"Leverage must be between 1 and {MAX_LEVERAGE}")
                return False
            
            response = self.client.futures_change_leverage(
                symbol=symbol,
                leverage=leverage
            )
            self.logger.info(f"✓ Leverage set to {leverage}x for {symbol}")
            return True
            
        except BinanceAPIException as e:
            self.logger.error(f"✗ Failed to set leverage: {e}")
            return False
    
    def place_market_order(self, symbol: str, side: str, quantity: float) -> Optional[Dict]:
        """
        Place a market order
        
        Args:
            symbol (str): Trading pair
            side (str): BUY or SELL
            quantity (float): Order quantity
            
        Returns:
            Optional[Dict]: Order response or None
        """
        try:
            self.logger.info(f"Placing MARKET {side} order: {quantity} {symbol}")
            
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type='MARKET',
                quantity=quantity
            )
            
            self.logger.info(f"✓ Market order executed | Order ID: {order['orderId']}")
            self.logger.debug(f"Order details: {order}")
            
            return order
            
        except BinanceAPIException as e:
            self.logger.error(f"✗ Binance API Error: {e}")
            return None
        except BinanceOrderException as e:
            self.logger.error(f"✗ Order Error: {e}")
            return None
        except Exception as e:
            self.logger.error(f"✗ Unexpected error: {e}")
            return None
    
    def place_limit_order(self, symbol: str, side: str, quantity: float, 
                         price: float) -> Optional[Dict]:
        """
        Place a limit order
        
        Args:
            symbol (str): Trading pair
            side (str): BUY or SELL
            quantity (float): Order quantity
            price (float): Limit price
            
        Returns:
            Optional[Dict]: Order response or None
        """
        try:
            self.logger.info(
                f"Placing LIMIT {side} order: {quantity} {symbol} @ {price}"
            )
            
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type='LIMIT',
                timeInForce=TIME_IN_FORCE,
                quantity=quantity,
                price=price
            )
            
            self.logger.info(f"✓ Limit order placed | Order ID: {order['orderId']}")
            self.logger.debug(f"Order details: {order}")
            
            return order
            
        except BinanceAPIException as e:
            self.logger.error(f"✗ Binance API Error: {e}")
            return None
        except BinanceOrderException as e:
            self.logger.error(f"✗ Order Error: {e}")
            return None
        except Exception as e:
            self.logger.error(f"✗ Unexpected error: {e}")
            return None
    
    def place_stop_market_order(self, symbol: str, side: str, quantity: float,
                               stop_price: float) -> Optional[Dict]:
        """
        Place a stop-market order
        
        Args:
            symbol (str): Trading pair
            side (str): BUY or SELL
            quantity (float): Order quantity
            stop_price (float): Stop trigger price
            
        Returns:
            Optional[Dict]: Order response or None
        """
        try:
            self.logger.info(
                f"Placing STOP_MARKET {side} order: {quantity} {symbol} @ stop {stop_price}"
            )
            
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type='STOP_MARKET',
                quantity=quantity,
                stopPrice=stop_price
            )
            
            self.logger.info(f"✓ Stop-market order placed | Order ID: {order['orderId']}")
            self.logger.debug(f"Order details: {order}")
            
            return order
            
        except BinanceAPIException as e:
            self.logger.error(f"✗ Binance API Error: {e}")
            return None
        except Exception as e:
            self.logger.error(f"✗ Unexpected error: {e}")
            return None
    
    def place_stop_limit_order(self, symbol: str, side: str, quantity: float,
                              price: float, stop_price: float) -> Optional[Dict]:
        """
        Place a stop-limit order
        
        Args:
            symbol (str): Trading pair
            side (str): BUY or SELL
            quantity (float): Order quantity
            price (float): Limit price after stop is triggered
            stop_price (float): Stop trigger price
            
        Returns:
            Optional[Dict]: Order response or None
        """
        try:
            self.logger.info(
                f"Placing STOP_LIMIT {side} order: {quantity} {symbol} "
                f"@ stop {stop_price}, limit {price}"
            )
            
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type='STOP',
                timeInForce=TIME_IN_FORCE,
                quantity=quantity,
                price=price,
                stopPrice=stop_price
            )
            
            self.logger.info(f"✓ Stop-limit order placed | Order ID: {order['orderId']}")
            self.logger.debug(f"Order details: {order}")
            
            return order
            
        except BinanceAPIException as e:
            self.logger.error(f"✗ Binance API Error: {e}")
            return None
        except Exception as e:
            self.logger.error(f"✗ Unexpected error: {e}")
            return None
    
    def get_open_orders(self, symbol: str) -> Optional[List[Dict]]:
        """
        Get all open orders for a symbol
        
        Args:
            symbol (str): Trading pair
            
        Returns:
            Optional[List[Dict]]: List of open orders or None
        """
        try:
            orders = self.client.futures_get_open_orders(symbol=symbol)
            self.logger.info(f"Retrieved {len(orders)} open orders for {symbol}")
            return orders
        except Exception as e:
            self.logger.error(f"Failed to get open orders: {e}")
            return None
    
    def cancel_order(self, symbol: str, order_id: int) -> bool:
        """
        Cancel a specific order
        
        Args:
            symbol (str): Trading pair
            order_id (int): Order ID to cancel
            
        Returns:
            bool: Success status
        """
        try:
            result = self.client.futures_cancel_order(
                symbol=symbol,
                orderId=order_id
            )
            self.logger.info(f"✓ Order {order_id} cancelled successfully")
            return True
        except Exception as e:
            self.logger.error(f"✗ Failed to cancel order {order_id}: {e}")
            return False
    
    def cancel_all_orders(self, symbol: str) -> bool:
        """
        Cancel all open orders for a symbol
        
        Args:
            symbol (str): Trading pair
            
        Returns:
            bool: Success status
        """
        try:
            result = self.client.futures_cancel_all_open_orders(symbol=symbol)
            self.logger.info(f"✓ All orders cancelled for {symbol}")
            return True
        except Exception as e:
            self.logger.error(f"✗ Failed to cancel all orders: {e}")
            return False
    
    def get_account_balance(self) -> Optional[Dict]:
        """
        Get account balance information
        
        Returns:
            Optional[Dict]: Balance information or None
        """
        try:
            account = self.client.futures_account()
            balance_info = {
                'total_wallet_balance': float(account['totalWalletBalance']),
                'total_unrealized_profit': float(account['totalUnrealizedProfit']),
                'available_balance': float(account['availableBalance'])
            }
            self.logger.info(
                f"Account Balance: {balance_info['total_wallet_balance']} USDT"
            )
            return balance_info
        except Exception as e:
            self.logger.error(f"Failed to get account balance: {e}")
            return None
    
    def get_position(self, symbol: str) -> Optional[Dict]:
        """
        Get current position for a symbol
        
        Args:
            symbol (str): Trading pair
            
        Returns:
            Optional[Dict]: Position information or None
        """
        try:
            positions = self.client.futures_position_information(symbol=symbol)
            if positions:
                position = positions[0]
                pos_info = {
                    'symbol': position['symbol'],
                    'position_amount': float(position['positionAmt']),
                    'entry_price': float(position['entryPrice']),
                    'unrealized_profit': float(position['unRealizedProfit']),
                    'leverage': int(position['leverage'])
                }
                self.logger.info(f"Position for {symbol}: {pos_info['position_amount']}")
                return pos_info
            return None
        except Exception as e:
            self.logger.error(f"Failed to get position: {e}")
            return None
    
    def get_order_status(self, symbol: str, order_id: int) -> Optional[Dict]:
        """
        Get status of a specific order
        
        Args:
            symbol (str): Trading pair
            order_id (int): Order ID
            
        Returns:
            Optional[Dict]: Order status or None
        """
        try:
            order = self.client.futures_get_order(symbol=symbol, orderId=order_id)
            self.logger.info(f"Order {order_id} status: {order['status']}")
            return order
        except Exception as e:
            self.logger.error(f"Failed to get order status: {e}")
            return None
