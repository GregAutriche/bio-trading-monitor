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
    "^GDAXI": "DAX 40", "^NDX": "NASDAQ 100", "EURUSD=X": "EUR/USD",
    "^STOXX50E": "EuroStoxx 50", "XU100.IS": "BIST 100", "^NSEI": "Nifty 50"
}
STOCKS_ONLY = list(TICKER_NAMES.keys())

# --- 3. DESIGN (MAXIMALER KONTRAST & FARBLOGIK) ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    
    /* Metriken (Indices) - Extrem helles Weiß für Werte */
    [data-testid="stMetricValue"] { 
        font-size: 2.2rem !important; 
        font-weight: 800 !important; 
        color: #E2E8F0 !important; /* Helles Platin-Weiß */
        text-shadow: 0px 0px 10px rgba(255,255,255,0.1);
    }
    [data-testid="stMetricLabel"] { 
        font-size: 1rem !important; 
        color: #94A3B8 !important; 
        text-transform: uppercase; 
    }
    div[data-testid="stMetric"] { 
        background: #161B22; 
        border: 1px solid #30363D; 
        padding: 20px; 
        border-radius: 12px; 
    }

    /* Tabellen-Styling */
    .stTable td { 
        color: #FFFFFF !important; 
        background-color: #11141C !important; 
        border: 1px solid #1F2937 !important;
        font-size: 1.1rem !important;
    }
    .stTable th { 
        background-color: #1E90FF !important; 
        color: #FFFFFF !important; 
        font-weight: bold !important; 
    }

    /* Wetter-Info-Text */
    .update-info { font-size: 1.1rem; color: #1E90FF; font-weight: bold; margin-bottom: 25px; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FUNKTIONEN ---
@st.cache_data(ttl=290)
def get_live_data(symbol):
    try:
        tk = yf.Ticker(symbol)
        df = tk.history(period="5d")
        cp = df["Close"].iloc[-1]
        chg = ((cp / df["Close"].iloc[-2]) - 1) * 100
        return cp, chg
    except: return 0, 0

def get_signal_style(chance, chg):
    """Logik für C/P Farben: Blau (Put), Grau (Neutral), Grün (Call)"""
    if chg > 0.5: return "🟢 CALL", "#00FFA3"  # Grün
    if chg < -0.5: return "🔵 PUT", "#1E90FF"   # Blau
    return "⚪ NEUTRAL", "#8892b0"              # Grau

# --- 5. DASHBOARD LAYOUT ---
st.title("🚀 Bio-Trading Monitor Live PRO")

# 5.1 UPDATE-INFO & WETTER (LANGFRISTIG)
now = datetime.now().strftime('%H:%M:%S')
st.markdown(f'<div class="update-info">🕒 Letztes Update: {now} | Intervall: 5 Min. | Markt-Wetter: ⚖️ Stabil</div>', unsafe_allow_html=True)

# 5.2 INDICES GRID (2 REIHEN)
idx_list = list(INDEX_MAPPING.keys())
rows = [idx_list[:3], idx_list[3:]]

for row in rows:
    cols = st.columns(3)
    for sym, col in zip(row, cols):
        val, chg = get_live_data(sym)
        fmt = "{:.5f}" if "EURUSD" in sym else "{:,.2f}"
        col.metric(INDEX_MAPPING[sym], fmt.format(val), f"{chg:.2f}%")

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
        chance_val = 52.0000 + (vol_rel * 1.5) + (abs(chg) * 0.4)
        
        signal, _ = get_signal_style(chance_val, chg)
        
        top_list.append({
            "Aktie": TICKER_NAMES[t],
            "Signal (C/P)": signal,
            "Chance (%)": chance_val,
            "Kurs (€)": f"{cp:.2f}",
            "Vol-Rel": f"{vol_rel:.2f}x"
        })

# Sortierung & Formatierung
df_top = pd.DataFrame(top_list).sort_values(by="Chance (%)", ascending=False)
df_top["Chance (%)"] = df_top["Chance (%)"].map("{:.4f}".format)
st.table(df_top)

# 5.4 DETAIL-ANALYSE
st.divider()
selected = st.selectbox("🔍 Detail-Analyse & Volumen-Trend:", STOCKS_ONLY, format_func=lambda x: TICKER_NAMES[x])
# ... (Hier folgt der bekannte Chart-Code)
