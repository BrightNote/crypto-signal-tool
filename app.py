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

    if df.empty or "name" not in df.columns:
        st.error("⚠️ Failed to load expected coin data from CoinGecko.")
        st.stop()

    # Show preview so we can debug structure
    st.markdown("### Raw API Response Preview")
    st.write(df.head())

    # Only use available columns
    safe_cols = [col for col in ["id", "symbol", "name", "current_price", "price_change_percentage_24h"] if col in df.columns]
    df = df[safe_cols]
    df = add_signal_column(df)




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
st.markdown("### 📉 View 7-Day Price Trend")

selected_coin = st.selectbox("Select a coin to view its 7-day price chart:", df["name"])
selected_row = df[df["name"] == selected_coin].iloc[0]
selected_id = selected_row["id"]

@st.cache_data(ttl=600)
def get_price_history(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {
        "vs_currency": "usd",
        "days": 7,
        "interval": "hourly"
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        return None

    data = response.json()
    return data.get("prices", None)  # return None if prices key is missing


# --- Fetch and plot historical data ---
price_data = get_price_history(selected_id)

if not price_data:
    st.warning(f"No historical price data available for {selected_coin}. Showing raw API response for debug:")
    url = f"https://api.coingecko.com/api/v3/coins/{selected_id}/market_chart"
    st.code(f"GET {url}")
    st.stop()

# Parse into DataFrame
price_df = pd.DataFrame(price_data, columns=["timestamp", "price"])
price_df["timestamp"] = pd.to_datetime(price_df["timestamp"], unit="ms")

# Plot with Plotly
import plotly.graph_objs as go
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=price_df["timestamp"],
    y=price_df["price"],
    mode='lines',
    name='Price'
))
fig.update_layout(
    title=f"{selected_coin} - 7 Day Price Chart",
    xaxis_title="Date",
    yaxis_title="Price (USD)",
    height=400
)
st.plotly_chart(fig, use_container_width=True)




# --- Footer ---
st.markdown(f"Last updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
