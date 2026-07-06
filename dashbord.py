from dotenv import load_dotenv
load_dotenv()
import os
import streamlit as st
import pandas as pd
from bot.client import BinanceFuturesTestnetClient

st.set_page_config(page_title="Trading Bot Dashboard", layout="wide")
st.title("📈 Trading Bot Dashboard")

# 1. Load your API keys from the environment variables you set in the terminal
api_key = os.getenv('BINANCE_TESTNET_API_KEY')
api_secret = os.getenv('BINANCE_TESTNET_API_SECRET')

# 2. Initialize your custom bot client
try:
    bot = BinanceFuturesTestnetClient(api_key, api_secret)
    # Your class stores the raw python-binance client in a private variable called _client. 
    # We will expose it here so the dashboard can fetch live market data easily.
    client = bot._client 
except Exception as e:
    st.error(f"Failed to initialize bot: {e}. Did you run the export/env commands in this terminal?")
    st.stop()