import os
import sys

# --- AUTO-INSTALLER ---
def install_and_import(package):
    try:
        __import__(package.replace('-', '_'))
    except ImportError:
        os.system(f"{sys.executable} -m pip install {package}")

install_and_import('streamlit-autorefresh')
install_and_import('lxml')
install_and_import('html5lib')
install_and_import('yfinance')

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# --- SETUP & REFRESH ---
# 5-Minuten Intervall für Stabilität
st_autorefresh(interval=300000, key="datarefresh")
st.set_page_config(layout="wide", page_title="Momentum Monitor", page_icon="📡")

# --- STYLING (HÖHE & KONTRAST OPTIMIERT) ---
st.markdown("""
    <style>
    .stApp { background-color: #050a0f; }
    [data-testid="column"] { padding: 0px 8px !important; }
    .header-text { font-size: 20px; font-weight: bold; margin-top: 15px; color: #ffd700 !important; }
    .update-info { text-align: right; color: #666; font-size: 0.8rem; margin-top: -15px; margin-bottom: 10px; }
    
    /* Zeilen-Design */
    .row-container { border-bottom: 1px solid #1a202c; padding: 6px 0 !important; width: 100%; line-height: 1.2; }
    
    /* Signal Badges */
    .sig-badge { padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 0.85rem; }
    .sig-c { background-color: rgba(63, 185, 80, 0.2); color: #3fb950; border: 1px solid #3fb950; }
    .sig-p { background-color: rgba(0, 123, 255, 0.2); color: #007bff; border: 1px solid #007bff; }
    
    /* Gold-Box für Risiko-Analyse */
    .mc-box { 
        background-color: #161b22; padding: 15px; border-radius: 10px; 
        border: 1px solid #ffd700; margin-bottom: 12px; color: #ffffff !important; 
    }
    .gold-title { color: #ffd700; font-size: 1.1rem; font-weight: bold; }
    small { font-size: 0.75rem; color: #888; }
    b { color: #fff; }
    </style>
    """, unsafe_allow_html=True)

# --- KLARNAMEN MAPPING ---
NAME_MAP = {
    "EURUSD=X": "EURO / US-DOLLAR", "^GDAXI": "DAX 40 INDEX", "^STOXX50E": "EUROSTOXX 50", 
    "^IXIC": "NASDAQ COMPOSITE", "XU100.IS": "BIST 100 INDEX", "^NSEI": "NIFTY 50 INDEX",
    "^IBEX": "IBEX 35 SPAIN",
    # BIST (Beispiele)
    "THYAO.IS": "TURKISH AIRLINES", "AKBNK.IS": "AKBANK", "TUPRS.IS": "TUPRAS PETROL",
    # NASDAQ (Beispiele)
    "AAPL": "APPLE INC.", "NVDA": "NVIDIA CORP.", "MSFT": "MICROSOFT CORP.", "TSLA": "TESLA INC."
}

@st.cache_data(ttl=3600)
def get_name_safe(ticker):
    if ticker in NAME_MAP: return NAME_MAP[ticker]
    try:
        t_obj = yf.Ticker(ticker)
        return (t_obj.info.get('shortName') or t_obj.info.get('longName') or ticker).upper()
    except: return ticker.upper()

# --- CORE FUNCTIONS ---
@st.cache_data(ttl=300, show_spinner=False)
def fetch_batch_data(tickers):
    if not tickers: return {}
    try:
        data = yf.download(tickers=tickers, period="1y", interval="1d", auto_adjust=True, group_by='ticker', threads=False, timeout=12)
        if data is None or data.empty: return {}
        result = {}
        if len(tickers) > 1:
            for t in tickers:
                if t in data.columns.get_level_values(0):
                    df_t = data.xs(t, axis=1, level=0).dropna()
                    if not df_t.empty: result[t] = df_t
        else:
            if not data.empty: result[tickers if isinstance(tickers, list) else tickers] = data.dropna()
        return result
    except: return {}

def compute_signal_from_df(ticker, df):
    try:
        if df is None or df.empty or len(df) < 30: return None
        cp = df['Close']
        curr, prev, prev2 = cp.iloc[-1], cp.iloc[-2], cp.iloc[-3]
        sma20 = cp.rolling(20).mean().iloc[-1]
        
        # Wetter-Logik
        daily_delta = ((curr - df['Open'].iloc[-1]) / df['Open'].iloc[-1]) * 100
        icon = "☀️" if (curr > sma20 and daily_delta > 0.2) else "⚖️" if abs(daily_delta) < 0.2 else "⛈️"
        
        # Signal & SL
        signal = "C" if curr > prev > prev2 and curr > sma20 else ("P" if curr < prev < prev2 and curr < sma20 else "Wait")
        tr = (df['High']-df['Low']).rolling(14).mean().iloc[-1]
        sl = curr-(tr*1.5) if signal=="C" else (curr+(tr*1.5) if signal=="P" else 0)
        
        return {
            "name": get_name_safe(ticker), "ticker": ticker, "price": float(curr), 
            "delta": daily_delta, "signal": signal, "stop": sl, "icon": icon, "df": df
        }
    except: return None

def render_row(res, prefix="row"):
    fmt = "{:.2f}"
    with st.container(key=f"cont_{prefix}_{res['ticker']}"):
        st.markdown("<div class='row-container'>", unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns([2.5, 0.8, 0.8, 1.0])
        with c1: st.markdown(f"**{res['name']}**<br><small>{res['ticker']} | {fmt.format(res['price'])}</small>", unsafe_allow_html=True)
        with c2: st.markdown(f"<div style='text-align:center;'>{res['icon']}<br><span style='color:{'#3fb950' if res['delta']>=0 else '#007bff'}; font-size:0.75rem;'>{res['delta']:+.2f}%</span></div>", unsafe_allow_html=True)
        with c3:
            if res['signal'] != "Wait":
                cls = "sig-c" if res['signal'] == "C" else "sig-p"
                st.markdown(f"<div style='margin-top:5px;'><span class='sig-badge {cls}'>{res['signal']}</span></div>", unsafe_allow_html=True)
        with c4:
            if res['stop'] != 0: st.markdown(f"<small>STOP-LOSS</small><br><b>{fmt.format(res['stop'])}</b>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# --- UI MAIN ---
st.markdown(f"<div class='update-info'>Update: {datetime.now().strftime('%H:%M:%S')} | Auto-Refresh: 5m</div>", unsafe_allow_html=True)
st.markdown("<div class='header-text'>🌍 GLOBAL MACRO + INDICES</div>", unsafe_allow_html=True)

m_list = ["EURUSD=X", "^GDAXI", "^STOXX50E", "^IXIC", "XU100.IS", "^NSEI"]
m_data = fetch_batch_data(m_list)
if m_data:
    for t in m_list:
        if t in m_data:
            res = compute_signal_from_df(t, m_data[t])
            if res: render_row(res, "macro")

# --- SCREENER ---
st.markdown("<br><div class='header-text'>🔭 MARKT SCREENER</div>", unsafe_allow_html=True)
choice = st.radio("Markt wählen:", ["US Tech", "DAX 40", "IBEX 35", "BIST 100", "NIFTY 50"], horizontal=True, label_visibility="collapsed")

if st.button("🚀 SCAN STARTEN", use_container_width=True):
    t_map = {
        "US Tech": ["AAPL", "MSFT", "NVDA", "AMZN", "TSLA", "GOOGL", "META", "AVGO", "NFLX", "AMD"],
        "DAX 40": ["ADS.DE", "AIR.DE", "ALV.DE", "BAS.DE", "BAYN.DE", "BMW.DE", "SAP.DE", "SIE.DE", "DTE.DE", "VOW3.DE"],
        "IBEX 35": ["SAN.MC", "ITX.MC", "BBVA.MC", "IBE.MC", "TEF.MC", "REP.MC", "FER.MC", "AMS.MC"],
        "BIST 100": ["THYAO.IS", "AKBNK.IS", "EREGL.IS", "TUPRS.IS", "SISE.IS", "KCHOL.IS", "ASELS.IS", "BIMAS.IS"],
        "NIFTY 50": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS", "HINDUNILVR.NS"]
    }
    tickers = t_map.get(choice, ["AAPL"])
    batch = fetch_batch_data(tickers)
    results = []
    
    for t in tickers:
        if t in batch:
            res = compute_signal_from_df(t, batch[t])
            if res:
                results.append(res)
                render_row(res, "scan")

    # --- TOP 3 GOLD LOGIK & MONTE CARLO ---
    st.markdown("<br><div class='header-text'>📈 RISIKO-ANALYSE (TOP SIGNALE)</div>", unsafe_allow_html=True)
    top_sigs = [r for r in results if r['signal'] != "Wait"][:3]
    for res in top_sigs:
        # Schnelle Simulation
        rets = res['df']['Close'].pct_change().dropna()
        mc_surv = np.mean([np.prod(1 + np.random.choice(rets, 252, replace=True)) > 0.8 for _ in range(200)]) * 100
        
        st.markdown(f"""
        <div class='mc-box'>
            <span class='sig-badge {'sig-c' if res['signal']=='C' else 'sig-p'}'>{res['signal']}</span>
            <span class='gold-title'>{res['name']}</span> 
            <span style='margin-left:15px; color:#888;'>Stop-Loss: {res['stop']:.2f}</span><br>
            <div style='margin-top:10px;'>
                <span style='color:#8b949e; font-size:0.8rem;'>Überlebens-Rate (1J):</span> <b style='color:#3fb950;'>{mc_surv:.1f}%</b> | 
                <span style='color:#8b949e; font-size:0.8rem;'>Wetter-Indikator:</span> {res['icon']}
            </div>
        </div>
        """, unsafe_allow_html=True)
