import streamlit as st
import requests
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime, timedelta

st.set_page_config(page_title="Crypto Signal Tool", layout="wide")

st.title("📈 Crypto Signal Dashboard")
st.subheader("Real-time crypto market snapshot")

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

    # Flatten and build dataframe
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



# --- Signal Logic ---
def add_signal_column(df):
    df['Signal'] = df['percent_change_24h'].apply(
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

with st.spinner("Loading market data..."):
    df = get_market_data()

    if df.empty or "name" not in df.columns:
        st.error("⚠️ Failed to load expected coin data from CoinGecko.")
        st.markdown("### Raw API Response (Top Coins)")
        st.write(df)
        st.stop()

    # Preview first few rows to confirm structure
    st.markdown("### CoinGecko Market Data Preview")
    st.write(df.head())

    # Safe column filtering
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

# Call the API and get full response
response = get_price_history(selected_id)

# Check if the response has valid price data
if response["status"] != 200 or "prices" not in response["json"]:
    st.warning(f"⚠️ CoinGecko returned no price data for {selected_coin}.")
    st.markdown("### Raw API Response")
    st.write(response)
    st.stop()

# Extract price data
price_data = response["json"]["prices"]

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
