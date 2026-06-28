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

# Hier sind alle Ticker explizit definiert
TICKER_DICTS = {
    "Indizes": {
        "DAX": "^GDAXI", 
        "Nasdaq 100": "^NDX", 
        "S&P 500": "^GSPC"
    },
    "Währungen": {
        "EUR/USD": "EURUSD=X"
    },
    "Osteuropa": {
        "OTP Bank": "OTP.BU", 
        "MOL": "MOL.BU"
    }
}

# ==========================================
# 2. LOGIK
# ==========================================

@st.cache_data(ttl=600) # Cache-Zeit verkürzt für schnellere Aktualisierung
def load_data(ticker):
    # 'yfinance' benötigt bei manchen Ticker-Formaten explizite Zeiträume
    data = yf.download(ticker, period="1y", interval="1d")
    if data.empty: return pd.DataFrame()
    
    # Sicherstellung, dass Close als Float vorliegt
    df = pd.DataFrame(index=data.index)
    
    # Umgang mit MultiIndex bei yfinance (tritt bei manchen Symbolen auf)
    if isinstance(data.columns, pd.MultiIndex):
        df["Close"] = data.iloc[:, 0].astype(float)
    else:
        df["Close"] = data["Close"].astype(float)
    
    # RSI Berechnung
    delta = df["Close"].diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = -delta.where(delta < 0, 0).rolling(14).mean()
    rs = gain / (loss + 1e-9)
    df["RSI"] = (100 - (100 / (1 + rs))).fillna(50.0).astype(float)
    return df

# ==========================================
# 3. SIDEBAR & RENDERING
# ==========================================
cat = st.sidebar.selectbox("Kategorie", list(TICKER_DICTS.keys()))
tick_name = st.sidebar.selectbox("Asset", list(TICKER_DICTS[cat].keys()))
ticker_symbol = TICKER_DICTS[cat][tick_name]

df = load_data(ticker_symbol)

if not df.empty:
    curr = float(df["Close"].iloc[-1])
    prev = float(df["Close"].iloc[-2])
    chg = ((curr - prev) / prev) * 100
    rsi = float(df["RSI"].iloc[-1])
    
    # UI Layout
    c1, c2, c3 = st.columns(3)
    c1.metric(f"Kurs {tick_name}", f"{curr:,.4f}", f"{chg:+.2f}%")
    c2.metric("Fear & Greed (RSI)", f"{rsi:.1f} %")
    c3.info(f"System bereit für {tick_name}")
    
    # Chart
    fig = go.Figure(go.Scatter(x=df.index[-60:], y=df["Close"].iloc[-60:], line=dict(color='#00CC96')))
    fig.update_layout(template="plotly_dark", title=f"Historie: {tick_name}")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error(f"Daten für {tick_name} konnten nicht geladen werden. Bitte prüfen Sie die Internetverbindung.")
