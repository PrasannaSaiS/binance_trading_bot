"""
Command-line interface for Binance Futures Trading Bot
Interactive menu system for placing orders and managing positions
"""

import sys
from colorama import Fore, Style, init
from tabulate import tabulate

from trading_bot import BinanceFuturesBot
from utils import (
    validate_symbol, validate_quantity, validate_price,
    validate_order_side, validate_order_type, format_order_response
)
from logger import setup_logger

# Import strategies
try:
    from strategies.twap import TWAPStrategy
    from strategies.grid_trading import GridTradingBot
    STRATEGIES_AVAILABLE = True
except ImportError:
    STRATEGIES_AVAILABLE = False

# Initialize colorama
init(autoreset=True)

class TradingBotCLI:
    """Command-line interface for the trading bot"""
    
    def __init__(self):
        self.logger = setup_logger("CLI")
        self.bot = None
        self.current_symbol = "BTCUSDT"
    
    def print_header(self):
        """Print application header"""
        print("\n" + "="*70)
        print(f"{Fore.CYAN}{Style.BRIGHT}BINANCE FUTURES TRADING BOT - TESTNET")
        print(f"{Style.RESET_ALL}{'='*70}\n")
    
    def print_menu(self):
        """Print main menu"""
        menu_items = [
            ["1", "Place Market Order"],
            ["2", "Place Limit Order"],
            ["3", "Place Stop-Market Order"],
            ["4", "Place Stop-Limit Order"],
            ["5", "View Open Orders"],
            ["6", "View Account Balance"],
            ["7", "View Current Position"],
            ["8", "Cancel Order"],
            ["9", "Cancel All Orders"],
            ["10", "Change Symbol"],
            ["11", "Set Leverage"],
        ]
        
        # Add advanced strategies if available
        if STRATEGIES_AVAILABLE:
            menu_items.extend([
                ["12", "TWAP Strategy"],
                ["13", "Grid Trading Bot"]
            ])
        
        menu_items.append(["0", "Exit"])
        
        print(f"\n{Fore.YELLOW}═══ MAIN MENU ═══{Style.RESET_ALL}")
        print(tabulate(menu_items, headers=["Option", "Action"], tablefmt="simple"))
        print(f"\nCurrent Symbol: {Fore.GREEN}{self.current_symbol}{Style.RESET_ALL}")
    
    def get_input(self, prompt: str, input_type=str, validator=None):
        """
        Get and validate user input
        
        Args:
            prompt (str): Input prompt
            input_type (type): Expected input type
            validator (callable): Validation function
            
        Returns:
            Input value or None if invalid
        """
        while True:
            try:
                value = input(f"{Fore.CYAN}{prompt}{Style.RESET_ALL}")
                
                if value.lower() in ['exit', 'quit', 'q']:
                    return None
                
                # Convert to appropriate type
                if input_type == float:
                    value = float(value)
                elif input_type == int:
                    value = int(value)
                else:
                    value = str(value).strip()
                
                # Validate if validator provided
                if validator:
                    is_valid, error_msg = validator(value)
                    if not is_valid:
                        print(f"{Fore.RED}✗ {error_msg}{Style.RESET_ALL}")
                        continue
                
                return value
                
            except ValueError:
                print(f"{Fore.RED}✗ Invalid input type. Expected {input_type.__name__}{Style.RESET_ALL}")
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}Operation cancelled{Style.RESET_ALL}")
                return None
    
    def place_market_order_menu(self):
        """Interactive menu for market orders"""
        print(f"\n{Fore.YELLOW}═══ MARKET ORDER ═══{Style.RESET_ALL}")
        
        side = self.get_input("Enter side (BUY/SELL): ", str, validate_order_side)
        if not side:
            return
        
        quantity = self.get_input("Enter quantity: ", float, validate_quantity)
        if not quantity:
            return
        
        # Confirmation
        current_price = self.bot.get_current_price(self.current_symbol)
        print(f"\n{Fore.YELLOW}Order Summary:{Style.RESET_ALL}")
        print(f"Symbol: {self.current_symbol}")
        print(f"Side: {side.upper()}")
        print(f"Quantity: {quantity}")
        print(f"Type: MARKET")
        print(f"Estimated Price: ~{current_price}")
        
        confirm = input(f"\n{Fore.CYAN}Confirm order? (yes/no): {Style.RESET_ALL}")
        if confirm.lower() not in ['yes', 'y']:
            print(f"{Fore.YELLOW}Order cancelled{Style.RESET_ALL}")
            return
        
        # Place order
        order = self.bot.place_market_order(self.current_symbol, side.upper(), quantity)
        
        if order:
            print(f"{Fore.GREEN}✓ Order placed successfully!{Style.RESET_ALL}")
            print(format_order_response(order))
        else:
            print(f"{Fore.RED}✗ Failed to place order{Style.RESET_ALL}")
    
    def place_limit_order_menu(self):
        """Interactive menu for limit orders"""
        print(f"\n{Fore.YELLOW}═══ LIMIT ORDER ═══{Style.RESET_ALL}")
        
        side = self.get_input("Enter side (BUY/SELL): ", str, validate_order_side)
        if not side:
            return
        
        quantity = self.get_input("Enter quantity: ", float, validate_quantity)
        if not quantity:
            return
        
        current_price = self.bot.get_current_price(self.current_symbol)
        print(f"Current market price: {current_price}")
        
        price = self.get_input("Enter limit price: ", float, validate_price)
        if not price:
            return
        
        # Confirmation
        print(f"\n{Fore.YELLOW}Order Summary:{Style.RESET_ALL}")
        print(f"Symbol: {self.current_symbol}")
        print(f"Side: {side.upper()}")
        print(f"Quantity: {quantity}")
        print(f"Type: LIMIT")
        print(f"Price: {price}")
        
        confirm = input(f"\n{Fore.CYAN}Confirm order? (yes/no): {Style.RESET_ALL}")
        if confirm.lower() not in ['yes', 'y']:
            print(f"{Fore.YELLOW}Order cancelled{Style.RESET_ALL}")
            return
        
        # Place order
        order = self.bot.place_limit_order(self.current_symbol, side.upper(), quantity, price)
        
        if order:
            print(f"{Fore.GREEN}✓ Order placed successfully!{Style.RESET_ALL}")
            print(format_order_response(order))
        else:
            print(f"{Fore.RED}✗ Failed to place order{Style.RESET_ALL}")
    
    def place_stop_market_order_menu(self):
        """Interactive menu for stop-market orders"""
        print(f"\n{Fore.YELLOW}═══ STOP-MARKET ORDER ═══{Style.RESET_ALL}")
        
        side = self.get_input("Enter side (BUY/SELL): ", str, validate_order_side)
        if not side:
            return
        
        quantity = self.get_input("Enter quantity: ", float, validate_quantity)
        if not quantity:
            return
        
        current_price = self.bot.get_current_price(self.current_symbol)
        print(f"Current market price: {current_price}")
        
        stop_price = self.get_input("Enter stop price: ", float, validate_price)
        if not stop_price:
            return
        
        # Confirmation
        print(f"\n{Fore.YELLOW}Order Summary:{Style.RESET_ALL}")
        print(f"Symbol: {self.current_symbol}")
        print(f"Side: {side.upper()}")
        print(f"Quantity: {quantity}")
        print(f"Type: STOP_MARKET")
        print(f"Stop Price: {stop_price}")
        
        confirm = input(f"\n{Fore.CYAN}Confirm order? (yes/no): {Style.RESET_ALL}")
        if confirm.lower() not in ['yes', 'y']:
            print(f"{Fore.YELLOW}Order cancelled{Style.RESET_ALL}")
            return
        
        # Place order
        order = self.bot.place_stop_market_order(self.current_symbol, side.upper(), quantity, stop_price)
        
        if order:
            print(f"{Fore.GREEN}✓ Order placed successfully!{Style.RESET_ALL}")
            print(format_order_response(order))
        else:
            print(f"{Fore.RED}✗ Failed to place order{Style.RESET_ALL}")
    
    def place_stop_limit_order_menu(self):
        """Interactive menu for stop-limit orders"""
        print(f"\n{Fore.YELLOW}═══ STOP-LIMIT ORDER ═══{Style.RESET_ALL}")
        
        side = self.get_input("Enter side (BUY/SELL): ", str, validate_order_side)
        if not side:
            return
        
        quantity = self.get_input("Enter quantity: ", float, validate_quantity)
        if not quantity:
            return
        
        current_price = self.bot.get_current_price(self.current_symbol)
        print(f"Current market price: {current_price}")
        
        stop_price = self.get_input("Enter stop price: ", float, validate_price)
        if not stop_price:
            return
        
        limit_price = self.get_input("Enter limit price: ", float, validate_price)
        if not limit_price:
            return
        
        # Confirmation
        print(f"\n{Fore.YELLOW}Order Summary:{Style.RESET_ALL}")
        print(f"Symbol: {self.current_symbol}")
        print(f"Side: {side.upper()}")
        print(f"Quantity: {quantity}")
        print(f"Type: STOP_LIMIT")
        print(f"Stop Price: {stop_price}")
        print(f"Limit Price: {limit_price}")
        
        confirm = input(f"\n{Fore.CYAN}Confirm order? (yes/no): {Style.RESET_ALL}")
        if confirm.lower() not in ['yes', 'y']:
            print(f"{Fore.YELLOW}Order cancelled{Style.RESET_ALL}")
            return
        
        # Place order
        order = self.bot.place_stop_limit_order(
            self.current_symbol, side.upper(), quantity, limit_price, stop_price
        )
        
        if order:
            print(f"{Fore.GREEN}✓ Order placed successfully!{Style.RESET_ALL}")
            print(format_order_response(order))
        else:
            print(f"{Fore.RED}✗ Failed to place order{Style.RESET_ALL}")
    
    def view_open_orders(self):
        """Display all open orders"""
        print(f"\n{Fore.YELLOW}═══ OPEN ORDERS ═══{Style.RESET_ALL}")
        
        orders = self.bot.get_open_orders(self.current_symbol)
        
        if not orders:
            print(f"{Fore.YELLOW}No open orders found{Style.RESET_ALL}")
            return
        
        # Format orders for display
        order_data = []
        for order in orders:
            order_data.append([
                order['orderId'],
                order['symbol'],
                order['side'],
                order['type'],
                order['origQty'],
                order.get('price', 'MARKET'),
                order['status']
            ])
        
        print(tabulate(
            order_data,
            headers=['Order ID', 'Symbol', 'Side', 'Type', 'Quantity', 'Price', 'Status'],
            tablefmt='grid'
        ))
    
    def view_account_balance(self):
        """Display account balance"""
        print(f"\n{Fore.YELLOW}═══ ACCOUNT BALANCE ═══{Style.RESET_ALL}")
        
        balance = self.bot.get_account_balance()
        
        if not balance:
            print(f"{Fore.RED}✗ Failed to retrieve balance{Style.RESET_ALL}")
            return
        
        balance_data = [
            ["Total Wallet Balance", f"{balance['total_wallet_balance']:.2f} USDT"],
            ["Available Balance", f"{balance['available_balance']:.2f} USDT"],
            ["Unrealized Profit", f"{balance['total_unrealized_profit']:.2f} USDT"]
        ]
        
        print(tabulate(balance_data, tablefmt='simple'))
    
    def view_position(self):
        """Display current position"""
        print(f"\n{Fore.YELLOW}═══ CURRENT POSITION ═══{Style.RESET_ALL}")
        
        position = self.bot.get_position(self.current_symbol)
        
        if not position or position['position_amount'] == 0:
            print(f"{Fore.YELLOW}No open position for {self.current_symbol}{Style.RESET_ALL}")
            return
        
        position_data = [
            ["Symbol", position['symbol']],
            ["Position Size", position['position_amount']],
            ["Entry Price", position['entry_price']],
            ["Leverage", f"{position['leverage']}x"],
            ["Unrealized Profit", f"{position['unrealized_profit']:.2f} USDT"]
        ]
        
        print(tabulate(position_data, tablefmt='simple'))
    
    def cancel_order_menu(self):
        """Interactive menu for canceling orders"""
        print(f"\n{Fore.YELLOW}═══ CANCEL ORDER ═══{Style.RESET_ALL}")
        
        # Show open orders first
        self.view_open_orders()
        
        order_id = self.get_input("Enter Order ID to cancel: ", int)
        if not order_id:
            return
        
        confirm = input(f"\n{Fore.CYAN}Confirm cancellation? (yes/no): {Style.RESET_ALL}")
        if confirm.lower() not in ['yes', 'y']:
            print(f"{Fore.YELLOW}Cancellation aborted{Style.RESET_ALL}")
            return
        
        success = self.bot.cancel_order(self.current_symbol, order_id)
        
        if success:
            print(f"{Fore.GREEN}✓ Order cancelled successfully{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}✗ Failed to cancel order{Style.RESET_ALL}")
    
    def cancel_all_orders_menu(self):
        """Interactive menu for canceling all orders"""
        print(f"\n{Fore.YELLOW}═══ CANCEL ALL ORDERS ═══{Style.RESET_ALL}")
        
        # Show open orders first
        self.view_open_orders()
        
        confirm = input(
            f"\n{Fore.RED}⚠ Cancel ALL orders for {self.current_symbol}? (yes/no): {Style.RESET_ALL}"
        )
        if confirm.lower() not in ['yes', 'y']:
            print(f"{Fore.YELLOW}Cancellation aborted{Style.RESET_ALL}")
            return
        
        success = self.bot.cancel_all_orders(self.current_symbol)
        
        if success:
            print(f"{Fore.GREEN}✓ All orders cancelled successfully{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}✗ Failed to cancel orders{Style.RESET_ALL}")
    
    def change_symbol_menu(self):
        """Interactive menu for changing trading symbol"""
        print(f"\n{Fore.YELLOW}═══ CHANGE SYMBOL ═══{Style.RESET_ALL}")
        print(f"Current symbol: {self.current_symbol}")
        
        symbol = self.get_input("Enter new symbol (e.g., ETHUSDT): ", str, validate_symbol)
        if not symbol:
            return
        
        # Test if symbol exists
        price = self.bot.get_current_price(symbol.upper())
        if price:
            self.current_symbol = symbol.upper()
            print(f"{Fore.GREEN}✓ Symbol changed to {self.current_symbol}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}✗ Invalid symbol or symbol not available{Style.RESET_ALL}")
    
    def set_leverage_menu(self):
        """Interactive menu for setting leverage"""
        print(f"\n{Fore.YELLOW}═══ SET LEVERAGE ═══{Style.RESET_ALL}")
        
        leverage = self.get_input("Enter leverage (1-125): ", int)
        if not leverage:
            return
        
        success = self.bot.set_leverage(self.current_symbol, leverage)
        
        if success:
            print(f"{Fore.GREEN}✓ Leverage set successfully{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}✗ Failed to set leverage{Style.RESET_ALL}")
    
    def twap_strategy_menu(self):
        """Interactive menu for TWAP strategy"""
        if not STRATEGIES_AVAILABLE:
            print(f"{Fore.RED}✗ Strategies module not available{Style.RESET_ALL}")
            return
        
        print(f"\n{Fore.YELLOW}═══ TWAP STRATEGY ═══{Style.RESET_ALL}")
        
        side = self.get_input("Enter side (BUY/SELL): ", str, validate_order_side)
        if not side:
            return
        
        total_quantity = self.get_input("Enter total quantity: ", float, validate_quantity)
        if not total_quantity:
            return
        
        time_window = self.get_input("Enter time window (minutes): ", int)
        if not time_window or time_window <= 0:
            return
        
        num_orders = self.get_input("Enter number of orders: ", int)
        if not num_orders or num_orders <= 0:
            return
        
        # Confirmation
        print(f"\n{Fore.YELLOW}TWAP Strategy Summary:{Style.RESET_ALL}")
        print(f"Symbol: {self.current_symbol}")
        print(f"Side: {side.upper()}")
        print(f"Total Quantity: {total_quantity}")
        print(f"Time Window: {time_window} minutes")
        print(f"Number of Orders: {num_orders}")
        print(f"Quantity per Order: {total_quantity/num_orders:.6f}")
        
        confirm = input(f"\n{Fore.CYAN}Start TWAP execution? (yes/no): {Style.RESET_ALL}")
        if confirm.lower() not in ['yes', 'y']:
            print(f"{Fore.YELLOW}TWAP cancelled{Style.RESET_ALL}")
            return
        
        # Execute TWAP
        twap = TWAPStrategy(self.bot, self.current_symbol)
        summary = twap.execute(side.upper(), total_quantity, time_window, num_orders)
        twap.print_summary(summary)
    
    def grid_trading_menu(self):
        """Interactive menu for grid trading"""
        if not STRATEGIES_AVAILABLE:
            print(f"{Fore.RED}✗ Strategies module not available{Style.RESET_ALL}")
            return
        
        print(f"\n{Fore.YELLOW}═══ GRID TRADING BOT ═══{Style.RESET_ALL}")
        
        current_price = self.bot.get_current_price(self.current_symbol)
        print(f"Current price: {current_price}")
        
        lower_price = self.get_input("Enter lower price bound: ", float, validate_price)
        if not lower_price:
            return
        
        upper_price = self.get_input("Enter upper price bound: ", float, validate_price)
        if not upper_price:
            return
        
        num_grids = self.get_input("Enter number of grids: ", int)
        if not num_grids or num_grids < 2:
            print(f"{Fore.RED}✗ Minimum 2 grids required{Style.RESET_ALL}")
            return
        
        investment = self.get_input("Enter total investment (USDT): ", float)
        if not investment or investment <= 0:
            return
        
        # Confirmation
        print(f"\n{Fore.YELLOW}Grid Bot Configuration:{Style.RESET_ALL}")
        print(f"Symbol: {self.current_symbol}")
        print(f"Price Range: {lower_price} - {upper_price}")
        print(f"Current Price: {current_price}")
        print(f"Number of Grids: {num_grids}")
        print(f"Investment: {investment} USDT")
        
        confirm = input(f"\n{Fore.CYAN}Start Grid Bot? (yes/no): {Style.RESET_ALL}")
        if confirm.lower() not in ['yes', 'y']:
            print(f"{Fore.YELLOW}Grid Bot cancelled{Style.RESET_ALL}")
            return
        
        # Start grid bot
        grid_bot = GridTradingBot(self.bot)
        result = grid_bot.start(self.current_symbol, lower_price, upper_price, num_grids, investment)
        
        if result.get('success'):
            print(f"{Fore.GREEN}✓ Grid Bot started successfully{Style.RESET_ALL}")
            print(f"Orders Placed: {result['orders_placed']['total_orders']}")
        else:
            print(f"{Fore.RED}✗ Failed to start Grid Bot: {result.get('error')}{Style.RESET_ALL}")
    
    def run(self):
        """Main application loop"""
        try:
            self.print_header()
            
            # Initialize bot
            print(f"{Fore.CYAN}Initializing bot...{Style.RESET_ALL}")
            self.bot = BinanceFuturesBot()
            
            while True:
                try:
                    self.print_menu()
                    
                    choice = input(f"\n{Fore.CYAN}Select option: {Style.RESET_ALL}")
                    
                    if choice == "1":
                        self.place_market_order_menu()
                    elif choice == "2":
                        self.place_limit_order_menu()
                    elif choice == "3":
                        self.place_stop_market_order_menu()
                    elif choice == "4":
                        self.place_stop_limit_order_menu()
                    elif choice == "5":
                        self.view_open_orders()
                    elif choice == "6":
                        self.view_account_balance()
                    elif choice == "7":
                        self.view_position()
                    elif choice == "8":
                        self.cancel_order_menu()
                    elif choice == "9":
                        self.cancel_all_orders_menu()
                    elif choice == "10":
                        self.change_symbol_menu()
                    elif choice == "11":
                        self.set_leverage_menu()
                    elif choice == "12" and STRATEGIES_AVAILABLE:
                        self.twap_strategy_menu()
                    elif choice == "13" and STRATEGIES_AVAILABLE:
                        self.grid_trading_menu()
                    elif choice == "0":
                        print(f"\n{Fore.GREEN}Thank you for using Binance Futures Trading Bot!{Style.RESET_ALL}")
                        break
                    else:
                        print(f"{Fore.RED}✗ Invalid option{Style.RESET_ALL}")
                    
                    input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
                    
                except KeyboardInterrupt:
                    print(f"\n{Fore.YELLOW}Operation interrupted{Style.RESET_ALL}")
                    continue
                
        except Exception as e:
            print(f"{Fore.RED}✗ Fatal error: {e}{Style.RESET_ALL}")
            self.logger.critical(f"Application error: {e}")
            sys.exit(1)

def main():
    """Application entry point"""
    cli = TradingBotCLI()
    cli.run()

if __name__ == "__main__":
    main()
