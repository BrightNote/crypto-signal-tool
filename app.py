import streamlit as st
import requests
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Crypto Signal Tool", layout="wide")

st.title("📈 Crypto Signal Dashboard")
st.subheader("Real-time crypto market snapshot")

# --- CoinGecko API call ---
@st.cache_data(ttl=600)
def get_market_data():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        'vs_currency': 'usd',
        'order': 'market_cap_desc',
        'per_page': 20,
        'page': 1,
        'sparkline': 'false',
        'price_change_percentage': '1h,24h'
    }
    response = requests.get(url, params=params)
    data = response.json()
    return pd.DataFrame(data)

# --- Signal Logic ---
def add_signal_column(df):
    df['Signal'] = df['price_change_percentage_24h'].apply(
        lambda x: "BUY ✅" if x > 3 else ""
    )
    return df

# --- Fetch & Process Data ---
with st.spinner("Loading market data..."):
    df = get_market_data()
    df = df[["symbol", "name", "current_price", "price_change_percentage_24h"]]
    df = add_signal_column(df)

# --- Display Table ---
st.markdown("### Top 20 Coins with Signals")
st.dataframe(
    df.rename(columns={
        "symbol": "Symbol",
        "name": "Name",
        "current_price": "Price (USD)",
        "price_change_percentage_24h": "24h Change (%)",
        "Signal": "Signal"
    }),
    use_container_width=True
)

# --- Footer ---
st.markdown(f"Last updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
