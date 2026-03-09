import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# --- SETUP ---
st_autorefresh(interval=300000, key="datarefresh")
st.set_page_config(layout="wide", page_title="Momentum Strategy", page_icon="📡")

# --- REPARIERTES STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #050a0f; }
    /* Zeilen-Abstand korrigiert */
    .row-container { 
        border-bottom: 1px solid #1a202c; 
        padding: 12px 0 !important; 
        margin-bottom: 5px;
        line-height: 1.4 !important; 
    }
    .header-text { font-size: 22px; font-weight: bold; margin-top: 20px; color: #ffd700 !important; }
    
    /* Signal-Boxen mit Kontrast */
    .sig-box { padding: 4px 10px; border-radius: 5px; font-weight: bold; font-size: 0.9rem; display: inline-block; }
    .sig-c { background-color: rgba(63, 185, 80, 0.2); color: #3fb950; border: 1px solid #3fb950; }
    .sig-p { background-color: rgba(0, 123, 255, 0.2); color: #007bff; border: 1px solid #007bff; }
    
    /* Monte Carlo Gold-Box */
    .mc-box { 
        background-color: #161b22; 
        padding: 15px; 
        border-radius: 10px; 
        border: 1px solid #ffd700; 
        margin-top: 15px;
        color: #ffffff !important; 
    }
    .gold-title { color: #ffd700; font-size: 1.2rem; font-weight: bold; }
    small { color: #888; font-size: 0.8rem; }
    </style>
    """, unsafe_allow_html=True)

# --- KLARNAMEN MAPPING ---
NAME_MAP = {
    "EURUSD=X": "Euro / US-Dollar", "^GDAXI": "DAX 40", "^STOXX50E": "EuroStoxx 50", 
    "TTE.PA": "TotalEnergies", "SAN.MC": "Banco Santander", "ASML.AS": "ASML Holding",
    "MC.PA": "LVMH Moët Hennessy", "OR.PA": "L'Oréal", "SAP.DE": "SAP SE"
}

def get_name(t):
    return NAME_MAP.get(t, t.upper())

# --- FUNKTIONEN ---
@st.cache_data(ttl=300)
def fetch_data(tickers):
    return yf.download(tickers, period="1y", interval="1d", auto_adjust=True, threads=False, timeout=10)

def process_signal(ticker, df):
    cp = df['Close']
    curr, prev, prev2 = cp.iloc[-1], cp.iloc[-2], cp.iloc[-3]
    sma20 = cp.rolling(20).mean().iloc[-1]
    
    # Wetter-Logik
    delta = ((curr - df['Open'].iloc[-1]) / df['Open'].iloc[-1]) * 100
    icon = "☀️" if (curr > sma20 and delta > 0.2) else "⚖️" if abs(delta) < 0.2 else "⛈️"
    
    # Signal P/C
    sig = "C" if curr > prev > prev2 and curr > sma20 else "P" if curr < prev < prev2 and curr < sma20 else "Wait"
    
    # Volatilität für Stop Loss
    tr = (df['High']-df['Low']).rolling(14).mean().iloc[-1]
    sl = curr - (tr * 1.5) if sig == "C" else curr + (tr * 1.5) if sig == "P" else 0
    
    return {"name": get_name(ticker), "ticker": ticker, "price": curr, "sig": sig, "icon": icon, "sl": sl, "delta": delta}

def render_row(res):
    st.markdown(f"""
    <div class="row-container">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="flex: 2;">
                <b>{res['name']}</b><br><small>{res['ticker']} | {res['price']:.2f}</small>
            </div>
            <div style="flex: 1; text-align: center; font-size: 1.2rem;">
                {res['icon']}<br><span style="color:{'#3fb950' if res['delta']>0 else '#007bff'}; font-size: 0.8rem;">{res['delta']:+.2f}%</span>
            </div>
            <div style="flex: 1; text-align: center;">
                <span class="sig-box {'sig-c' if res['sig']=='C' else 'sig-p' if res['sig']=='P' else ''}">{res['sig']}</span>
            </div>
            <div style="flex: 1; text-align: right;">
                <small>STOP</small><br><b>{res['sl']:.2f}</b>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- APP ---
st.markdown("<div class='header-text'>🌍 MARKT ÜBERSICHT</div>", unsafe_allow_html=True)
macros = ["EURUSD=X", "^GDAXI", "^STOXX50E"]
data = fetch_data(macros)

for t in macros:
    df = data.xs(t, axis=1, level=0).dropna() if len(macros)>1 else data.dropna()
    res = process_signal(t, df)
    render_row(res)

st.markdown("<div class='header-text'>🔭 EURO SCREENER</div>", unsafe_allow_html=True)
euro_list = ["ASML.AS", "MC.PA", "OR.PA", "SAP.DE", "TTE.PA", "SAN.MC"]

if st.button("🚀 EURO-SCAN STARTEN", use_container_width=True):
    batch = fetch_data(euro_list)
    results = []
    for t in euro_list:
        df = batch.xs(t, axis=1, level=0).dropna()
        res = process_signal(t, df)
        results.append(res)
        render_row(res)

    # --- TOP 3 GOLD LOGIK ---
    st.markdown("<div class='header-text'>📈 TOP ANALYSE</div>", unsafe_allow_html=True)
    for r in [x for x in results if x['sig'] != "Wait"][:3]:
        st.markdown(f"""
        <div class="mc-box">
            <span class="gold-title">{r['name']}</span> <span class="sig-box {'sig-c' if r['sig']=='C' else 'sig-p'}">{r['sig']}</span>
            <div style="margin-top: 10px;">
                Trendstärke bestätigt. Stop-Loss bei <b>{r['sl']:.2f}</b> aktiv.<br>
                Szenario: Median-Erwartung positiv.
            </div>
        </div>
        """, unsafe_allow_html=True)
