# Trading Bot — Binance Futures Testnet (USDT-M)

A small CLI application that places MARKET and LIMIT orders on Binance
Futures Testnet, with structured code, input validation, logging, and
error handling.

## Project Structure

```
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
```

## Setup

1. **Create a Binance Futures Testnet account** at
   https://testnet.binancefuture.com and generate an API key + secret
   from the testnet dashboard.

2. **Clone this repo and install dependencies:**
   ```bash
   git clone <this-repo-url>
   cd trading_bot
   python3 -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set your API credentials as environment variables** (never hard-code
   them in source):
   ```bash
   export BINANCE_TESTNET_API_KEY="your_api_key"
   export BINANCE_TESTNET_API_SECRET="your_api_secret"
   ```
   On Windows (PowerShell):
   ```powershell
   $env:BINANCE_TESTNET_API_KEY="your_api_key"
   $env:BINANCE_TESTNET_API_SECRET="your_api_secret"
   ```

## How to Run

From the project root:

**Market order (BUY):**
```bash
python -m bot.cli --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
```

**Limit order (SELL):**
```bash
python -m bot.cli --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 65000
```

**With verbose (debug) console output:**
```bash
python -m bot.cli --symbol ETHUSDT --side BUY --type MARKET --quantity 0.05 --log-level DEBUG
```
 ## How to Run the UI Dashboard (Bonus Requirement)
**To launch the interactive web interface, run the following command from the project root:**

```bash
streamlit run dashbord.py
```
This will open a local web server (usually at http://localhost:8501) where you can view live market data, interactive price action charts, and submit validated Futures orders directly through the GUI

Every run prints:
- an order request summary
- the order response (`orderId`, `status`, `executedQty`, `avgPrice`)
- a clear `SUCCESS:` or `FAILED:` message

All requests, responses, and errors are also written to
`logs/trading_bot.log` (rotating, up to 5 x 2MB files).

## Assumptions

- Only **MARKET** and **LIMIT** order types are required per the task
  spec; LIMIT orders use `GTC` (Good-Til-Cancelled) as the time-in-force,
  since the task didn't specify one.
- Quantity and price are taken as raw floats; exchange-specific rules
  (lot size / tick size / minimum notional per symbol) are enforced by
  Binance itself and surfaced back to the user as a clear error message
  rather than being independently re-implemented client-side.
- API credentials are read from environment variables rather than CLI
  flags or a config file, to avoid credentials ending up in shell
  history or being accidentally committed.
- The bot targets **USDT-M Futures Testnet** specifically
  (`https://testnet.binancefuture.com`), not spot testnet.

## Error Handling Covered

- Invalid/missing CLI input (bad symbol format, invalid side/type,
  non-numeric or non-positive quantity/price, missing price on LIMIT)
- Binance API rejections (e.g. insufficient testnet balance, invalid
  symbol, filter violations)
- Network/connectivity failures
- Any unexpected exception (caught and logged rather than crashing the CLI)


