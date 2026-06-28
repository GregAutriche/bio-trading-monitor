import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

# ==========================================
# 1. KONFIGURATION
# ==========================================
st.set_page_config(page_title="Börsen Wetter", layout="wide")
st.title("🌦️ Börsen Wetter & Trading Dashboard")

TICKER_DICTS = {
    "Indizes": {"DAX": "^GDAXI", "Nasdaq 100": "^NDX"},
    "DAX Champions": {
        "SAP": "SAP.DE",
        "Siemens": "SIE.DE",
        "Allianz": "ALV.DE",
        "Deutsche Telekom": "DTE.DE"
    }
}

# ==========================================
# 2. LOGIK MIT SMA 200
# ==========================================
@st.cache_data(ttl=600)
def load_data(ticker):
    data = yf.download(ticker, period="2y")
    df = pd.DataFrame(index=data.index)
    df["Close"] = data.iloc[:, 0].astype(float)
    # SMA 200 berechnen
    df["SMA200"] = df["Close"].rolling(window=200).mean()
    return df

# ==========================================
# 3. UI RENDERING
# ==========================================
cat = st.sidebar.selectbox("Kategorie", list(TICKER_DICTS.keys()))
tick_name = st.sidebar.selectbox("Asset", list(TICKER_DICTS[cat].keys()))
ticker = TICKER_DICTS[cat][tick_name]

df = load_data(ticker)
curr = float(df["Close"].iloc[-1])
sma200 = float(df["SMA200"].iloc[-1])

# Metrik anzeigen
c1, c2 = st.columns(2)
c1.metric("Aktueller Kurs", f"{curr:,.2f}")
c2.metric("SMA 200 (Trend)", f"{sma200:,.2f}")

# Chart mit SMA 200 Linie
fig = go.Figure()
fig.add_trace(go.Scatter(x=df.index[-200:], y=df["Close"].iloc[-200:], name="Kurs", line=dict(color='#00CC96')))
fig.add_trace(go.Scatter(x=df.index[-200:], y=df["SMA200"].iloc[-200:], name="SMA 200", line=dict(color='#FFD700', dash='dash')))

fig.update_layout(template="plotly_dark", title=f"Trend-Analyse: {tick_name}")
st.plotly_chart(fig, use_container_width=True)

# Windschatten-Check
if curr > sma200:
    st.success(f"✅ {tick_name} ist über dem SMA 200: Bullischer Windschatten aktiv.")
else:
    st.warning(f"⚠️ {tick_name} ist unter dem SMA 200: Vorsicht, kein Windschatten-Momentum.")
