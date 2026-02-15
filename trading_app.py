import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime

# --- 1. DARK MODE & LAYOUT SETUP ---
st.set_page_config(layout="wide", page_title="Börsen-Wetter Dashboard")

# Erzwingt schwarzen Hintergrund via CSS
st.markdown("""
    <style>
    .main {
        background-color: #000000;
    }
    .stMetric {
        background-color: #111111;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #333333;
    }
    h1, h2, h3, p, span {
        color: #ffffff !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATENABRUF ---
def get_data():
    tickers = {"EURUSD": "EURUSD=X", "STOXX": "^STOXX50E", "SP": "^GSPC"}
    res = {}
    for k, v in tickers.items():
        ticker = yf.Ticker(v)
        df = ticker.history(period="5d")
        if not df.empty:
            res[k] = {"val": df['Close'].iloc[-1], "delta": ((df['Close'].iloc[-1] - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100, "df": df}
    return res

data = get_data()
now = datetime.now()

# --- 3. HEADER (YYMMDD) ---
st.write(f"### {now.strftime('%y%m%d')}")
st.write(f"**{now.strftime('%A, %H:%M')} (Letztes Update)**")
st.divider()

# --- 4. SEKTION 1: EUR/USD (Obere Zeile) ---
if "EURUSD" in data:
    st.subheader("Währungs-Fokus")
    c1, c2, c3 = st.columns([1, 1, 1])
    c1.metric("EUR/USD", f"{data['EURUSD']['val']:.4f}", f"{data['EURUSD']['delta']:.2f}%")
    c2.write("☀️ **Wetter:** Heiter")
    c3.write("🔵 **Action:** Monitoring")

st.divider()

# --- 5. SEKTION 2: INDIZES (Untereinander) ---
st.subheader("Markt-Indizes")

# Zeile: Euro Stoxx
if "STOXX" in data:
    c1, c2, c3 = st.columns([1, 1, 1])
    c1.metric("Euro Stoxx 50", f"{data['STOXX']['val']:.2f}", f"{data['STOXX']['delta']:.2f}%")
    c2.write("☁️ **Wetter:** Bewölkt")
    c3.write("⚪ **Action:** Wait")

st.write("") # Abstandhalter

# Zeile: S&P
if "SP" in data:
    c1, c2, c3 = st.columns([1, 1, 1])
    c1.metric("S&P Index", f"{data['SP']['val']:.2f}", f"{data['SP']['delta']:.2f}%")
    c2.write("☀️ **Wetter:** Sonnig")
    c3.write("🟢 **Action:** Buy")

st.divider()

# --- 6. SEKTION 3: GRAFIK ---
st.subheader("Grafik")
if "SP" in data:
    fig = go.Figure(data=[go.Candlestick(
        x=data["SP"]["df"].index,
        open=data["SP"]["df"]['Open'], high=data["SP"]["df"]['High'],
        low=data["SP"]["df"]['Low'], close=data["SP"]["df"]['Close']
    )])
    fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

# --- 7. SEKTION 4: DETAIL INFO & LEGENDE ---
st.divider()
col_l1, col_l2 = st.columns(2)
with col_l1:
    st.markdown("**Symbol-Legende:**")
    st.markdown("* ☀️ Sonne = Bullisch\n* ☁️ Wolken = Neutral\n* 🌧️ Regen = Bärisch")
with col_l2:
    st.markdown("**System-Info:**")
    st.write("Daten: Yahoo Finance | Hintergrund: Deep Black")
