import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# --- SETUP ---
# Intervall auf 5 Minuten (300.000ms) für maximale API-Stabilität
st_autorefresh(interval=300000, key="datarefresh")
st.set_page_config(layout="wide", page_title="Momentum Strategy", page_icon="📡")

# --- STYLING (REPARIERT & KONTRASTREICH) ---
st.markdown("""
    <style>
    .stApp { background-color: #050a0f; }
    .header-text { font-size: 22px; font-weight: bold; margin-top: 15px; color: #ffd700 !important; }
    .row-container { border-bottom: 1px solid #1a202c; padding: 12px 0 !important; line-height: 1.4 !important; }
    .sig-box { padding: 4px 10px; border-radius: 5px; font-weight: bold; font-size: 0.9rem; display: inline-block; }
    .sig-c { background-color: rgba(63, 185, 80, 0.2); color: #3fb950; border: 1px solid #3fb950; }
    .sig-p { background-color: rgba(0, 123, 255, 0.2); color: #007bff; border: 1px solid #007bff; }
    .mc-box { 
        background-color: #161b22; padding: 15px; border-radius: 10px; 
        border: 1px solid #ffd700; margin-top: 15px; color: #ffffff !important; 
    }
    .gold-title { color: #ffd700; font-size: 1.1rem; font-weight: bold; }
    .update-info { text-align: right; color: #666; font-size: 0.8rem; margin-top: -10px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- KLARNAMEN MAPPING (ALLE INDIZES) ---
NAME_MAP = {
    "EURUSD=X": "EURO / US-DOLLAR", "^GDAXI": "DAX 40 INDEX", "^STOXX50E": "EUROSTOXX 50 INDEX", 
    "^IXIC": "NASDAQ COMPOSITE", "XU100.IS": "BIST 100 INDEX", "^NSEI": "NIFTY 50 INDEX",
    "ASML.AS": "ASML HOLDING", "MC.PA": "LVMH MOET HENNESSY", "OR.PA": "L'OREAL SA", 
    "TTE.PA": "TOTALENERGIES SE", "SAN.MC": "BANCO SANTANDER", "SAP.DE": "SAP SE"
}

# --- FUNKTIONEN ---
@st.cache_data(ttl=300)
def fetch_data(tickers):
    if not tickers: return None
    try:
        data = yf.download(tickers, period="1y", interval="1d", auto_adjust=True, group_by='ticker', threads=False, timeout=10)
        return data
    except: return None

def process_signal(ticker, df):
    if df is None or df.empty or len(df) < 25: return None
    cp = df['Close']
    curr, prev, prev2 = cp.iloc[-1], cp.iloc[-2], cp.iloc[-3]
    sma20 = cp.rolling(20).mean().iloc[-1]
    
    delta = ((curr - df['Open'].iloc[-1]) / df['Open'].iloc[-1]) * 100
    icon = "☀️" if (curr > sma20 and delta > 0.2) else "⚖️" if abs(delta) < 0.2 else "⛈️"
    sig = "C" if curr > prev > prev2 and curr > sma20 else "P" if curr < prev < prev2 and curr < sma20 else "Wait"
    
    tr = (df['High']-df['Low']).rolling(14).mean().iloc[-1]
    sl = curr - (tr * 1.5) if sig == "C" else curr + (tr * 1.5) if sig == "P" else 0
    
    return {"name": NAME_MAP.get(ticker, ticker.upper()), "ticker": ticker, "price": curr, "sig": sig, "icon": icon, "sl": sl, "delta": delta, "df": df}

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
                <small>STOP-LOSS</small><br><b>{res['sl']:.2f}</b>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- APP ---
# Zeitstempel & Intervall
st.markdown(f"<div class='update-info'>Letztes Update: {datetime.now().strftime('%H:%M:%S')} | Intervall: 5 Min.</div>", unsafe_allow_html=True)

# GLOBAL MACRO SECTION
st.markdown("<div class='header-text'>🌍 GLOBAL MACRO + INDICES</div>", unsafe_allow_html=True)
macro_list = ["EURUSD=X", "^GDAXI", "^STOXX50E", "^IXIC", "XU100.IS", "^NSEI"]
data_m = fetch_data(macro_list)

if data_m is not None:
    for t in macro_list:
        try:
            df = data_m[t] if len(macro_list) > 1 else data_m
            res = process_signal(t, df)
            if res: render_row(res)
        except: continue

# EURO SCREENER SECTION
st.markdown("<br><div class='header-text'>🔭 EURO-MARKT-SCREENER</div>", unsafe_allow_html=True)
euro_list = ["ASML.AS", "MC.PA", "OR.PA", "TTE.PA", "SAN.MC", "SAP.DE"]

if st.button("🚀 SCAN STARTEN", use_container_width=True):
    batch = fetch_data(euro_list)
    results = []
    if batch is not None:
        for t in euro_list:
            try:
                df = batch[t]
                res = process_signal(t, df)
                if res:
                    results.append(res)
                    render_row(res)
            except: continue

    # TOP 3 RISK ANALYSIS
    if any(r['sig'] != "Wait" for r in results):
        st.markdown("<div class='header-text'>📈 RISIKO-ANALYSE (MONTE-CARLO)</div>", unsafe_allow_html=True)
        for r in [x for x in results if x['sig'] != "Wait"][:3]:
            # Schnelle Simulation
            rets = r['df']['Close'].pct_change().dropna()
            mc_surv = np.mean([np.prod(1 + np.random.choice(rets, 252, replace=True)) > 0.8 for _ in range(200)]) * 100
            
            st.markdown(f"""
            <div class="mc-box">
                <span class="gold-title">{r['name']}</span> 
                <span class="sig-box {'sig-c' if r['sig']=='C' else 'sig-p'}">{r['sig']}</span>
                <div style="margin-top: 10px;">
                    Überlebens-Rate (1J): <b style="color:#3fb950;">{mc_surv:.1f}%</b> | 
                    Stop-Loss: <b>{r['sl']:.2f}</b><br>
                    <small>Trend bestätigt durch Wetter-Icon {r['icon']}.</small>
                </div>
            </div>
            """, unsafe_allow_html=True)
