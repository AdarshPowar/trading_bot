import streamlit as st
import pandas as pd
# Import the client instance directly from your uploaded client.py
from client import client 

st.set_page_config(page_title="Trading Bot Dashboard", layout="wide")
st.title("📈 Trading Bot Dashboard")

# --- SIDEBAR CONTROLS ---
st.sidebar.header("Bot Controls")
symbol = st.sidebar.text_input("Trading Pair", value="BTCUSDT").upper()

if st.sidebar.button("Test Connection"):
    try:
        # Ping the Binance API to verify connection
        client.ping()
        st.sidebar.success("✅ Connected to Binance Demo API successfully!")
    except Exception as e:
        st.sidebar.error(f"❌ Connection failed: {e}")

# --- MAIN DASHBOARD AREA ---
st.subheader("Live Market Data")

try:
    # Fetch current price for the selected symbol
    ticker = client.futures_symbol_ticker(symbol=symbol)
    current_price = float(ticker['price'])
    
    # Fetch account balance
    account_info = client.futures_account_balance()
    usdt_balance = next((item for item in account_info if item["asset"] == "USDT"), None)
    balance_amount = float(usdt_balance['balance']) if usdt_balance else 0.0

    # Display metrics in columns
    col1, col2 = st.columns(2)
    col1.metric(f"Current {symbol} Price", f"${current_price:,.2f}")
    col2.metric("USDT Account Balance", f"${balance_amount:,.2f}")

except Exception as e:
    st.error(f"Error fetching data: {e}. Please ensure your API keys are correct and the testnet flag is set.")

# --- TRADE HISTORY PLACEHOLDER ---
st.subheader("Recent Activity")
st.info("No trades executed yet. Add order execution logic to populate this area.")