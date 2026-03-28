import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

# --- 1. KONFIGURATION & REFRESH (5 MINUTEN) ---
st.set_page_config(page_title="Bio-Trading Monitor Live PRO", layout="wide")
st_autorefresh(interval=5 * 60 * 1000, key="fscounter")

# --- 2. TICKER-MAPPING ---
TICKER_NAMES = {
    "BAS.DE": "DE BASF", "SAP.DE": "DE SAP", "AIR.DE": "DE Airbus", 
    "DBK.DE": "DE Deutsche Bank", "ADS.DE": "DE Adidas", "BMW.DE": "DE BMW",
    "ALV.DE": "DE Allianz", "VOW3.DE": "DE VW"
}
INDEX_MAPPING = {
    "^GDAXI": "DAX 40", "^NDX": "NASDAQ 100", 
    "^STOXX50E": "EuroStoxx 50", "XU100.IS": "BIST 100", "^NSEI": "Nifty 50",
    "EURUSD=X": "EUR/USD"
}
STOCKS_ONLY = list(TICKER_NAMES.keys())

# --- 3. DESIGN ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    .update-info { font-size: 1rem; color: #1E90FF; margin-bottom: 20px; font-weight: bold; }
    .stTable td { color: #FFFFFF !important; background-color: #11141C !important; border: 1px solid #1F2937 !important; }
    .stTable th { background-color: #1E90FF !important; color: #FFFFFF !important; font-weight: bold !important; }
    div[data-testid="stMetric"] { background: #161B22; border: 1px solid #30363D; padding: 10px; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. ANALYSE-FUNKTION ---
@st.cache_data(ttl=290)
def get_live_data(symbol):
    try:
        tk = yf.Ticker(symbol)
        df = tk.history(period="2d")
        cp = df["Close"].iloc[-1]
        chg = ((cp / df["Close"].iloc[-2]) - 1) * 100
        return cp, chg
    except: return 0, 0

@st.cache_data(ttl=290)
def get_stock_analysis(symbol):
    try:
        tk = yf.Ticker(symbol)
        df = tk.history(period="60d", interval="1d")
        cp = df["Close"].iloc[-1]
        chg = ((cp / df["Close"].iloc[-2]) - 1) * 100
        vol_rel = df["Volume"].iloc[-1] / df["Volume"].tail(20).mean()
        chance = 52.0000 + (vol_rel * 1.5) + (abs(chg) * 0.4)
        return {"cp": cp, "chg": chg, "vol_rel": vol_rel, "df": df, "chance": round(chance, 4)}
    except: return None

# --- 5. DASHBOARD LAYOUT ---
st.title("🚀 Bio-Trading Monitor Live PRO")

# 5.1 UPDATE-INFO
now = datetime.now().strftime('%H:%M:%S')
st.markdown(f'<div class="update-info">🕒 Letztes Update: {now} | Aktualisierung alle: 5 Min. | Status: 🟢 Synchronisiert</div>', unsafe_allow_html=True)

# 5.2 INDICES GRID (VOR DER TABELLE)
# Zeile 1: DAX, NASDAQ, EURUSD
idx1, idx2, idx3 = st.columns(3)
for sym, col in zip(["^GDAXI", "^NDX", "EURUSD=X"], [idx1, idx2, idx3]):
    val, chg = get_live_data(sym)
    fmt = "{:.5f}" if "EURUSD" in sym else "{:,.2f}"
    col.metric(INDEX_MAPPING[sym], fmt.format(val), f"{chg:.2f}%")

# Zeile 2: Eurostoxx, BIST100, Nifty
idx4, idx5, idx6 = st.columns(3)
for sym, col in zip(["^STOXX50E", "XU100.IS", "^NSEI"], [idx4, idx5, idx6]):
    val, chg = get_live_data(sym)
    col.metric(INDEX_MAPPING[sym], f"{val:,.2f}", f"{chg:.2f}%")

st.divider()

# 5.3 TOP MARKT-CHANCEN TABELLE
st.subheader("📊 Top Markt-Chancen (Vola-Analyse)")
top_list = []
for t in STOCKS_ONLY:
    d = get_stock_analysis(t)
    if d:
        top_list.append({
            "Aktie": TICKER_NAMES[t],
            "Signal (C/P)": "🟢 CALL" if d['chg'] >= 0 else "🔵 PUT",
            "Chance (%)": d['chance'],
            "Kurs (€)": f"{d['cp']:.2f}",
            "Vol-Rel": f"{d['vol_rel']:.2f}x"
        })

df_top = pd.DataFrame(top_list).sort_values(by="Chance (%)", ascending=False)
df_top["Chance (%)"] = df_top["Chance (%)"].map("{:.4f}".format)
st.table(df_top)

# 5.4 DETAIL-ANALYSE
st.divider()
selected = st.selectbox("🔍 Detail-Analyse wählen:", STOCKS_ONLY, format_func=lambda x: TICKER_NAMES[x])
det = get_stock_analysis(selected)
if det:
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.7, 0.3])
    fig.add_trace(go.Candlestick(x=det['df'].index, open=det['df']['Open'], high=det['df']['High'], low=det['df']['Low'], close=det['df']['Close'], name="Kurs"), row=1, col=1)
    v_cols = ['#00FFA3' if c >= o else '#FF4B4B' for o, c in zip(det['df']['Open'], det['df']['Close'])]
    fig.add_trace(go.Bar(x=det['df'].index, y=det['df']['Volume'], marker_color=v_cols, name="Volumen"), row=2, col=1)
    fig.update_layout(height=500, template="plotly_dark", xaxis_rangeslider_visible=False, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
