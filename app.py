import streamlit as st
import datetime

st.set_page_config(page_title="Crypto Signal Tool", layout="wide")

st.title("📈 Crypto Signal Dashboard")
st.subheader("Your personalized, real-time signal tool")

st.markdown("This is a placeholder dashboard. Signal data and charts will be added step-by-step.")

# Simulate button to scan signals
if st.button("Run Daily Signal Scan"):
    st.success(f"Scan triggered at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.info("🔍 Signal engine coming in the next step...")
