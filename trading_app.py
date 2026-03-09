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
# Intervall auf 5 Minuten (300.000ms), um API-Sperren durch Yahoo zu vermeiden
st_autorefresh(interval=300000, key="datarefresh")
st.set_page_config(layout="wide", page_title="Momentum Strategy", page_icon="📡")

# --- STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #050a0f; }
    h1, h2, h3, p, span, label, div { color: #e0e0e0 !important; font-family: 'Courier New', Courier, monospace; }
    .header-text { font-size: 24px; font-weight: bold; margin-bottom: 5px; display: flex; align-items: center; gap: 10px; }
    .sig-box-p { color: #007bff !important; border: 1px solid #007bff !important; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
    .sig-box-c { color: #3fb950 !important; border: 1px solid #3fb950 !important; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
    .sig-box-high { color: #ffd700 !important; border: 1px solid #ffd700 !important; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
    .indicator-label { color: #888; font-size: 0.75rem; margin-top: 2px; }
    .row-container { border-bottom: 1px solid #1a202c; padding: 12px 0; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- CORE FUNCTIONS ---

def sparkline_svg(series, color="#3fb950"):
    values = list(series.values)
    if len(values) < 2: return ""
    min_v, max_v = min(values), max(values)
    span = max_v - min_v if max_v != min_v else 1.0
    norm = [(v - min_v) / span for v in values]
    points = " ".join(f"{i},{1 - v}" for i, v in enumerate(norm))
    width = max(len(values) - 1, 1)
    return f'<svg width="120" height="30" viewBox="0 0 {width} 1" xmlns="http://www.w3.org"><polyline fill="none" stroke="{color}" stroke-width="0.08" points="{points}" /></svg>'

@st.cache_data(ttl=300, show_spinner=False)
def fetch_batch_data(tickers):
    if not tickers: return {}
    if isinstance(tickers, str): tickers = [tickers]
    try:
        # threads=False verhindert Deadlocks in Streamlit
        data = yf.download(tickers=tickers, period="1y", interval="1d", auto_adjust=True, group_by='ticker', threads=False, timeout=10)
        if data is None or data.empty: return {}
        
        result = {}
        if len(tickers) > 1 and isinstance(data.columns, pd.MultiIndex):
            for t in tickers:
                if t in data.columns.get_level_values(0):
                    df_t = data.xs(t, axis=1, level=0).dropna()
                    if not df_t.empty: result[t] = df_t
        else:
            if not data.empty:
                t_key = tickers[0] if isinstance(tickers, list) else tickers
                result[t_key] = data.dropna()
        return result
    except: return {}

@st.cache_data(ttl=3600)
def get_name_for_ticker(ticker):
    try:
        t_obj = yf.Ticker(ticker)
        # Bevorzugt den Klarnamen (shortName)
        return t_obj.info.get('shortName') or t_obj.info.get('longName') or ticker
    except: return ticker

def compute_signal_from_df(ticker, df):
    try:
        if df is None or df.empty or len(df) < 35: return None
        cp = df['Close']
        delta_p = cp.diff()
        gain = delta_p.where(delta_p > 0, 0).rolling(14).mean()
        loss = (-delta_p.where(delta_p < 0, 0)).rolling(14).mean()
        rsi = 100 - (100 / (1 + (gain / (loss + 1e-9))))
        
        tr = pd.concat([df['High']-df['Low'], (df['High']-cp.shift()).abs(), (df['Low']-cp.shift()).abs()], axis=1).max(axis=1)
        atr = tr.rolling(14).mean().iloc[-1]
        adx = ((df['High'].diff().abs() - df['Low'].diff().abs()).abs() / (tr + 1e-9)).rolling(14).mean().iloc[-1] * 100

        curr, prev, prev2 = cp.iloc[-1], cp.iloc[-2], cp.iloc[-3]
        sma20 = cp.rolling(20).mean().iloc[-1]
        daily_delta = ((curr - df['Open'].iloc[-1]) / df['Open'].iloc[-1]) * 100

        signal = "C" if curr > prev > prev2 and curr > sma20 else ("P" if curr < prev < prev2 and curr < sma20 else "Wait")
        
        # Win-Rate Check
        bt_df = df.tail(60).copy()
        bt_df['SMA20'] = bt_df['Close'].rolling(20).mean()
        hits, sigs = 0, 0
        for i in range(20, len(bt_df)-3):
            c, p, p2 = bt_df['Close'].iloc[i], bt_df['Close'].iloc[i-1], bt_df['Close'].iloc[i-2]
            if (signal=="C" and c>p>p2 and c>bt_df['SMA20'].iloc[i]) or (signal=="P" and c<p<p2 and c<bt_df['SMA20'].iloc[i]):
                sigs += 1
                if (signal=="C" and bt_df['Close'].iloc[i+3] > c) or (signal=="P" and bt_df['Close'].iloc[i+3] < c): hits += 1
        prob = (hits/sigs*100) if sigs > 0 else 50.0

        return {
            "name": get_name_for_ticker(ticker), "ticker": ticker, "price": float(curr), "delta": daily_delta,
            "signal": signal, "stop": curr-(atr*1.5) if signal=="C" else (curr+(atr*1.5) if signal=="P" else 0),
            "prob": prob, "rsi": rsi.iloc[-1], "adx": adx, "icon": "☀️" if (curr>sma20 and daily_delta>0.3) else ("⚖️" if abs(daily_delta)<0.3 else "⛈️"),
            "spark": sparkline_svg(cp.tail(20), "#3fb950" if curr>=prev else "#007bff")
        }
    except: return None

def render_row(res):
    fmt = "{:.6f}" if "=" in res['ticker'] else "{:.2f}"
    st.markdown("<div class='row-container'>", unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns([1.2, 0.6, 0.8, 0.5, 1.1])
    with c1: st.markdown(f"**{res['name']}**<br><small>{fmt.format(res['price'])}</small>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div style='text-align:center;'>{res['icon']}<br><span style='color:{'#3fb950' if res['delta']>=0 else '#007bff'};'>{res['delta']:+.2f}%</span></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(res["spark"], unsafe_allow_html=True)
        st.markdown(f"<span class='indicator-label'>RSI: {res['rsi']:.1f} | ADX: {res['adx']:.1f}</span>", unsafe_allow_html=True)
    with c4:
        if res['signal'] != "Wait":
            cls = "sig-box-high" if res['prob'] >= 60 else ("sig-box-c" if res['signal'] == "C" else "sig-box-p")
            st.markdown(f"<br><span class='{cls}'>{res['signal']}</span>", unsafe_allow_html=True)
    with c5:
        if res['stop'] != 0: st.markdown(f"<small>SL ({res['prob']:.1f}%)</small><br><b>{fmt.format(res['stop'])}</b>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- UI MAIN ---
st.markdown("<div class='header-text'>📡 Momentum Strategie 📡</div>", unsafe_allow_html=True)
st.write(f"Update: {datetime.now().strftime('%H:%M:%S')} | Auto-Refresh: 5m")

with st.expander("📘 Ausführlicher Strategie‑Leitfaden & Markt‑Logik 📘", expanded=False):
    st.markdown("""
    ## 🧭 Überblick des Momentum‑Monitors
    Kombiniert technische Analyse, Trend‑Erkennung und statistische Risiko‑Modelle.
    - **C (Call/Long)**: Starker Aufwärtstrend über SMA20.
    - **P (Put/Short)**: Starker Abwärtstrend unter SMA20.
    - **Wahrscheinlichkeit**: Historische Trefferquote der Signal-Konstellation über die letzten 60 Tage.
    - **Risikomanagement**: Stop-Loss basiert auf der ATR (Average True Range).
    """)

# --- MACRO SECTION ---
st.markdown("<div class='header-text'>🌍 Macro + Indices 🌍</div>", unsafe_allow_html=True)
macro_list = ["EURUSD=X", "^GDAXI", "^STOXX50E", "^IXIC", "XU100.IS", "^NSEI"]
macro_data = fetch_batch_data(macro_list)

if not macro_data:
    st.warning("Warte auf API-Antwort von Yahoo Finance...")
else:
    for t in macro_list:
        df_t = macro_data.get(t)
        if df_t is not None:
            res = compute_signal_from_df(t, df_t)
            if res: render_row(res)

# --- SCREENER ---
st.markdown("<br><div class='header-text'>🔭 Markt Screener 🔭</div>", unsafe_allow_html=True)
if 'scan_active' not in st.session_state: st.session_state.scan_active = False

with st.expander("Index-Auswahl & Scan Steuerung", expanded=True):
    choice = st.radio("Markt:", ["DAX 40", "EuroStoxx 50", "Nasdaq 100", "BIST 100", "NIFTY 50"], horizontal=True)
    if st.button("🚀 Scan Start/Stop", use_container_width=True): st.session_state.scan_active = not st.session_state.scan_active

if st.session_state.scan_active:
    t_lists = {
        "DAX 40": ["ADS.DE", "AIR.DE", "ALV.DE", "BAS.DE", "BAYN.DE", "BMW.DE", "CON.DE", "1COV.DE", "DTG.DE", "DTE.DE", "DBK.DE", "DB1.DE", "DHL.DE", "EON.DE", "FRE.DE", "FME.DE", "HEI.DE", "HEN3.DE", "IFX.DE", "MBG.DE", "MRK.DE", "MTX.DE", "MUV2.DE", "PUM.DE", "PAH3.DE", "RWE.DE", "SAP.DE", "SIE.DE", "SHL.DE", "SY1.DE", "TKA.DE", "VOW3.DE", "VNA.DE", "ZAL.DE", "BEI.DE", "CBK.DE", "RHM.DE", "SRT3.DE", "ENR.DE", "QIA.DE"],
        "Nasdaq 100": ["AAPL", "MSFT", "NVDA", "AMZN", "TSLA", "GOOGL", "META", "AVGO", "COST", "NFLX", "ADBE", "AMD"], # Gekürzt für Code-Beispiel
        "EuroStoxx 50": ["ASML.AS", "MC.PA", "OR.PA", "SAP.DE", "TTE.PA", "SIE.DE", "AIR.PA"],
        "BIST 100": ["THYAO.IS", "AKBNK.IS", "EREGL.IS", "TUPRS.IS", "SISE.IS", "KCHOL.IS"],
        "NIFTY 50": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS"]
    }
    tickers = t_lists.get(choice, ["AAPL"])
    batch = fetch_batch_data(tickers)
    
    results = []
    for t in tickers:
        df_t = batch.get(t)
        if df_t is not None:
            res = compute_signal_from_df(t, df_t)
            if res: results.append(res)
    
    hits = sorted([r for r in results if r['signal'] != "Wait"], key=lambda x: -x['prob'])
    if hits:
        for r in hits: render_row(r)
    else:
        st.info("Keine aktiven Signale in diesem Markt.")

# --- TOP SIGNALE ---
if st.session_state.scan_active and 'results' in locals() and results:
    st.markdown("---")
    top_3 = sorted([r for r in results if r['signal'] != "Wait"], key=lambda x: (-x['prob'], -x['adx']))[:3]
    with st.expander("📈 Top-Signale Detail-Analyse", expanded=True):
        for res in top_3:
            st.write(f"### {res['name']} ({res['ticker']})")
            st.write(f"Signal: {res['signal']} | Wahrscheinlichkeit: {res['prob']:.1f}% | RSI: {res['rsi']:.1f}")
