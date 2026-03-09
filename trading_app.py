import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# --- SETUP ---
st_autorefresh(interval=300000, key="datarefresh")
st.set_page_config(layout="wide", page_title="Momentum Strategy", page_icon="📡")

# --- KLARNAMEN MAPPING (ERWEITERT) ---
NAME_MAP = {
    # IBEX 35 (Spanien)
    "SAN.MC": "BANCO SANTANDER", "ITX.MC": "INDITEX (ZARA)", "BBVA.MC": "BANCO BILBAO VIZCAYA",
    "IBE.MC": "IBERDROLA", "TEF.MC": "TELEFONICA", "REP.MC": "REPSOL",
    # BIST 100 (Türkei)
    "THYAO.IS": "TURKISH AIRLINES", "AKBNK.IS": "AKBANK", "TUPRS.IS": "TUPRAS PETROL",
    # DAX & NASDAQ
    "SAP.DE": "SAP SE", "ADS.DE": "ADIDAS AG", "AAPL": "APPLE INC.", "NVDA": "NVIDIA CORP."
}

def get_name(t):
    return NAME_MAP.get(t, t.upper())

# --- FUNKTIONEN ---
@st.cache_data(ttl=300)
def fetch_data(tickers):
    try:
        return yf.download(tickers, period="1y", interval="1d", auto_adjust=True, group_by='ticker', threads=False, timeout=10)
    except: return None

def process_signal(ticker, df):
    if df is None or df.empty or len(df) < 30: return None
    cp = df['Close']
    curr, prev, prev2 = cp.iloc[-1], cp.iloc[-2], cp.iloc[-3]
    sma20 = cp.rolling(20).mean().iloc[-1]
    
    delta = ((curr - df['Open'].iloc[-1]) / df['Open'].iloc[-1]) * 100
    icon = "☀️" if (curr > sma20 and delta > 0.2) else "⚖️" if abs(delta) < 0.2 else "⛈️"
    sig = "C" if curr > prev > prev2 and curr > sma20 else "P" if curr < prev < prev2 and curr < sma20 else "Wait"
    
    tr = (df['High']-df['Low']).rolling(14).mean().iloc[-1]
    sl = curr - (tr * 1.5) if sig == "C" else curr + (tr * 1.5) if sig == "P" else 0
    
    # Monte Carlo direkt hier für die Sortierung
    rets = cp.pct_change().dropna()
    mc_surv = np.mean([np.prod(1 + np.random.choice(rets, 252, replace=True)) > 0.8 for _ in range(200)]) * 100
    
    return {
        "name": get_name(ticker), "ticker": ticker, "price": curr, "sig": sig, 
        "icon": icon, "sl": sl, "delta": delta, "mc": mc_surv
    }

# --- UI LOGIK ---
st.markdown("<h2 style='color:#ffd700;'>🔭 MARKT SCREENER</h2>", unsafe_allow_html=True)
choice = st.radio("Region:", ["IBEX 35", "DAX 40", "US Tech", "BIST 100"], horizontal=True)

t_map = {
    "IBEX 35": ["SAN.MC", "ITX.MC", "BBVA.MC", "IBE.MC", "TEF.MC"],
    "DAX 40": ["SAP.DE", "ADS.DE", "ALV.DE", "SIE.DE"],
    "US Tech": ["AAPL", "NVDA", "MSFT", "TSLA"],
    "BIST 100": ["THYAO.IS", "AKBNK.IS", "TUPRS.IS"]
}

if st.button("🚀 SCAN STARTEN", use_container_width=True):
    batch = fetch_data(t_map[choice])
    results = []
    for t in t_map[choice]:
        try:
            df = batch[t] if len(t_map[choice]) > 1 else batch
            res = process_signal(t, df)
            if res: results.append(res)
        except: continue

    # --- SORTIERUNG & TOP 3 GOLD BOXEN ---
    st.markdown("<h3 style='color:#ffd700;'>📈 TOP SIGNALE (GEORDNET NACH SICHERHEIT)</h3>", unsafe_allow_html=True)
    
    # Sortiert nach Monte-Carlo Überlebens-Rate (Absteigend)
    top_3 = sorted([r for r in results if r['sig'] != "Wait"], key=lambda x: x['mc'], reverse=True)[:3]

    for r in top_3:
        st.markdown(f"""
        <div style="border: 1px solid #ffd700; background-color: #161b22; padding: 15px; border-radius: 10px; margin-bottom: 10px;">
            <span style="background-color: {'#3fb950' if r['sig']=='C' else '#007bff'}; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold; margin-right: 10px;">{r['sig']}</span>
            <b style="color: #ffd700; font-size: 1.1rem;">{r['name']}</b> 
            <span style="color: #888; margin-left: 15px;">Stop-Loss: {r['sl']:.2f}</span>
            <div style="margin-top: 10px; color: #eee; font-size: 0.9rem;">
                Überlebens-Rate (1J): <b style="color: #3fb950;">{r['mc']:.1f}%</b> | Wetter-Indikator: {r['icon']}
            </div>
        </div>
        """, unsafe_allow_html=True)
