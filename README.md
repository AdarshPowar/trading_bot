# Trading Bot — Binance Futures Testnet (USDT-M)

A small Python application that places MARKET and LIMIT orders on Binance
Futures Testnet, featuring structured modular code, strict input validation, logging, 
error handling, and a lightweight interactive web dashboard.

## Project Structure

```text
trading_bot/
  bot/
    __init__.py
    client.py            # Binance client wrapper (all API calls live here)
    orders.py            # Order orchestration: validate -> submit -> report
    validators.py        # Input validation / normalization
    logging_config.py    # Logging setup (console + rotating file)
    cli.py               # CLI entry point (argparse)
  dashbord.py            # Streamlit UI Dashboard (Bonus Implementation)
  .env                   # API Credentials (User created)
  logs/
    trading_bot.log      # Generated at runtime (Includes Market & Limit examples)
  README.md
  requirements.txt

##Setup
Create a Binance Futures Testnet account at
https://testnet.binancefuture.com and generate an API key + secret
from the testnet dashboard.

Clone this repo and install dependencies:

Bash
git clone <this-repo-url>
cd trading_bot
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
Set your API credentials: (Never hard-code them in source).
Create a .env file in the root directory of the project and add your testnet keys:

Plaintext
BINANCE_TESTNET_API_KEY="your_api_key_here"
BINANCE_TESTNET_API_SECRET="your_api_secret_here"
(Alternatively, for pure CLI usage, you can export them directly to your terminal session).

##How to Run the UI Dashboard (Bonus Requirement)
To launch the interactive web interface, run the following command from the project root:

Bash
streamlit run dashbord.py
This will open a local web server (usually at http://localhost:8501) where you can view live market data, interactive price action charts, and submit validated Futures orders directly through the GUI.

##How to Run the CLI
The modular backend can be executed directly from the terminal. From the project root:

Market order (BUY):

Bash
python -m bot.cli --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
Limit order (SELL):

Bash
python -m bot.cli --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 65000
With verbose (debug) console output:

Bash
python -m bot.cli --symbol ETHUSDT --side BUY --type MARKET --quantity 0.05 --log-level DEBUG
Every CLI run prints:

an order request summary

the order response (orderId, status, executedQty, avgPrice)

a clear SUCCESS: or FAILED: message

All requests, responses, and errors (from both the CLI and the Web UI) are written to
logs/trading_bot.log (rotating, up to 5 x 2MB files).

Assumptions
Only MARKET and LIMIT order types are required per the task
spec; LIMIT orders use GTC (Good-Til-Cancelled) as the time-in-force,
since the task didn't specify one.

Quantity and price are taken as raw floats; exchange-specific rules
(lot size / tick size / minimum notional per symbol) are enforced by
Binance itself and surfaced back to the user as a clear error message
rather than being independently re-implemented client-side.

API credentials are read from environment variables (via os.environ or python-dotenv) rather than CLI
flags or a config file, to avoid credentials ending up in shell
history or being accidentally committed.

The bot targets USDT-M Futures Testnet specifically
(https://testnet.binancefuture.com), not spot testnet.

##Error Handling Covered
Invalid/missing CLI or UI input (bad symbol format, invalid side/type,
non-numeric or non-positive quantity/price, missing price on LIMIT)

Binance API rejections (e.g. insufficient testnet balance, invalid
symbol, filter violations)

Network/connectivity failures

Any unexpected exception (caught and logged rather than crashing the CLI or UI)


