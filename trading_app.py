import os
import sys

# --- AUTO-INSTALLER ---
def install_and_import(package):
    try:
        __import__(package.replace('-', '_'))
    except ImportError:
        os.system(f"{sys.executable} -m pip install {package}")

install_and_import('streamlit-autorefresh')
install_and_import('yfinance')

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# --- SETUP & REFRESH ---
st_autorefresh(interval=300000, key="datarefresh")
st.set_page_config(layout="wide", page_title="Momentum Strategy", page_icon="📡")

# --- STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #050a0f; }
    [data-testid="column"] { padding: 0px 8px !important; }
    .header-text { font-size: 20px; font-weight: bold; margin-top: 15px; color: #ffd700 !important; }
    .row-container { border-bottom: 1px solid #1a202c; padding: 6px 0 !important; width: 100%; line-height: 1.2; }
    /* Monte-Carlo Box Design */
    .mc-box { 
        background-color: #161b22; 
        padding: 15px; 
        border-radius: 10px; 
        border: 1px solid #30363d; 
        margin-bottom: 12px;
        color: #ffffff !important; 
    }
    .sig-badge { padding: 2px 6px; border-radius: 4px; font-weight: bold; font-size: 0.8rem; margin-right: 8px; }
    .sig-c { background-color: rgba(63, 185, 80, 0.2); color: #3fb950; border: 1px solid #3fb950; }
    .sig-p { background-color: rgba(0, 123, 255, 0.2); color: #007bff; border: 1px solid #007bff; }
    .mc-label { color: #8b949e; font-size: 0.8rem; }
    </style>
    """, unsafe_allow_html=True)

# --- ERWEITERTES MAPPING FÜR KLARNAMEN ---
NAME_MAP = {
    "TTE.PA": "TOTALENERGIES SE", "SAN.MC": "BANCO SANTANDER", "CS.PA": "AXA SA",
    "MC.PA": "LVMH MOET HENNESSY", "OR.PA": "L'OREAL SA", "ASML.AS": "ASML HOLDING",
    "EURUSD=X": "EURO / US-DOLLAR", "^GDAXI": "DAX 40", "^IXIC": "NASDAQ", "XU100.IS": "BIST 100",
    "AAPL": "APPLE INC.", "NVDA": "NVIDIA CORP.", "ADS.DE": "ADIDAS AG", "SAP.DE": "SAP SE"
}

@st.cache_data(ttl=3600)
def get_name_safe(ticker):
    if ticker in NAME_MAP: return NAME_MAP[ticker]
    try:
        info = yf.Ticker(ticker).info
        return (info.get('shortName') or info.get('longName') or ticker).upper()
    except: return ticker.upper()

# --- CORE FUNCTIONS ---
@st.cache_data(ttl=300, show_spinner=False)
def fetch_batch_data(tickers):
    if not tickers: return {}
    try:
        data = yf.download(tickers=tickers, period="1y", interval="1d", auto_adjust=True, group_by='ticker', threads=False, timeout=10)
        result = {}
        if len(tickers) > 1:
            for t in tickers:
                if t in data.columns.get_level_values(0):
                    df_t = data.xs(t, axis=1, level=0).dropna()
                    if not df_t.empty: result[t] = df_t
        else:
            if not data.empty: result[tickers[0] if isinstance(tickers, list) else tickers] = data.dropna()
        return result
    except: return {}

def compute_signal_from_df(ticker, df):
    try:
        cp = df['Close']
        curr, prev, prev2 = cp.iloc[-1], cp.iloc[-2], cp.iloc[-3]
        sma20 = cp.rolling(20).mean().iloc[-1]
        tr = pd.concat([df['High']-df['Low'], (df['High']-cp.shift()).abs(), (df['Low']-cp.shift()).abs()], axis=1).max(axis=1)
        atr = tr.rolling(14).mean().iloc[-1]
        
        signal = "C" if curr > prev > prev2 and curr > sma20 else ("P" if curr < prev < prev2 and curr < sma20 else "Wait")
        daily_delta = ((curr - df['Open'].iloc[-1]) / df['Open'].iloc[-1]) * 100
        
        return {
            "name": get_name_safe(ticker), "ticker": ticker, "price": float(curr), 
            "delta": daily_delta, "signal": signal, 
            "stop": curr-(atr*1.5) if signal=="C" else (curr+(atr*1.5) if signal=="P" else 0)
        }
    except: return None

def monte_carlo_sim(df, sims=250):
    if df is None or len(df) < 50: return None
    rets = df['Close'].pct_change().dropna()
    res = [np.prod(1 + np.random.choice(rets, 252, replace=True)) for _ in range(sims)]
    return {"median": np.median(res), "worst": np.min(res), "survival": np.mean(np.array(res) > 0.8) * 100}

def render_row(res, prefix="row"):
    fmt = "{:.2f}"
    with st.container(key=f"cont_{prefix}_{res['ticker']}"):
        st.markdown("<div class='row-container'>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([2.5, 1.0, 1.0])
        with c1: st.markdown(f"**{res['name']}**<br><small>{res['ticker']} | {fmt.format(res['price'])}</small>", unsafe_allow_html=True)
        with c2: 
            cls = "sig-box-c" if res['signal'] == "C" else "sig-box-p"
            if res['signal'] != "Wait": st.markdown(f"<span class='{cls}'>{res['signal']}</span>", unsafe_allow_html=True)
        with c3: 
            if res['stop'] != 0: st.markdown(f"<small>STOP</small><br><b>{fmt.format(res['stop'])}</b>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# --- UI ---
st.markdown("<div class='header-text'>📡 MOMENTUM MONITOR</div>", unsafe_allow_html=True)

# Macro Section
m_list = ["EURUSD=X", "^GDAXI", "^STOXX50E", "^IXIC"]
m_data = fetch_batch_data(m_list)
for t in m_list:
    if t in m_data:
        res = compute_signal_from_df(t, m_data[t])
        if res: render_row(res, "macro")

# Screener Section
st.markdown("<br><div class='header-text'>🔭 EURO-MARKET SCREENER</div>", unsafe_allow_html=True)
euro_tickers = ["TTE.PA", "SAN.MC", "CS.PA", "MC.PA", "OR.PA", "ASML.AS"]

if st.button("🚀 SCAN START", use_container_width=True):
    batch = fetch_batch_data(euro_tickers)
    results = []
    for t in euro_tickers:
        if t in batch:
            res = compute_signal_from_df(t, batch[t])
            if res: 
                results.append(res)
                render_row(res, "scan")

    # --- TOP 3 RISIKOANALYSE ---
    st.markdown("<br><div class='header-text'>📈 RISIKOANALYSE (MONTE-CARLO)</div>", unsafe_allow_html=True)
    for res in [r for r in results if r['signal'] != "Wait"][:3]:
        mc = monte_carlo_sim(batch[res['ticker']])
        if mc:
            sig_cls = "sig-c" if res['signal'] == "C" else "sig-p"
            st.markdown(f"""
            <div class='mc-box'>
                <span class='sig-badge {sig_cls}'>{res['signal']}</span>
                <b style='font-size:1.1rem; color:#ffd700;'>{res['name']}</b> 
                <span style='margin-left:15px; color:#888;'>Stop-Loss: {res['stop']:.2f}</span><br>
                <div style='margin-top:8px;'>
                    <span class='mc-label'>Überlebens-Rate:</span> <span style='color:#3fb950; font-weight:bold;'>{mc['survival']:.0f}%</span> | 
                    <span class='mc-label'>Median:</span> <b>{mc['median']:.2f}</b> | 
                    <span class='mc-label'>Worst Case:</span> <span style='color:#ff4b4b;'>{mc['worst']:.2f}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
