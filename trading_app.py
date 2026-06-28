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
    "Indizes": {"DAX": "^GDAXI", "Nasdaq 100": "^NDX", "S&P 500": "^GSPC"},
    "DAX Champions": {
        "SAP": "SAP.DE", "Siemens": "SIE.DE", 
        "Allianz": "ALV.DE", "Deutsche Telekom": "DTE.DE"
    },
    "Währungen": {"EUR/USD": "EURUSD=X"}
}

# ==========================================
# 2. LOGIK
# ==========================================
def get_trading_advice(curr, sma200, rsi, category):
    if curr > sma200 and rsi > 50:
        signal = "Kaufen / Halten"
        horizont = "Mittelfristig" if category != "Währungen" else "Kurzfristig"
    elif curr < sma200:
        signal = "Warten / Verkaufen"
        horizont = "Cash-Position (Seitenlinie)"
    else:
        signal = "Neutral"
        horizont = "Beobachten"
    return signal, horizont

@st.cache_data(ttl=600)
def load_data(ticker):
    data = yf.download(ticker, period="2y")
    df = pd.DataFrame(index=data.index)
    df["Close"] = data.iloc[:, 0].astype(float)
    df["SMA200"] = df["Close"].rolling(window=200).mean()
    delta = df["Close"].diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = -delta.where(delta < 0, 0).rolling(14).mean()
    rs = gain / (loss + 1e-9)
    df["RSI"] = 100 - (100 / (1 + rs))
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
rsi = float(df["RSI"].iloc[-1])
signal, horizont = get_trading_advice(curr, sma200, rsi, cat)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Kurs", f"{curr:,.4f}")
c2.metric("Empfehlung", signal)
c3.metric("Horizont", horizont)
c4.metric("SMA 200", f"{sma200:,.4f}")

fig = go.Figure()
fig.add_trace(go.Scatter(x=df.index[-200:], y=df["Close"].iloc[-200:], name="Kurs"))
fig.add_trace(go.Scatter(x=df.index[-200:], y=df["SMA200"].iloc[-200:], name="SMA 200", line=dict(dash='dash')))
fig.update_layout(template="plotly_dark", title=f"Analyse: {tick_name}")
st.plotly_chart(fig, use_container_width=True)

# Erweiterter Infoblock
with st.expander("ℹ️ Erläuterung der Trading-Logik"):
    st.markdown("""
    * **Kaufen / Halten**: Kurs über SMA 200 und RSI > 50. Der Windschatten-Trend ist intakt.
    * **Warten / Verkaufen (Cash-Position)**: Der Kurs ist unter den SMA 200 gefallen. Sicherheit geht vor: Kapital in Cash wandeln und an der Seitenlinie auf bessere Zeiten warten.
    * **Cash-Postion** Das ist deine „Sicherheits-Zone“. Wenn das Dashboard „Warten/Verkaufen“ anzeigt und als Horizont „Cash-Position“ nennt, bedeutet das: Baue deine Aktien-Positionen ab oder halte sie nicht weiter. Du „parkst“ dein Kapital in Bargeld (auf dem Verrechnungskonto), um nicht im fallenden Markt (unter dem SMA 200) weiter an Wert zu verlieren. Du wartest in Ruhe an der Seitenlinie, bis sich das „Wetter“ wieder bessert.
    * **Haltehorizonte**: 
        * *Mittelfristig*: Für Aktien (Wochen/Monate).
        * *Kurzfristig*: Für volatile Währungspaare (Intraday/Swing).
    """)
