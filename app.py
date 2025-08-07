import streamlit as st
import requests
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime, timedelta

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
        'sparkline': 'true',  # enable sparkline data
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

# --- Plot chart ---
def plot_price_chart(sparkline, coin_name):
    days = 7
    timestamps = [datetime.utcnow() - timedelta(hours=(168 - i)) for i in range(len(sparkline))]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=timestamps,
        y=sparkline,
        mode='lines',
        name='Price'
    ))
    fig.update_layout(
        title=f"{coin_name} - 7 Day Price Trend",
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        height=400
    )
    return fig

# --- Fetch & Process Data ---
with st.spinner("Loading market data..."):
    df = get_market_data()

    # Safely check columns exist before using
    expected_cols = {"id", "symbol", "name", "current_price", "price_change_percentage_24h", "sparkline_in_7d"}
    available_cols = set(df.columns)

    if expected_cols.issubset(available_cols):
        df = df[["id", "symbol", "name", "current_price", "price_change_percentage_24h", "sparkline_in_7d"]]
        df = add_signal_column(df)
    else:
        st.error("⚠️ CoinGecko data returned an unexpected format. Please try again later.")
        st.stop()


# --- Display Table ---
st.markdown("### Top 20 Coins with Signals")
st.dataframe(
    df[["symbol", "name", "current_price", "price_change_percentage_24h", "Signal"]]
    .rename(columns={
        "symbol": "Symbol",
        "name": "Name",
        "current_price": "Price (USD)",
        "price_change_percentage_24h": "24h Change (%)",
        "Signal": "Signal"
    }),
    use_container_width=True
)

# --- Coin selector + chart ---
st.markdown("### 📉 View Price Trend")
selected_coin = st.selectbox("Select a coin to view its 7-day chart:", df["name"])
selected_data = df[df["name"] == selected_coin].iloc[0]
sparkline_data = selected_data["sparkline_in_7d"]["price"]

chart = plot_price_chart(sparkline_data, selected_coin)
st.plotly_chart(chart, use_container_width=True)

# --- Footer ---
st.markdown(f"Last updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
