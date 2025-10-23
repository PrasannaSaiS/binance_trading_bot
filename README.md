# Binance Futures Trading Bot - Testnet

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-success)

A Python-based trading bot for Binance Futures Testnet (USDT-M) supporting Market, Limit, Stop-Market, Stop-Limit orders, TWAP, and Grid Trading strategies.  

## Features

- Place orders: Market, Limit, Stop-Market, Stop-Limit  
- Set leverage from 1x to 125x  
- View account balance and current positions  
- TWAP strategy for time-weighted average price execution  
- Automated grid trading bot for range-bound markets  
- Clean CLI interface with input validation and logging  
- Detailed logs in `logs/trading_bot.log` for analysis  

## Setup & Installation

1. Clone or download this repository.
2. Create and activate a Python 3.10+ virtual environment.
3. Install dependencies:
pip install -r requirements.txt

4. Rename `.env.example` to `.env` and update with your Binance Futures Testnet API keys.
5. Run the bot:
python main.py


## Usage and CLI Menus

The CLI offers an intuitive menu to:

- Place various order types (market, limit, stop-market, stop-limit).
- View open orders, account balance, current position.
- Set leverage.
- Run TWAP or Grid Trading strategies.
- Cancel individual or all open orders.
- Change the trading symbol.

**Example: Place a Market Buy Order**

Select option: 1
Enter side (BUY/SELL): BUY
Enter quantity: 0.01
text

## Notes About Testnet Usage

- This bot works against Binance Futures Testnet only.  
- Testnet funds must be acquired via Binance testnet faucets.  
- Use small quantities within your testnet balance and adjust leverage accordingly.  
- Production usage requires code audit, real API credentials, and extensive risk management.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

Made with ❤️ for the Junior Python Developer internship assignment.