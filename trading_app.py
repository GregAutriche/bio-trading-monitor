import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

# ==========================================
# 1. KONFIGURATION & TICKER
# ==========================================
st.set_page_config(page_title="Börsen Wetter", layout="wide")
st.title("🌦️ Börsen Wetter & Trading Dashboard")

TICKER_DICTS = {
    "Indizes": {"DAX": "^GDAXI", "Nasdaq 100": "^NDX", "S&P 500": "^GSPC"},
    "Währungen": {"EUR/USD": "EURUSD=X"},
    "Osteuropa": {"OTP Bank": "OTP.BU", "MOL": "MOL.BU"}
}

# ==========================================
# 2. LOGIK: BÖRSENWETTER & INDIKATOREN
# ==========================================
def calculate_metrics(df):
    """Berechnet RSI und Fear & Greed Score."""
    close = df["Close"].squeeze()
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = -delta.where(delta < 0, 0).rolling(14).mean()
    rs = gain / (loss + 1e-9)
    rsi = 100 - (100 / (1 + rs))
    
    # Fear & Greed (Deine 10/90 Regel)
    sma200 = close.rolling(200).mean()
    dist = ((close - sma200) / sma200) * 100
    fg_score = np.clip((dist + 15) / 30 * 100, 0, 100)
    
    return rsi.iloc[-1], fg_score.iloc[-1]

@st.cache_data(ttl=600)
def load_data(ticker):
    data = yf.download(ticker, period="2y")
    df = pd.DataFrame(index=data.index)
    df["Close"] = data.iloc[:, 0].astype(float)
    return df

# ==========================================
# 3. UI RENDERING
# ==========================================
cat = st.sidebar.selectbox("Kategorie", list(TICKER_DICTS.keys()))
tick_name = st.sidebar.selectbox("Asset", list(TICKER_DICTS[cat].keys()))
ticker = TICKER_DICTS[cat][tick_name]

df = load_data(ticker)
rsi, fg_score = calculate_metrics(df)

# BÖRSENWETTER ANZEIGE
curr = float(df["Close"].iloc[-1])
c1, c2, c3 = st.columns(3)

c1.metric("Aktueller Kurs", f"{curr:,.4f}")
c2.metric("Börsenwetter (Fear & Greed)", f"{fg_score:.1f} %")

# Windschatten-Taktik Logik
if fg_score > 90:
    c3.error("🔥 Extrem hoch (Gier) - Vorsicht!")
elif fg_score < 10:
    c3.success("❄️ Extrem tief (Angst) - Chance!")
else:
    c3.info("⚖️ Normalbereich")

# Chart
fig = go.Figure(go.Scatter(x=df.index[-60:], y=df["Close"].iloc[-60:]))
fig.update_layout(template="plotly_dark", title=f"Historie: {tick_name}")
st.plotly_chart(fig, use_container_width=True)
