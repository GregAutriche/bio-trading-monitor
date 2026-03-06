import os
import sys

# --- AUTO-INSTALLER FÜR FEHLENDE MODULE ---
def install_and_import(package):
    try:
        __import__(package)
    except ImportError:
        os.system(f"{sys.executable} -m pip install {package}")

install_and_import('matplotlib')
install_and_import('streamlit_autorefresh')

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import base64
import io
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh

# --- 0. AUTO-REFRESH & SETUP ---
st_autorefresh(interval=60000, key="datarefresh")

# --- 1. CONFIG & STYLING ---
st.set_page_config(layout="wide", page_title="Bauer Strategy Pro 2026", page_icon="📡")

st.markdown("""
    <style>
    .stApp { background-color: #050a0f; }
    h1, h2, h3, p, span, label, div { color: #e0e0e0 !important; font-family: 'Courier New', Courier, monospace; }
    .header-text { font-size: 24px; font-weight: bold; margin-bottom: 5px; display: flex; align-items: center; gap: 10px; }
    .sig-box-p { color: #007bff !important; border: 1px solid #007bff !important; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
    .sig-box-c { color: #3fb950 !important; border: 1px solid #3fb950 !important; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
    .sig-box-high { color: #ffd700 !important; border: 1px solid #ffd700 !important; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
    .sl-label { color: #888; font-size: 0.85rem; }
    .sl-value { color: #e0e0e0; font-weight: bold; font-size: 1.1rem; }
    .indicator-label { color: #888; font-size: 0.75rem; margin-top: 2px; }
    .row-container { border-bottom: 1px solid #1a202c; padding: 12px 0; width: 100%; }
    .scan-info { color: #ffd700; font-style: italic; font-size: 0.9rem; margin-bottom: 10px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. HILFSFUNKTIONEN ---
def create_sparkline(data, color):
    plt.figure(figsize=(2.5, 0.6), dpi=70)
    plt.plot(data.values, color=color, linewidth=2.5)
    plt.axis('off')
    plt.gca().set_facecolor((0,0,0,0))
    buf = io.BytesIO()
    plt.savefig(buf, format='png', transparent=True, bbox_inches='tight', pad_inches=0)
    plt.close()
    return base64.b64encode(buf.getvalue()).decode()

@st.cache_data(ttl=300)
def get_historical_data(ticker):
    try:
        t_obj = yf.Ticker(ticker)
        df = t_obj.history(period="1y", interval="1d", auto_adjust=True)
        if df.empty or len(df) < 35: return None, None
        return df, t_obj.info.get('shortName') or ticker
    except: return None, None

def calculate_indicators(df):
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / (loss + 1e-9)
    df['RSI'] = 100 - (100 / (1 + rs))
    tr = pd.concat([df['High']-df['Low'], abs(df['High']-df['Close'].shift()), abs(df['Low']-df['Close'].shift())], axis=1).max(axis=1)
    atr = tr.rolling(window=14).mean()
    df['ADX'] = (abs(df['High'].diff() - abs(df['Low'].diff())) / (tr + 1e-9)).rolling(window=14).mean() * 100
    return df, atr.iloc[-1]

def calculate_probability(df, signal_type):
    if df is None or len(df) < 50: return 50.0
    bt_df = df.copy()
    bt_df['SMA20'] = bt_df['Close'].rolling(window=20).mean()
    hits, signals = 0, 0
    for i in range(25, len(bt_df) - 5):
        c, p, p2 = bt_df['Close'].iloc[i], bt_df['Close'].iloc[i-1], bt_df['Close'].iloc[i-2]
        sma = bt_df['SMA20'].iloc[i]
        h_sig = "C" if (c > p > p2 and c > sma) else "P" if (c < p < p2 and c < sma) else None
        if h_sig == signal_type:
            signals += 1
            if (signal_type == "C" and bt_df['Close'].iloc[i+3] > c) or \
               (signal_type == "P" and bt_df['Close'].iloc[i+3] < c):
                hits += 1
    return (hits / signals * 100) if signals > 0 else 50.0

def fetch_data(ticker):
    df, name = get_historical_data(ticker)
    if df is None: return None
    df, last_atr = calculate_indicators(df)
    curr = float(df['Close'].iloc[-1])
    prev, prev2 = df['Close'].iloc[-2], df['Close'].iloc[-3]
    open_t = df['Open'].iloc[-1]
    sma20 = df['Close'].rolling(window=20).mean().iloc[-1]
    rsi_val = df['RSI'].iloc[-1]
    adx_val = df['ADX'].iloc[-1]
    signal = "C" if (curr > prev > prev2 and curr > sma20) else "P" if (curr < prev < prev2 and curr < sma20) else "Wait"
    delta = ((curr - open_t) / (open_t + 1e-9)) * 100
    stop = curr - (last_atr * 1.5) if signal == "C" else curr + (last_atr * 1.5) if signal == "P" else 0
    icon = "☀️" if (curr > sma20 and delta > 0.3) else "⚖️" if abs(delta) < 0.3 else "⛈️"
    spark_data = df['Close'].tail(20)
    spark_color = "#3fb950" if curr >= spark_data.iloc[0] else "#007bff"
    spark_img = create_sparkline(spark_data, spark_color)
    return {
        "display_name": name, "ticker": ticker, "price": curr, "delta": delta, "signal": signal, 
        "stop": stop, "icon": icon, "prob": calculate_probability(df, signal), 
        "rsi": rsi_val, "adx": adx_val, "sparkline": spark_img
    }

# --- 3. UI RENDERER ---
def render_row(res):
    if not res: return
    is_forex = ("=" in res['ticker'])
    fmt = "{:.6f}" if is_forex else "{:.2f}"
    st.markdown("<div class='row-container'>", unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns([1.2, 0.6, 0.8, 0.5, 1.1])
    with c1: st.markdown(f"**{res['display_name']}**<br><span style='color:#888; font-size:0.85rem;'>{fmt.format(res['price'])}</span>", unsafe_allow_html=True)
    with c2:
        color = "#3fb950" if res['delta'] >= 0 else "#007bff"
        st.markdown(f"<div style='text-align:center;'>{res['icon']}<br><span style='color:{color}; font-size:0.85rem;'>{res['delta']:+.2f}%</span></div>", unsafe_allow_html=True)
    with c3:
        rsi_c = "#ff4b4b" if res['rsi'] > 70 else "#3fb950" if res['rsi'] < 30 else "#888"
        adx_c = "#ffd700" if res['adx'] > 25 else "#888"
        st.markdown(f'<img src="data:image/png;base64,{res["sparkline"]}" width="110">', unsafe_allow_html=True)
        st.markdown(f"<span class='indicator-label'>RSI: <b style='color:{rsi_c};'>{res['rsi']:.1f}</b> | ADX: <b style='color:{adx_c};'>{res['adx']:.1f}</b></span>", unsafe_allow_html=True)
    with c4:
        if res['signal'] != "Wait":
            cls = "sig-box-high" if res['prob'] >= 60.0 else ("sig-box-c" if res['signal'] == "C" else "sig-box-p")
            st.markdown(f"<br><span class='{cls}'>{res['signal']}</span>", unsafe_allow_html=True)
        else: st.markdown("<br><span style='color:#444;'>-</span>", unsafe_allow_html=True)
    with c5:
        if res['stop'] != 0:
            prob_txt = f"<span style='color:#ffd700; font-weight:bold;'>{res['prob']:.1f}%</span>" if res['prob'] >= 60.0 else f"<span style='color:#888;'>({res['prob']:.1f}%)</span>"
            st.markdown(f"<span class='sl-label'>Stop-Loss</span> {prob_txt}<br><span class='sl-value'>{fmt.format(res['stop'])}</span>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- 4. MAIN APP ---
st.markdown("<div class='header-text'>📡 Dr. Gregor Bauer Strategie 📡</div>", unsafe_allow_html=True)
st.write(f"Update: {datetime.now().strftime('%H:%M:%S')} | Refresh: 60s")

with st.expander("ℹ️ Strategie-Leitfaden", expanded=False):
    st.markdown("""
    - **Trend-Chart:** Zeigt den Kursverlauf der **letzten 20 Handelstage**.
    - **Zustand:** ☀️ Bullish (>SMA20), ⚖️ Neutral, ⛈️ Bearish (<SMA20).
    - **Signale:** <span class='sig-box-c'>C</span> (Call), <span class='sig-box-p'>P</span> (Put). Gold ab 60% Trefferquote.
    """, unsafe_allow_html=True)

# --- 5. MACRO SECTION (Bitcoin entfernt) ---
st.markdown("<div class='header-text'>🌍 Macro + Indices 🌍</div>", unsafe_allow_html=True)
macro_list = ["EURUSD=X", "EURRUB=X", "^GDAXI", "^STOXX50E", "^IXIC", "XU100.IS", "^NSEI", "RTSI.ME"]
with ThreadPoolExecutor(max_workers=10) as executor:
    m_results = list(executor.map(fetch_data, macro_list))
    for r in m_results: render_row(r)

# --- 6. SCANNER SECTION (Mit Counter) ---
st.markdown("<br><div class='header-text'>🔭 Markt Screener 🔭</div>", unsafe_allow_html=True)
index_data = {
    "DAX 40": ["ADS.DE", "AIR.DE", "ALV.DE", "BAS.DE", "BAYN.DE", "BMW.DE", "CON.DE", "1COV.DE", "DTG.DE", "DTE.DE", "DBK.DE", "DB1.DE", "DHL.DE", "EON.DE", "FRE.DE", "FME.DE", "HEI.DE", "HEN3.DE", "IFX.DE", "MBG.DE", "MRK.DE", "MTX.DE", "MUV2.DE", "PUM.DE", "PAH3.DE", "RWE.DE", "SAP.DE", "SIE.DE", "SHL.DE", "SY1.DE", "TKA.DE", "VOW3.DE", "VNA.DE", "ZAL.DE"],
    "EuroStoxx 50": ["ASML.AS", "MC.PA", "OR.PA", "SAP.DE", "TTE.PA", "SIE.DE", "AIR.PA", "SAN.MC", "ITX.MC", "CS.PA"],
    "Nasdaq 100": ["AAPL", "MSFT", "NVDA", "AMZN", "TSLA", "GOOGL", "META", "AVGO", "COST", "NFLX"],
    "BIST 100": ["THYAO.IS", "TUPRS.IS", "AKBNK.IS", "ISCTR.IS", "EREGL.IS", "ASELS.IS", "KCHOL.IS", "SAHOL.IS"],
    "NIFTY 50": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS", "SBIN.NS", "BHARTIARTL.NS"]
}

if 'scan_active' not in st.session_state: st.session_state.scan_active = False
with st.expander("Index-Auswahl & Scan", expanded=True):
    col_sel, col_btn = st.columns(2)
    with col_sel: choice = st.radio("Markt:", list(index_data.keys()), horizontal=True)
    with col_btn:
        st.write("<br>", unsafe_allow_html=True)
        if st.button("🚀 Scan Start/Stop", use_container_width=True):
            st.session_state.scan_active = not st.session_state.scan_active

if st.session_state.scan_active:
    total_count = len(index_data[choice])
    st.markdown(f"<div class='scan-info'>Scanne {choice}... ({total_count} Werte insgesamt) | Zeige nur Signale.</div>", unsafe_allow_html=True)
    with ThreadPoolExecutor(max_workers=30) as executor:
        results = list(executor.map(fetch_data, index_data[choice]))
        signal_hits = [r for r in results if r is not None and r['signal'] != "Wait"]
        if signal_hits:
            st.success(f"{len(signal_hits)} Signale in {choice} gefunden.")
            for r in sorted(signal_hits, key=lambda x: (x['prob'] < 60.0, -x['prob'])): render_row(r)
        else: st.info(f"Keine Signale unter den {total_count} gescannten Werten.")
else: st.warning("Screener im Standby.")

# --- 7. BACKTESTING ---
st.markdown("---")
with st.expander("📈 Backtesting-Details (Fokus: DAX Schwergewicht SAP)"):
    sap_res = fetch_data("SAP.DE")
    if sap_res:
        st.write(f"Analyse für: **{sap_res['display_name']}**")
        c1, c2 = st.columns(2)
        c1.metric("Historische Prob.", f"{sap_res['prob']:.1f}%")
        c2.metric("Trendstärke (ADX)", f"{sap_res['adx']:.1f}")
