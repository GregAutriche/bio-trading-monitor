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
    .stApp { background-color: #0B0E14; color: #FFFFFF; }
    div[data-testid="stMetric"] { background: #161B22; border: 1px solid #1F2937; padding: 20px !important; border-radius: 12px; }
    [data-testid="stMetricLabel"] { font-size: 1.1rem !important; color: #F8FAFC !important; font-weight: 700 !important; }
    [data-testid="stMetricValue"] { font-size: 2.2rem !important; font-weight: 800 !important; color: #FFFFFF !important; }
    .stTable td { color: #FFFFFF !important; background-color: #0B0E14 !important; border: 1px solid #1F2937 !important; font-size: 1.1rem !important; }
    .stTable th { background-color: #1E90FF !important; color: #FFFFFF !important; font-weight: 900 !important; }
    .vol-info-box { background: rgba(56, 189, 248, 0.05); border-left: 5px solid #38BDF8; padding: 15px; border-radius: 8px; margin: 10px 0; }
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
        prev_cp = df["Close"].iloc[-2]
        chg = ((cp / prev_cp) - 1) * 100
        
        # Volumens-Kennzahlen
        curr_vol = df["Volume"].iloc[-1]
        prev_vol = df["Volume"].iloc[-2]
        avg_vol = df["Volume"].tail(20).mean()
        vol_rel = curr_vol / avg_vol
        vol_chg = ((curr_vol / prev_vol) - 1) * 100 if prev_vol > 0 else 0
        
        # ATR für Vola-Check
        df['TR'] = np.maximum(df['High'] - df['Low'], np.maximum(abs(df['High'] - df['Close'].shift(1)), abs(df['Low'] - df['Close'].shift(1))))
        atr = df['TR'].tail(14).mean()
        
        chance = 52.0000 + (vol_rel * 1.5) + (abs(chg) * 0.4)
        return {"cp": cp, "chg": chg, "vol": curr_vol, "vol_rel": vol_rel, "vol_chg": vol_chg, "atr": atr, "df": df, "chance": round(chance, 4)}
    except: return None

# --- 5. DASHBOARD LAYOUT ---
st.title("🚀 Bio-Trading Monitor Live PRO")

# 5.1 HEADER INFO
now = datetime.now().strftime('%H:%M:%S')
st.markdown(f'<div class="update-info">🕒 Letztes Update: {now} | Intervall: 5 Min.</div>', unsafe_allow_html=True)

# 5.2 INDIZES GRID
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

# 5.3 TOP MARKT-CHANCEN TABELLE
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

# 5.4 VOLUMENS-ANALYSE & CHART
st.divider()
st.subheader("🔍 Detail-Analyse: Volumen & Markt-Dynamik")
selected = st.selectbox("Aktie wählen:", STOCKS_ONLY, format_func=lambda x: TICKER_NAMES[x])
det = get_stock_analysis(selected)

if det:
    # Neue Volumens-Kennzahlen Zeile
    v1, v2, v3, v4 = st.columns(4)
    with v1: st.metric("VOLUMEN AKTUELL", f"{det['vol']:,.0f}")
    with v2: st.metric("VOL-TREND (REL)", f"{det['vol_rel']:.2f}x", "vs. 20D Ø")
    with v3: st.metric("VOL-VERÄNDERUNG", f"{det['vol_chg']:.1f}%", "vs. Gestern")
    with v4: st.metric("MARKT-VOLA (ATR)", f"{det['atr']:.2f}", "Schwankung")

    # Interpretations-Box
    vol_status = "STARK" if det['vol_rel'] > 1.2 else "NORMAL" if det['vol_rel'] > 0.8 else "SCHWACH"
    st.markdown(f"""
        <div class="vol-info-box">
            🎯 <b>Volumen-Check:</b> Das Handelsinteresse ist aktuell <b>{vol_status}</b>. 
            Eine Volumen-Steigerung von <b>{det['vol_chg']:.1f}%</b> deutet auf {'zunehmendes' if det['vol_chg'] > 0 else 'abnehmendes'} institutionelles Interesse hin.
        </div>
    """, unsafe_allow_html=True)

    # Chart
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.7, 0.3])
    fig.add_trace(go.Candlestick(x=det['df'].index, open=det['df']['Open'], high=det['df']['High'], low=det['df']['Low'], close=det['df']['Close'], name="Kurs"), row=1, col=1)
    
    v_colors = ['#00FFA3' if c >= o else '#FF4B4B' for o, c in zip(det['df']['Open'], det['df']['Close'])]
    fig.add_trace(go.Bar(x=det['df'].index, y=det['df']['Volume'], marker_color=v_colors, name="Volumen"), row=2, col=1)
    
    fig.update_layout(height=550, template="plotly_dark", xaxis_rangeslider_visible=False, paper_bgcolor='#0B0E14', plot_bgcolor='#0B0E14', showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
