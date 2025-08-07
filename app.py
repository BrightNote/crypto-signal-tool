import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Crypto Signal Tool", layout="wide")

st.title("📈 Crypto Signal Dashboard")
st.subheader("Live CoinMarketCap Data + Signals")

# --- Fetch market data from CoinMarketCap ---
@st.cache_data(ttl=600)
def get_market_data():
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
    headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": "296ec5c4-43e0-4a6b-9d69-0b3dab8dd8a5"
    }
    params = {
        "start": "1",
        "limit": "20",
        "convert": "USD"
    }

    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    coins = []
    for coin in data.get("data", []):
        coins.append({
            "id": coin["id"],
            "name": coin["name"],
            "symbol": coin["symbol"],
            "price": coin["quote"]["USD"]["price"],
            "percent_change_24h": coin["quote"]["USD"]["percent_change_24h"]
        })

    return pd.DataFrame(coins)

# --- Add signal logic ---
def add_signal_column(df):
    if "percent_change_24h" not in df.columns:
        df["Signal"] = "N/A"
    else:
        df["Signal"] = df["percent_change_24h"].apply(
            lambda x: "BUY ✅" if x > 3 else ""
        )
    return df

# --- Main logic ---
with st.spinner("Loading market data..."):
    df = get_market_data()

    if df.empty or "name" not in df.columns:
        st.error("⚠️ Failed to load coin data.")
        st.stop()

    df = df[["symbol", "name", "price", "percent_change_24h"]]
    df = add_signal_column(df)

    st.markdown("### Top 20 Coins")
    st.dataframe(
        df.rename(columns={
            "symbol": "Symbol",
            "name": "Name",
            "price": "Price (USD)",
            "percent_change_24h": "24h Change (%)",
            "Signal": "Signal"
        }),
        use_container_width=True
    )
