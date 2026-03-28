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
TICKER_NAMES = {"BAS.DE": "DE BASF", "SAP.DE": "DE SAP", "AIR.DE": "DE Airbus", "DBK.DE": "DE Deutsche Bank", "ADS.DE": "DE Adidas", "BMW.DE": "DE BMW", "ALV.DE": "DE Allianz", "VOW3.DE": "DE VW"}
STOCKS_ONLY = list(TICKER_NAMES.keys())

# --- 3. DESIGN (2 ZEILEN LAYOUT & KONTRAST) ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    
    /* Metrik Label (DAX 40 etc.) - HELLWEISS & LESBAR */
    [data-testid="stMetricLabel"] { 
        font-size: 1.1rem !important; 
        color: #F8FAFC !important; /* Maximale Sichtbarkeit */
        font-weight: 700 !important;
    }
    
    /* Metrik Wert (Die große Zahl) */
    [data-testid="stMetricValue"] { 
        font-size: 2.2rem !important; 
        font-weight: 800 !important; 
        color: #FFFFFF !important; 
    }
    
    /* Kachel-Design */
    div[data-testid="stMetric"] { 
        background: #1A1C24; 
        border: 1px solid #334155; 
        padding: 20px !important; 
        border-radius: 12px; 
    }

    .update-info { font-size: 1rem; color: #38BDF8; font-weight: bold; margin-bottom: 25px; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FUNKTIONEN ---
def get_status(chg):
    if chg > 0.4: return "☀️ 🟢" # Call
    if chg < -0.4: return "⛈️ 🔵" # Put
    return "☁️ ⚪" # Neutral

@st.cache_data(ttl=290)
def get_live_data(symbol):
    try:
        tk = yf.Ticker(symbol)
        df = tk.history(period="2d")
        cp = df["Close"].iloc[-1]
        chg = ((cp / df["Close"].iloc[-2]) - 1) * 100
        return cp, chg
    except: return 0, 0

# --- 5. DASHBOARD LAYOUT ---
st.title("🚀 Bio-Trading Monitor Live PRO")

# 5.1 TIMER & UPDATE INFO
now = datetime.now().strftime('%H:%M:%S')
st.markdown(f'<div class="update-info">🕒 Letztes Update: {now} | Intervall: 5 Min.</div>', unsafe_allow_html=True)

# 5.2 INDIZES IN 2 ZEILEN (3 SPALTEN PRO ZEILE)
idx_keys = list(INDEX_MAPPING.keys())

# Zeile 1: DAX 40, NASDAQ 100, EUR/USD
row1_cols = st.columns(3)
for i in range(3):
    sym = idx_keys[i]
    val, chg = get_live_data(sym)
    status = get_status(chg)
    fmt = "{:.5f}" if "EURUSD" in sym else "{:,.0f}" # Kurze Ansicht wie im Screenshot
    row1_cols[i].metric(f"{status} {INDEX_MAPPING[sym]}", fmt.format(val), f"{chg:.2f}%")

# Zeile 2: EuroStoxx 50, BIST 100, Nifty 50
row2_cols = st.columns(3)
for i in range(3):
    sym = idx_keys[i+3]
    val, chg = get_live_data(sym)
    status = get_status(chg)
    row2_cols[i].metric(f"{status} {INDEX_MAPPING[sym]}", f"{val:,.0f}", f"{chg:.2f}%")

st.divider()

# 5.3 TOP MARKT-CHANCEN TABELLE
st.subheader("📊 Top Markt-Chancen (Vola-Analyse)")
top_list = []
for t in STOCKS_ONLY:
    tk = yf.Ticker(t)
    df = tk.history(period="60d")
    if not df.empty:
        cp = df["Close"].iloc[-1]
        chg = ((cp / df["Close"].iloc[-2]) - 1) * 100
        vol_rel = df["Volume"].iloc[-1] / df["Volume"].tail(20).mean()
        chance = 52.0000 + (vol_rel * 1.5) + (abs(chg) * 0.4)
        dot = get_signal_dot(chg)
        
        top_list.append({
            "Aktie": TICKER_NAMES[t],
            "Signal (C/P)": f"{dot} {'CALL' if chg > 0.4 else 'PUT' if chg < -0.4 else 'NEUTRAL'}",
            "Chance (%)": round(chance, 4),
            "Kurs (€)": f"{cp:.2f}",
            "Vol-Rel": f"{vol_rel:.2f}x"
        })

df_top = pd.DataFrame(top_list).sort_values(by="Chance (%)", ascending=False)
df_top["Chance (%)"] = df_top["Chance (%)"].map("{:.4f}".format)
st.table(df_top)
