import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import time

# --- 0. AUTO-REFRESH & SETUP ---
try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    import os
    os.system('pip install streamlit-autorefresh')
    from streamlit_autorefresh import st_autorefresh

st_autorefresh(interval=45000, key="datarefresh")

# --- 1. CONFIG & STYLING ---
st.set_page_config(layout="wide", page_title="Bauer Strategy Pro 2026")

st.markdown("""
    <style>
    .stApp { background-color: #050a0f; }
    h1, h2, h3, p, span, label, div { color: #e0e0e0 !important; font-family: 'Courier New', Courier, monospace; }
    .header-text { font-size: 24px; font-weight: bold; margin-bottom: 5px; display: flex; align-items: center; gap: 10px; }
    .sig-box-p { color: #ff4b4b; border: 1px solid #ff4b4b; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
    .sig-box-c { color: #3fb950; border: 1px solid #3fb950; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
    .sl-label { color: #888; font-size: 0.85rem; }
    .sl-value { color: #e0e0e0; font-weight: bold; font-size: 1rem; }
    .prob-val { color: #888; font-size: 0.85rem; margin-left: 5px; }
    .row-container { border-bottom: 1px solid #1a202c; padding: 10px 0; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. NAMENS-DATENBANK & SESSION STATE ---
NAME_DB = {
    "EURUSD=X": "Euro / US-Dollar", "^GDAXI": "DAX 40", "^STOXX50E": "EURO STOXX 50",
    "^IXIC": "NASDAQ Composite", "XU100.IS": "BIST 100", "^NSEI": "NIFTY 50"
}

if 'cache_results' not in st.session_state:
    st.session_state.cache_results = {}

# --- 3. DATEN-ENGINE (SERIALISIERTER DOWNLOAD FÜR STABILITÄT) ---
def analyze_ticker(ticker):
    try:
        # Kein Multithreading für Macro-Abfragen zur Vermeidung von Geisterwerten
        df = yf.download(ticker, period="1y", interval="1d", progress=False, auto_adjust=True)
        if df.empty or len(df) < 25: return None
        
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        # EUR/USD Deep Clean
        if "EURUSD=X" in ticker:
            mask = (df['Close'] > 2.0) | (df['Close'] < 0.5)
            if mask.any():
                df.loc[mask, ['Open', 'High', 'Low', 'Close']] = df.loc[~mask, 'Close'].median() or 1.1625

        curr = float(df['Close'].iloc[-1])
        prev, prev2 = df['Close'].iloc[-2], df['Close'].iloc[-3]
        open_t = df['Open'].iloc[-1]
        sma20 = df['Close'].rolling(window=20).mean().iloc[-1]
        atr = (df['High']-df['Low']).rolling(window=14).mean().iloc[-1]
        
        signal = "C" if (curr > prev > prev2 and curr > sma20) else "P" if (curr < prev < prev2 and curr < sma20) else "Wait"
        delta = ((curr - open_t) / open_t) * 100
        stop = curr - (atr * 1.5) if signal == "C" else curr + (atr * 1.5) if signal == "P" else 0
        icon = "☀️" if (curr > sma20 and delta > 0.3) else "⚖️" if abs(delta) < 0.3 else "⛈️"
        
        # Win-Rate Simulation
        bt_df = df.tail(100).copy()
        bt_df['sma'] = bt_df['Close'].rolling(20).mean()
        hits = ((bt_df['Close'] > bt_df['sma']).sum() / 100) * 100

        res = {
            "display_name": NAME_DB.get(ticker, ticker), "ticker": ticker, "price": curr, 
            "delta": delta, "signal": signal, "stop": stop, "icon": icon, "prob": hits
        }
        # Im Session State speichern
        st.session_state.cache_results[ticker] = res
        return res
    except:
        return st.session_state.cache_results.get(ticker) # Letzten Wert zurückgeben, falls API fehlschlägt

# --- 4. UI RENDERER ---
def render_row(res):
    if not res: return
    fmt = "{:.6f}" if "=" in res['ticker'] else "{:.2f}"
    st.markdown("<div class='row-container'>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns([1.2, 0.6, 0.5, 1.2])
    
    with c1:
        st.markdown(f"**{res['display_name']}**<br><small style='color:#888;'>Kurs: {fmt.format(res['price'])}</small>", unsafe_allow_html=True)
    with c2:
        color = "#3fb950" if res['delta'] >= 0 else "#ff4b4b"
        st.markdown(f"<div style='text-align:center;'>{res['icon']}<br><span style='color:{color}; font-size:0.85rem;'>{res['delta']:+.2f}%</span></div>", unsafe_allow_html=True)
    with c3:
        if res['signal'] != "Wait":
            cls = "sig-box-c" if res['signal'] == "C" else "sig-box-p"
            st.markdown(f"<br><span class='{cls}'>{res['signal']}</span>", unsafe_allow_html=True)
        else: st.markdown(f"<br><span style='color:#444;'>{res['signal']}</span>", unsafe_allow_html=True)
    with c4:
        if res['stop'] != 0:
            prob_txt = f"({res['prob']:.1f}%)"
            st.markdown(f"<span class='sl-label'>Stop-Loss</span> <span class='prob-val'>{prob_txt}</span><br><span class='sl-value'>{fmt.format(res['stop'])}</span>", unsafe_allow_html=True)
        else: st.markdown("<span class='sl-label'>Stop-Loss</span><br><span style='color:#444;'>---</span>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- 5. MAIN APP ---
st.markdown("<div class='header-text'>📡 Dr. Gregor Bauer Strategie Pro</div>", unsafe_allow_html=True)
st.write(f"letztes update: {datetime.now().strftime('%H:%M:%S')} | Auto-Refresh: 45s")

with st.expander("ℹ️ Strategie-Logik & System-Erklärung"):
    st.markdown("### **1. Trend-Check (2-Tage-Regel)**...")

st.markdown("<div class='header-text'>🌍 Macro & Indices</div>", unsafe_allow_html=True)
macro_tickers = ["EURUSD=X", "^GDAXI", "^STOXX50E", "^IXIC", "XU100.IS", "^NSEI"]

# Macro-Abfragen nacheinander (stabilisiert die Daten)
for ticker in macro_tickers:
    res = analyze_ticker(ticker)
    if res: render_row(res)

st.markdown("<br><div class='header-text'>🔭 Market Scanner</div>", unsafe_allow_html=True)
# [Screener Sektion bleibt gleich...]
