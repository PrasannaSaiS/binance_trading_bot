"""
Utility functions for input validation and data processing
"""

import re
from typing import Tuple, Optional
from config import VALID_ORDER_TYPES, VALID_SIDES, MIN_ORDER_SIZE

def validate_symbol(symbol: str) -> Tuple[bool, Optional[str]]:
    """
    Validate trading pair symbol format
    
    Args:
        symbol (str): Trading pair (e.g., BTCUSDT)
        
    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    if not symbol:
        return False, "Symbol cannot be empty"
    
    # Check for USDT-M futures format
    if not symbol.endswith("USDT"):
        return False, "Only USDT-M perpetual contracts are supported (e.g., BTCUSDT)"
    
    # Check format (letters + USDT)
    if not re.match(r'^[A-Z]+USDT$', symbol.upper()):
        return False, "Invalid symbol format. Use format like BTCUSDT, ETHUSDT"
    
    return True, None

def validate_quantity(quantity: float, symbol: str = "") -> Tuple[bool, Optional[str]]:
    """
    Validate order quantity
    
    Args:
        quantity (float): Order quantity
        symbol (str): Trading pair for context
        
    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    if quantity <= 0:
        return False, "Quantity must be greater than 0"
    
    if quantity < MIN_ORDER_SIZE:
        return False, f"Quantity must be at least {MIN_ORDER_SIZE}"
    
    return True, None

def validate_price(price: float) -> Tuple[bool, Optional[str]]:
    """
    Validate price value
    
    Args:
        price (float): Price value
        
    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    if price <= 0:
        return False, "Price must be greater than 0"
    
    return True, None

def validate_order_side(side: str) -> Tuple[bool, Optional[str]]:
    """
    Validate order side (BUY/SELL)
    
    Args:
        side (str): Order side
        
    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    side_upper = side.upper()
    if side_upper not in VALID_SIDES:
        return False, f"Side must be one of: {', '.join(VALID_SIDES)}"
    
    return True, None

def validate_order_type(order_type: str) -> Tuple[bool, Optional[str]]:
    """
    Validate order type
    
    Args:
        order_type (str): Order type
        
    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    order_type_upper = order_type.upper()
    if order_type_upper not in VALID_ORDER_TYPES:
        return False, f"Order type must be one of: {', '.join(VALID_ORDER_TYPES)}"
    
    return True, None

def format_order_response(order: dict) -> str:
    """
    Format order response for display
    
    Args:
        order (dict): Order response from Binance API
        
    Returns:
        str: Formatted order details
    """
    if not order:
        return "No order data available"
    
    formatted = "\n" + "="*60 + "\n"
    formatted += "ORDER DETAILS\n"
    formatted += "="*60 + "\n"
    formatted += f"Order ID:        {order.get('orderId', 'N/A')}\n"
    formatted += f"Symbol:          {order.get('symbol', 'N/A')}\n"
    formatted += f"Side:            {order.get('side', 'N/A')}\n"
    formatted += f"Type:            {order.get('type', 'N/A')}\n"
    formatted += f"Quantity:        {order.get('origQty', 'N/A')}\n"
    formatted += f"Price:           {order.get('price', 'MARKET')}\n"
    formatted += f"Status:          {order.get('status', 'N/A')}\n"
    formatted += f"Time in Force:   {order.get('timeInForce', 'N/A')}\n"
    formatted += f"Update Time:     {order.get('updateTime', 'N/A')}\n"
    formatted += "="*60 + "\n"
    
    return formatted

def format_number(num: float, decimals: int = 2) -> str:
    """
    Format number with specified decimal places
    
    Args:
        num (float): Number to format
        decimals (int): Number of decimal places
        
    Returns:
        str: Formatted number
    """
    return f"{num:.{decimals}f}"

def calculate_percentage(value: float, total: float) -> float:
    """
    Calculate percentage
    
    Args:
        value (float): Value
        total (float): Total
        
    Returns:
        float: Percentage
    """
    if total == 0:
        return 0.0
    return (value / total) * 100

def truncate_string(text: str, max_length: int = 50) -> str:
    """
    Truncate string to max length
    
    Args:
        text (str): Text to truncate
        max_length (int): Maximum length
        
    Returns:
        str: Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."
