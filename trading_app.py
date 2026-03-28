import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from streamlit_autorefresh import st_autorefresh
from datetime import datetime, timedelta

# --- 1. KONFIGURATION & REFRESH (5 MINUTEN) ---
st.set_page_config(page_title="Bio-Trading Monitor Live PRO", layout="wide")
st_autorefresh(interval=5 * 60 * 1000, key="fscounter")

# --- 2. TICKER-MAPPING ---
INDEX_MAPPING = {
    "^GDAXI": "DAX 40", "^NDX": "NASDAQ 100", "EURUSD=X": "EUR/USD",
    "^STOXX50E": "EuroStoxx 50", "XU100.IS": "BIST 100", "^NSEI": "Nifty 50"
}
TICKER_NAMES = {
    "BAS.DE": "DE BASF", "SAP.DE": "DE SAP", "AIR.DE": "DE Airbus", 
    "DBK.DE": "DE Deutsche Bank", "ADS.DE": "DE Adidas", "BMW.DE": "DE BMW",
    "ALV.DE": "DE Allianz", "VOW3.DE": "DE VW"
}
STOCKS_ONLY = list(TICKER_NAMES.keys())

# --- 3. DESIGN (DUNKELBLAUER HINTERGRUND & KONTRAST) ---
st.markdown("""
    <style>
    /* Haupt-Hintergrund Dunkelblau */
    .stApp { background-color: #0B0E14; color: #FFFFFF; }
    
    /* Metrik-Kacheln (Indices) */
    div[data-testid="stMetric"] { 
        background: #161B22; 
        border: 1px solid #1F2937; 
        padding: 20px !important; 
        border-radius: 12px; 
    }
    [data-testid="stMetricLabel"] { font-size: 1.1rem !important; color: #F8FAFC !important; font-weight: 700 !important; }
    [data-testid="stMetricValue"] { font-size: 2.2rem !important; font-weight: 800 !important; color: #FFFFFF !important; }
    
    /* Tabellen-Optik */
    .stTable td { color: #FFFFFF !important; background-color: #0B0E14 !important; border: 1px solid #1F2937 !important; font-size: 1.1rem !important; }
    .stTable th { background-color: #1E90FF !important; color: #FFFFFF !important; font-weight: 900 !important; }
    
    /* Execution Box */
    .execution-box { background: rgba(30, 144, 255, 0.1); border: 2px solid #1E90FF; padding: 20px; border-radius: 15px; margin-top: 10px; }
    .update-info { font-size: 1rem; color: #38BDF8; font-weight: bold; margin-bottom: 25px; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FUNKTIONEN ---
def get_status_info(chg):
    if chg > 0.4: return "☀️ 🟢"
    if chg < -0.4: return "⛈️ 🔵"
    return "☁️ ⚪"

@st.cache_data(ttl=290)
def get_live_data(symbol):
    try:
        tk = yf.Ticker(symbol)
        df = tk.history(period="5d")
        cp = df["Close"].iloc[-1]
        chg = ((cp / df["Close"].iloc[-2]) - 1) * 100
        return cp, chg
    except: return 0, 0

@st.cache_data(ttl=290)
def get_stock_analysis(symbol):
    try:
        tk = yf.Ticker(symbol)
        df = tk.history(period="60d")
        cp = df["Close"].iloc[-1]
        chg = ((cp / df["Close"].iloc[-2]) - 1) * 100
        vol_rel = df["Volume"].iloc[-1] / df["Volume"].tail(20).mean()
        # ATR für Trading-Hilfe
        df['TR'] = np.maximum(df['High'] - df['Low'], np.maximum(abs(df['High'] - df['Close'].shift(1)), abs(df['Low'] - df['Close'].shift(1))))
        atr = df['TR'].tail(14).mean()
        chance = 52.0000 + (vol_rel * 1.5) + (abs(chg) * 0.4)
        return {"cp": cp, "chg": chg, "vol_rel": vol_rel, "atr": atr, "df": df, "chance": round(chance, 4)}
    except: return None

# --- 5. DASHBOARD LAYOUT ---
st.title("🚀 Bio-Trading Monitor Live PRO")

# 5.1 HEADER INFO
now = datetime.now().strftime('%H:%M:%S')
st.markdown(f'<div class="update-info">🕒 Letztes Update: {now} | Intervall: 5 Min. | Status: Live</div>', unsafe_allow_html=True)

# 5.2 INDIZES IN 2 ZEILEN
idx_keys = list(INDEX_MAPPING.keys())
for i in range(0, 6, 3):
    cols = st.columns(3)
    for j in range(3):
        sym = idx_keys[i+j]
        val, chg = get_live_data(sym)
        status = get_status_info(chg)
        fmt = "{:.5f}" if "EURUSD" in sym else "{:,.0f}"
        cols[j].metric(f"{status} {INDEX_MAPPING[sym]}", fmt.format(val), f"{chg:.2f}%")

st.divider()

# 5.3 TOP MARKT-CHANCEN TABELLE (AKTIE | SIGNAL | CHANCE | KURS | VOL-REL)
st.subheader("📊 Top Markt-Chancen (Vola-Analyse)")
top_list = []
for t in STOCKS_ONLY:
    d = get_stock_analysis(t)
    if d:
        status = get_status_info(d['chg'])
        top_list.append({
            "Aktie": f"{status} {TICKER_NAMES[t]}",
            "Signal (C/P)": "🟢 CALL" if d['chg'] > 0.4 else "🔵 PUT" if d['chg'] < -0.4 else "⚪ NEUTRAL",
            "Chance (%)": d['chance'],
            "Kurs (€)": f"{d['cp']:.2f}",
            "Vol-Rel": f"{d['vol_rel']:.2f}x"
        })

df_top = pd.DataFrame(top_list).sort_values(by="Chance (%)", ascending=False)
df_top["Chance (%)"] = df_top["Chance (%)"].map("{:.4f}".format)
st.table(df_top)

# 5.4 TRADING HILFE & CHART
st.divider()
st.subheader("🔍 Smart-Entry & Execution Support")
selected = st.selectbox("Aktie wählen:", STOCKS_ONLY, format_func=lambda x: TICKER_NAMES[x])
det = get_stock_analysis(selected)

if det:
    direction = 1 if det['chg'] >= 0 else -1
    sl = det['cp'] - (1.5 * det['atr'] * direction)
    tp1 = det['cp'] + (2.0 * det['atr'] * direction)
    
    col_chart, col_exec = st.columns([2, 1])
    
    with col_exec:
        st.markdown('<div class="execution-box">', unsafe_allow_html=True)
        st.write(f"### 🛡️ Setup: {'CALL' if direction == 1 else 'PUT'}")
        risk = st.number_input("Risiko (€):", value=100, step=50)
        pos_size = int(risk / abs(det['cp'] - sl))
        st.write(f"**Stückzahl:** `{pos_size}` Aktien")
        st.write(f"🛑 **SL:** {sl:.2f} € | 🎯 **TP:** {tp1:.2f} €")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_chart:
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.7, 0.3])
        fig.add_trace(go.Candlestick(x=det['df'].index, open=det['df']['Open'], high=det['df']['High'], low=det['df']['Low'], close=det['df']['Close'], name="Kurs"), row=1, col=1)
        fig.add_hline(y=sl, line_dash="dash", line_color="red", row=1, col=1) # Stop-Loss Linie
        fig.add_hline(y=tp1, line_dash="dash", line_color="green", row=1, col=1) # Take-Profit Linie
        v_colors = ['#00FFA3' if c >= o else '#FF4B4B' for o, c in zip(det['df']['Open'], det['df']['Close'])]
        fig.add_trace(go.Bar(x=det['df'].index, y=det['df']['Volume'], marker_color=v_colors, name="Volumen"), row=2, col=1)
        fig.update_layout(height=550, template="plotly_dark", xaxis_rangeslider_visible=False, paper_bgcolor='#0B0E14', plot_bgcolor='#0B0E14')
        st.plotly_chart(fig, use_container_width=True)
