"""
Time-Weighted Average Price (TWAP) Strategy Implementation
Splits large orders into smaller chunks executed uniformly over time
"""

import time
from datetime import datetime, timedelta
from typing import List, Dict
from logger import setup_logger

class TWAPStrategy:
    """
    TWAP (Time-Weighted Average Price) execution algorithm
    """

    def __init__(self, bot, symbol: str = "BTCUSDT"):
        """
        Initialize TWAP strategy

        Args:
            bot: BinanceFuturesBot instance
            symbol: Trading pair symbol
        """
        self.bot = bot
        self.symbol = symbol
        self.logger = setup_logger("TWAP")
        self.execution_history: List[Dict] = []

    def calculate_order_schedule(self, total_quantity: float, 
                                 time_window_minutes: int,
                                 num_orders: int) -> List[Dict]:
        """
        Calculate order schedule for TWAP execution
        """
        quantity_per_order = total_quantity / num_orders
        interval_seconds = (time_window_minutes * 60) / num_orders
        schedule = []
        current_time = datetime.now()

        for i in range(num_orders):
            execution_time = current_time + timedelta(seconds=i * interval_seconds)
            schedule.append({
                'order_number': i + 1,
                'quantity': quantity_per_order,
                'execution_time': execution_time,
                'wait_seconds': interval_seconds if i > 0 else 0
            })

        self.logger.info(f"TWAP Schedule created: {num_orders} orders of {quantity_per_order:.6f} each")
        return schedule

    def execute(self, side: str, total_quantity: float, 
                time_window_minutes: int, num_orders: int,
                dry_run: bool = False) -> Dict:
        """
        Execute TWAP strategy
        """
        self.logger.info("="*60)
        self.logger.info("TWAP STRATEGY EXECUTION STARTED")
        self.logger.info("="*60)
        self.logger.info(f"Symbol: {self.symbol}")
        self.logger.info(f"Side: {side}")
        self.logger.info(f"Total Quantity: {total_quantity}")
        self.logger.info(f"Time Window: {time_window_minutes} minutes")
        self.logger.info(f"Number of Orders: {num_orders}")
        self.logger.info(f"Dry Run: {dry_run}")

        schedule = self.calculate_order_schedule(total_quantity, time_window_minutes, num_orders)

        successful_orders = 0
        failed_orders = 0
        total_executed_quantity = 0.0
        total_cost = 0.0

        for order_info in schedule:
            try:
                if order_info['wait_seconds'] > 0:
                    self.logger.info(f"Waiting {order_info['wait_seconds']:.1f} seconds...")
                    time.sleep(order_info['wait_seconds'])

                current_price = self.bot.get_current_price(self.symbol)
                self.logger.info(f"Executing Order {order_info['order_number']}/{num_orders}: {order_info['quantity']:.6f} {self.symbol} @ ~{current_price}")

                if not dry_run:
                    order = self.bot.place_market_order(self.symbol, side, order_info['quantity'])
                    if order:
                        executed_qty = float(order.get('executedQty', 0))
                        avg_price = float(order.get('avgPrice', current_price))
                        total_executed_quantity += executed_qty
                        total_cost += executed_qty * avg_price
                        successful_orders += 1
                        self.execution_history.append({
                            'order_id': order['orderId'],
                            'time': datetime.now(),
                            'quantity': executed_qty,
                            'price': avg_price,
                            'side': side
                        })
                        self.logger.info(f"✓ Order executed successfully | Avg Price: {avg_price}")
                    else:
                        failed_orders += 1
                        self.logger.error(f"✗ Order {order_info['order_number']} failed")
                else:
                    total_executed_quantity += order_info['quantity']
                    total_cost += order_info['quantity'] * current_price
                    successful_orders += 1
                    self.logger.info(f"✓ [DRY RUN] Order simulated at {current_price}")

            except Exception as e:
                failed_orders += 1
                self.logger.error(f"✗ Error executing order {order_info['order_number']}: {e}")

        avg_execution_price = total_cost / total_executed_quantity if total_executed_quantity > 0 else 0

        summary = {
            'strategy': 'TWAP',
            'symbol': self.symbol,
            'side': side,
            'total_quantity': total_quantity,
            'executed_quantity': total_executed_quantity,
            'avg_execution_price': avg_execution_price,
            'total_cost': total_cost,
            'successful_orders': successful_orders,
            'failed_orders': failed_orders,
            'execution_time_minutes': time_window_minutes,
            'dry_run': dry_run
        }

        self.logger.info("="*60)
        self.logger.info("TWAP STRATEGY EXECUTION COMPLETED")
        self.logger.info("="*60)
        self.logger.info(f"Successful Orders: {successful_orders}/{num_orders}")
        self.logger.info(f"Failed Orders: {failed_orders}")
        self.logger.info(f"Total Executed Quantity: {total_executed_quantity:.6f}")
        self.logger.info(f"Average Execution Price: {avg_execution_price:.2f}")
        self.logger.info(f"Total Cost: {total_cost:.2f} USDT")

        return summary

    def get_execution_history(self) -> List[Dict]:
        return self.execution_history

    def print_summary(self, summary: Dict):
        print("\n" + "="*60)
        print("TWAP EXECUTION SUMMARY")
        print("="*60)
        print(f"Strategy:              {summary['strategy']}")
        print(f"Symbol:                {summary['symbol']}")
        print(f"Side:                  {summary['side']}")
        print(f"Target Quantity:       {summary['total_quantity']:.6f}")
        print(f"Executed Quantity:     {summary['executed_quantity']:.6f}")
        print(f"Average Price:         {summary['avg_execution_price']:.2f}")
        print(f"Total Cost:            {summary['total_cost']:.2f} USDT")
        print(f"Successful Orders:     {summary['successful_orders']}")
        print(f"Failed Orders:         {summary['failed_orders']}")
        print(f"Execution Time:        {summary['execution_time_minutes']} minutes")
        print(f"Dry Run:               {summary['dry_run']}")
        print("="*60 + "\n")
