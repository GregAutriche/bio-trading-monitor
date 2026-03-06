import os
import sys

# --- 1. MATPLOTLIB BACKEND FIX (Muss VOR pyplot importiert werden) ---
import matplotlib
matplotlib.use('Agg') # Verhindert den "raise Done" Fehler in der Cloud
import matplotlib.pyplot as plt

# --- AUTO-INSTALLER ---
def install_and_import(package):
    try:
        __import__(package.replace('-', '_'))
    except ImportError:
        os.system(f"{sys.executable} -m pip install {package}")

install_and_import('streamlit-autorefresh')

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import base64
import io
from streamlit_autorefresh import st_autorefresh

# --- 2. SETUP ---
st_autorefresh(interval=60000, key="datarefresh")
st.set_page_config(layout="wide", page_title="Bauer Strategy Pro 2026", page_icon="📡")

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
    .scan-info { color: #ffd700; font-style: italic; font-size: 0.9rem; margin-bottom: 10px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. CORE ENGINE ---
def create_sparkline(data, color):
    fig, ax = plt.subplots(figsize=(2.5, 0.6), dpi=70) # Explizite Figure-Erstellung
    ax.plot(data.values, color=color, linewidth=2.5)
    ax.axis('off')
    buf = io.BytesIO()
    fig.savefig(buf, format='png', transparent=True, bbox_inches='tight', pad_inches=0)
    plt.close(fig) # Wichtig: Speicher freigeben
    return base64.b64encode(buf.getvalue()).decode()

@st.cache_data(ttl=300)
def fetch_data(ticker):
    try:
        t_obj = yf.Ticker(ticker)
        df = t_obj.history(period="1y", interval="1d", auto_adjust=True)
        if df.empty or len(df) < 35: return None
        
        # Indikatoren
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / (loss + 1e-9)
        rsi = 100 - (100 / (1 + rs))
        
        tr = pd.concat([df['High']-df['Low'], abs(df['High']-df['Close'].shift()), abs(df['Low']-df['Close'].shift())], axis=1).max(axis=1)
        atr = tr.rolling(window=14).mean().iloc[-1]
        adx = (abs(df['High'].diff() - abs(df['Low'].diff())) / (tr + 1e-9)).rolling(window=14).mean().iloc[-1] * 100
        
        curr = float(df['Close'].iloc[-1])
        prev, prev2 = df['Close'].iloc[-2], df['Close'].iloc[-3]
        sma20 = df['Close'].rolling(window=20).mean().iloc[-1]
        
        signal = "C" if (curr > prev > prev2 and curr > sma20) else "P" if (curr < prev < prev2 and curr < sma20) else "Wait"
        
        # Wahrscheinlichkeit
        bt_df = df.tail(100).copy()
        bt_df['SMA20'] = bt_df['Close'].rolling(window=20).mean()
        hits, sigs = 0, 0
        for i in range(20, len(bt_df)-3):
            c_h, p_h, p2_h = bt_df['Close'].iloc[i], bt_df['Close'].iloc[i-1], bt_df['Close'].iloc[i-2]
            if signal == "C" and (c_h > p_h > p2_h and c_h > bt_df['SMA20'].iloc[i]):
                sigs += 1
                if bt_df['Close'].iloc[i+3] > c_h: hits += 1
            elif signal == "P" and (c_h < p_h < p2_h and c_h < bt_df['SMA20'].iloc[i]):
                sigs += 1
                if bt_df['Close'].iloc[i+3] < c_h: hits += 1
        prob = (hits / sigs * 100) if sigs > 0 else 50.0

        spark_img = create_sparkline(df['Close'].tail(20), "#3fb950" if curr >= df['Close'].iloc[-2] else "#007bff")
        
        return {
            "name": t_obj.info.get('shortName') or ticker, "ticker": ticker, "price": curr, 
            "delta": ((curr - df['Open'].iloc[-1]) / df['Open'].iloc[-1]) * 100,
            "signal": signal, "stop": curr - (atr*1.5) if signal=="C" else curr + (atr*1.5) if signal=="P" else 0,
            "prob": prob, "rsi": rsi.iloc[-1], "adx": adx, "spark": spark_img, "icon": "☀️" if curr > sma20 else "⛈️"
        }
    except: return None

# --- 4. UI ---
def render_row(res):
    fmt = "{:.6f}" if "=" in res['ticker'] else "{:.2f}"
    st.markdown("<div class='row-container'>", unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns([1.2, 0.6, 0.8, 0.5, 1.1])
    with c1: st.markdown(f"**{res['name']}**<br><small>{fmt.format(res['price'])}</small>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div style='text-align:center;'>{res['icon']}<br><span style='color:{'#3fb950' if res['delta']>=0 else '#007bff'};'>{res['delta']:+.2f}%</span></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f'<img src="data:image/png;base64,{res["spark"]}" width="100">', unsafe_allow_html=True)
        st.markdown(f"<span class='indicator-label'>RSI: {res['rsi']:.1f} | ADX: {res['adx']:.1f}</span>", unsafe_allow_html=True)
    with c4:
        if res['signal'] != "Wait":
            cls = "sig-box-high" if res['prob'] >= 60 else ("sig-box-c" if res['signal']=="C" else "sig-box-p")
            st.markdown(f"<br><span class='{cls}'>{res['signal']}</span>", unsafe_allow_html=True)
    with c5:
        if res['stop'] != 0:
            st.markdown(f"<small>SL ({res['prob']:.1f}%)</small><br><b>{fmt.format(res['stop'])}</b>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- 5. MAIN ---
st.markdown("<div class='header-text'>📡 Dr. Gregor Bauer Strategie 📡</div>", unsafe_allow_html=True)

# Macro
macro_list = ["EURUSD=X", "EURRUB=X", "^GDAXI", "^STOXX50E", "^IXIC", "XU100.IS", "RTSI.ME"]
with ThreadPoolExecutor(max_workers=10) as ex:
    m_res = [r for r in ex.map(fetch_data, macro_list) if r]
    for r in m_res: render_row(r)

# Scanner
index_data = {
    "DAX 40": ["ADS.DE", "AIR.DE", "ALV.DE", "BAS.DE", "BAYN.DE", "BMW.DE", "CON.DE", "1COV.DE", "DTG.DE", "DTE.DE", "DBK.DE", "DB1.DE", "DHL.DE", "EON.DE", "FRE.DE", "FME.DE", "HEI.DE", "HEN3.DE", "IFX.DE", "MBG.DE", "MRK.DE", "MTX.DE", "MUV2.DE", "PUM.DE", "PAH3.DE", "RWE.DE", "SAP.DE", "SIE.DE", "SHL.DE", "SY1.DE", "TKA.DE", "VOW3.DE", "VNA.DE", "ZAL.DE", "BEI.DE", "CBK.DE", "RHM.DE"],
    "Nasdaq 100": ["AAPL", "MSFT", "NVDA", "AMZN", "TSLA", "GOOGL", "META", "AVGO", "COST", "NFLX"]
}

st.markdown("<br><div class='header-text'>🔭 Markt Screener 🔭</div>", unsafe_allow_html=True)
choice = st.radio("Markt:", list(index_data.keys()), horizontal=True)

if st.button("🚀 Scan Start/Stop"):
    tickers = index_data[choice]
    total = len(tickers)
    with ThreadPoolExecutor(max_workers=20) as ex:
        results = [r for r in ex.map(fetch_data, tickers) if r]
        
    # Korrigierte Zähl-Logik (80% Check)
    if len(results) >= (total * 0.8):
        hits = [r for r in results if r['signal'] != "Wait"]
        st.success(f"Scan abgeschlossen: {len(results)} von {total} Werten erfolgreich geladen.")
        for r in sorted(hits, key=lambda x: -x['prob']): render_row(r)
    else:
        st.warning(f"Warte auf Daten... ({len(results)}/{total} geladen)")
