import os
import streamlit as st
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv
from binance.client import Client

# Import your custom modular trading bot layers
from bot.client import BinanceFuturesTestnetClient, TradingBotError
from bot.orders import submit_order

# 1. Page Configuration & Setup
st.set_page_config(page_title="Binance Futures Bot", layout="wide")
st.title("📈 Binance Futures Trading Dashboard")

load_dotenv()
api_key = os.environ.get("BINANCE_TESTNET_API_KEY")
api_secret = os.environ.get("BINANCE_TESTNET_API_SECRET")

# Initialize client safely (cached so it doesn't rebuild on every rerun)
@st.cache_resource
def get_futures_client(key, secret):
    try:
        return BinanceFuturesTestnetClient(key, secret)
    except TradingBotError as e:
        st.error(f"Failed to connect to Binance Testnet: {e}")
        return None

client = get_futures_client(api_key, api_secret)

# 2. Live Market Overview Panel
st.subheader("Live Market Overview")

def get_current_price(symbol):
    # Using a generic client for public market data ticker fetch
    pub_client = Client(api_key, api_secret, testnet=True)
    ticker = pub_client.get_symbol_ticker(symbol=symbol)
    return float(ticker['price'])

try:
    btc_price = get_current_price("BTCUSDT")
    eth_price = get_current_price("ETHUSDT")
    bnb_price = get_current_price("BNBUSDT")

    col1, col2, col3 = st.columns(3)
    col1.metric("BTC/USDT", f"${btc_price:,.2f}")
    col2.metric("ETH/USDT", f"${eth_price:,.2f}")
    col3.metric("BNB/USDT", f"${bnb_price:,.2f}")
except Exception as e:
    st.warning(f"Could not update live prices: {e}")

# 3. Interactive Plotly Chart Panel
st.subheader("BTC/USDT Price Action (Last 24 Hours)")

@st.cache_data(ttl=60) 
def get_historical_data(symbol, interval, lookback):
    pub_client = Client(api_key, api_secret, testnet=True)
    klines = pub_client.get_historical_klines(symbol, interval, lookback)
    df = pd.DataFrame(klines, columns=[
        'time', 'open', 'high', 'low', 'close', 'volume', 
        'close_time', 'quote_asset_volume', 'number_of_trades', 
        'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
    ])
    df['time'] = pd.to_datetime(df['time'], unit='ms')
    df['close'] = df['close'].astype(float)
    df.set_index('time', inplace=True)
    return df[['close']]

try:
    chart_data = get_historical_data("BTCUSDT", Client.KLINE_INTERVAL_1HOUR, "1 day ago UTC")
    fig = px.line(chart_data, y='close', labels={'close': 'Price (USDT)', 'time': 'Time (UTC)'})
    fig.update_layout(xaxis_title=None, yaxis_title=None, margin=dict(l=0, r=0, t=10, b=0), hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)
except Exception as e:
    st.error(f"Failed to load historical chart: {e}")

st.divider()

# 4. Assignment Core Requirement: Futures Order Execution Panel
st.subheader("🚀 Execute Futures Order (USDT-M)")

if client is None:
    st.warning("Order placement panel disabled. Please verify your environment variables.")
else:
    with st.form(key="order_execution_form", clear_on_submit=False):
        form_col1, form_col2 = st.columns(2)
        
        with form_col1:
            symbol = st.text_input("Symbol", value="BTCUSDT").strip().upper()
            side = st.selectbox("Order Side", options=["BUY", "SELL"])
            order_type = st.selectbox("Order Type", options=["MARKET", "LIMIT"])
            
        with form_col2:
            quantity = st.number_input("Quantity", min_value=0.0, step=0.001, format="%.3f")
            price = st.number_input("Price (Required for LIMIT)", min_value=0.0, step=0.1, value=0.0)
            
        submit_button = st.form_submit_button(label="Submit Order to Testnet")
        
    if submit_button:
        # Front-end pre-validation matching your validators.py rules
        if order_type == "LIMIT" and price <= 0:
            st.error("❌ Validation Error: Price must be greater than 0 for LIMIT orders.")
        elif quantity <= 0:
            st.error("❌ Validation Error: Quantity must be greater than 0.")
        else:
            # Core Requirement: Display Request Summary
            st.write("### 📝 Order Request Summary")
            summary_df = pd.DataFrame({
                "Parameter": ["Symbol", "Side", "Type", "Quantity", "Price"],
                "Value": [symbol, side, order_type, quantity, price if order_type == "LIMIT" else "N/A"]
            })
            st.table(summary_df)
            
            with st.spinner("Transmitting order to Binance Futures Testnet..."):
                order_price = price if order_type == "LIMIT" else None
                
                # Execute utilizing your exact underlying orchestrator logic
                result = submit_order(
                    client=client,
                    symbol=symbol,
                    side=side,
                    order_type=order_type,
                    quantity=quantity,
                    price=order_price
                )
                
            # Core Requirement: Clear success/failure message & execution response tracking
            if result.success:
                st.success("✅ Order Placed Successfully!")
                
                if result.response:
                    st.write("### 📊 Order Response Details")
                    res_col1, res_col2, res_col3, res_col4 = st.columns(4)
                    res_col1.metric("Order ID", result.response.get("orderId"))
                    res_col2.metric("Status", result.response.get("status"))
                    res_col3.metric("Executed Qty", result.response.get("executedQty"))
                    res_col4.metric("Avg Price", result.response.get("avgPrice", "N/A"))
                    
                    with st.expander("View Full API JSON Payload"):
                        st.json(result.response)
            else:
                st.error("❌ Order Failed.")
                st.info(f"Reason: {result.message}")