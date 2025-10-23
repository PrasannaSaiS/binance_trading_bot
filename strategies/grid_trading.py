"""
Grid Trading Strategy Implementation
Automatically places buy and sell orders at predetermined price levels
"""

import time
from typing import List, Dict, Tuple
from logger import setup_logger

class GridTradingBot:
    """
    Grid Trading Bot for automated trading in ranging markets
    """
    
    def __init__(self, bot):
        self.bot = bot
        self.logger = setup_logger("GridBot")
        self.active = False
        self.grid_orders: List[Dict] = []
        self.completed_grids = 0
        self.total_profit = 0.0
    
    def calculate_grid_levels(self, lower_price: float, upper_price: float,
                              num_grids: int, grid_type: str = "arithmetic") -> List[float]:
        if grid_type == "arithmetic":
            step = (upper_price - lower_price) / num_grids
            levels = [lower_price + i * step for i in range(num_grids + 1)]
        else:
            ratio = (upper_price / lower_price) ** (1 / num_grids)
            levels = [lower_price * (ratio ** i) for i in range(num_grids + 1)]
        
        self.logger.info(f"Grid levels calculated: {num_grids} grids from {lower_price} to {upper_price}")
        return levels
    
    def calculate_order_quantities(self, investment_amount: float,
                                   grid_levels: List[float],
                                   current_price: float) -> Tuple[float, float]:
        grids_below = sum(1 for lvl in grid_levels if lvl < current_price)
        grids_above = sum(1 for lvl in grid_levels if lvl > current_price)

        buy_investment = investment_amount * 0.5
        sell_investment = investment_amount * 0.5

        buy_qty_per_grid = buy_investment / (grids_below * current_price) if grids_below else 0
        sell_qty_per_grid = sell_investment / (grids_above * current_price) if grids_above else 0
        
        self.logger.info(f"Buy quantity per grid: {buy_qty_per_grid:.6f}")
        self.logger.info(f"Sell quantity per grid: {sell_qty_per_grid:.6f}")
        
        return buy_qty_per_grid, sell_qty_per_grid
    
    def place_grid_orders(self, symbol: str, grid_levels: List[float],
                          buy_quantity: float, sell_quantity: float,
                          current_price: float) -> Dict:
        buy_orders_placed = 0
        sell_orders_placed = 0
        failed_orders = 0
        
        self.logger.info("Placing grid orders...")
        
        for level in grid_levels:
            try:
                if level < current_price and buy_quantity > 0:
                    order = self.bot.place_limit_order(symbol, "BUY", buy_quantity, level)
                    if order:
                        self.grid_orders.append({'order_id': order['orderId'], 'type': 'BUY', 'price': level, 'quantity': buy_quantity, 'status': 'ACTIVE'})
                        buy_orders_placed += 1
                        self.logger.info(f"✓ Buy order placed at {level:.2f}")
                    else:
                        failed_orders += 1
                
                elif level > current_price and sell_quantity > 0:
                    order = self.bot.place_limit_order(symbol, "SELL", sell_quantity, level)
                    if order:
                        self.grid_orders.append({'order_id': order['orderId'], 'type': 'SELL', 'price': level, 'quantity': sell_quantity, 'status': 'ACTIVE'})
                        sell_orders_placed += 1
                        self.logger.info(f"✓ Sell order placed at {level:.2f}")
                    else:
                        failed_orders += 1
                
                time.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"Error placing order at level {level}: {e}")
                failed_orders += 1
        
        summary = {
            'buy_orders': buy_orders_placed,
            'sell_orders': sell_orders_placed,
            'failed_orders': failed_orders,
            'total_orders': buy_orders_placed + sell_orders_placed
        }
        
        self.logger.info(f"Grid orders placed: {buy_orders_placed} buys, {sell_orders_placed} sells")
        
        return summary
    
    def start(self, symbol: str, lower_price: float, upper_price: float,
              num_grids: int, investment_amount: float,
              grid_type: str = "arithmetic") -> Dict:
        self.logger.info("="*60)
        self.logger.info("GRID TRADING BOT STARTING")
        self.logger.info("="*60)
        
        if lower_price >= upper_price:
            self.logger.error("Lower price must be less than upper price")
            return {'success': False, 'error': 'Invalid price range'}
        
        if num_grids < 2:
            self.logger.error("Number of grids must be at least 2")
            return {'success': False, 'error': 'Invalid grid count'}
        
        current_price = self.bot.get_current_price(symbol)
        
        if not current_price or current_price < lower_price or current_price > upper_price:
            self.logger.error(f"Current price {current_price} is outside grid range")
            return {'success': False, 'error': 'Price outside range'}
        
        self.logger.info(f"Symbol: {symbol}")
        self.logger.info(f"Price Range: {lower_price} - {upper_price}")
        self.logger.info(f"Current Price: {current_price}")
        self.logger.info(f"Number of Grids: {num_grids}")
        self.logger.info(f"Investment: {investment_amount} USDT")
        self.logger.info(f"Grid Type: {grid_type}")
        
        grid_levels = self.calculate_grid_levels(lower_price, upper_price, num_grids, grid_type)
        
        buy_qty, sell_qty = self.calculate_order_quantities(investment_amount, grid_levels, current_price)
        
        order_summary = self.place_grid_orders(symbol, grid_levels, buy_qty, sell_qty, current_price)
        
        self.active = True
        
        config = {
            'success': True,
            'symbol': symbol,
            'lower_price': lower_price,
            'upper_price': upper_price,
            'current_price': current_price,
            'num_grids': num_grids,
            'investment': investment_amount,
            'grid_type': grid_type,
            'buy_quantity': buy_qty,
            'sell_quantity': sell_qty,
            'orders_placed': order_summary
        }
        
        self.logger.info("="*60)
        self.logger.info("GRID TRADING BOT STARTED SUCCESSFULLY")
        self.logger.info("="*60)
        
        return config
    
    def stop(self, symbol: str) -> Dict:
        self.logger.info("Stopping grid trading bot...")
        
        cancelled = self.bot.cancel_all_orders(symbol)
        
        summary = {
            'completed_grids': self.completed_grids,
            'total_profit': self.total_profit,
            'remaining_orders': len(self.grid_orders),
            'orders_cancelled': cancelled
        }
        
        self.active = False
        self.grid_orders.clear()
        
        self.logger.info(f"Grid bot stopped | Completed: {self.completed_grids} grids")
        
        return summary
    
    def get_status(self) -> Dict:
        return {
            'active': self.active,
            'grid_orders': len(self.grid_orders),
            'completed_grids': self.completed_grids,
            'total_profit': self.total_profit
        }
