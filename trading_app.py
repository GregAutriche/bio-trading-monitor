import os
import sys

# --- 1. MATPLOTLIB FIX (Muss ganz oben stehen) ---
import matplotlib
matplotlib.use('Agg') 
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

# --- 2. SETUP & REFRESH ---
st_autorefresh(interval=60000, key="datarefresh")
st.set_page_config(layout="wide", page_title="Bauer Strategy Pro 2026", page_icon="📡")

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
    .scan-info { color: #ffd700; font-style: italic; font-size: 0.9rem; margin-bottom: 10px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNKTIONEN ---
def create_sparkline(data, color):
    fig, ax = plt.subplots(figsize=(2.5, 0.6), dpi=70)
    ax.plot(data.values, color=color, linewidth=2.5)
    ax.axis('off')
    buf = io.BytesIO()
    fig.savefig(buf, format='png', transparent=True, bbox_inches='tight', pad_inches=0)
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode()

@st.cache_data(ttl=300)
def fetch_data(ticker):
    try:
        t_obj = yf.Ticker(ticker)
        df = t_obj.history(period="1y", interval="1d", auto_adjust=True)
        if df.empty or len(df) < 35: return None
        
        # Indikatoren
        delta_p = df['Close'].diff()
        gain = (delta_p.where(delta_p > 0, 0)).rolling(window=14).mean()
        loss = (-delta_p.where(delta_p < 0, 0)).rolling(window=14).mean()
        rs = gain / (loss + 1e-9)
        rsi = 100 - (100 / (1 + rs))
        
        tr = pd.concat([df['High']-df['Low'], abs(df['High']-df['Close'].shift()), abs(df['Low']-df['Close'].shift())], axis=1).max(axis=1)
        atr = tr.rolling(window=14).mean().iloc[-1]
        adx = (abs(df['High'].diff() - abs(df['Low'].diff())) / (tr + 1e-9)).rolling(window=14).mean().iloc[-1] * 100
        
        curr = float(df['Close'].iloc[-1])
        prev, prev2 = df['Close'].iloc[-2], df['Close'].iloc[-3]
        sma20 = df['Close'].rolling(window=20).mean().iloc[-1]
        
        signal = "C" if (curr > prev > prev2 and curr > sma20) else "P" if (curr < prev < prev2 and curr < sma20) else "Wait"
        
        # Wahrscheinlichkeit (Backtest 100 Tage)
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
            "prob": prob, "rsi": rsi.iloc[-1], "adx": adx, "spark": spark_img, 
            "icon": "☀️" if (curr > sma20 and ((curr - df['Open'].iloc[-1]) / df['Open'].iloc[-1]) * 100 > 0.3) else "⚖️" if abs(((curr - df['Open'].iloc[-1]) / df['Open'].iloc[-1]) * 100) < 0.3 else "⛈️"
        }
    except: return None

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

# --- 4. UI MAIN ---
st.markdown("<div class='header-text'>📡 Dr. Gregor Bauer Strategie 📡</div>", unsafe_allow_html=True)
st.write(f"Update: {datetime.now().strftime('%H:%M:%S')} | Refresh: 60s")

with st.expander("ℹ️ Strategie-Leitfaden + Markt-Symbole", expanded=False):
    st.markdown("""
    - **Trend-Chart:** Kursverlauf der **letzten 20 Handelstage**.
    - **Zustand:** ☀️ Bullish (>SMA20 & >0,3%), ⚖️ Neutral, ⛈️ Bearish.
    - **Logik:** <span class='sig-box-c'>C</span> (Call), <span class='sig-box-p'>P</span> (Put). Gold ab 60% Wahrscheinlichkeit.
    """)

# --- 5. MACRO ---
st.markdown("<div class='header-text'>🌍 Macro + Indices 🌍</div>", unsafe_allow_html=True)
macro_list = ["EURUSD=X", "EURRUB=X", "^GDAXI", "^STOXX50E", "^IXIC", "XU100.IS", "^NSEI", "RTSI.ME"]
with ThreadPoolExecutor(max_workers=10) as ex:
    m_res = [r for r in ex.map(fetch_data, macro_list) if r]
    for r in m_res: render_row(r)

# --- 6. SCREENER ---
index_data = {
    "DAX 40": ["ADS.DE", "AIR.DE", "ALV.DE", "BAS.DE", "BAYN.DE", "BMW.DE", "CON.DE", "1COV.DE", "DTG.DE", "DTE.DE", "DBK.DE", "DB1.DE", "DHL.DE", "EON.DE", "FRE.DE", "FME.DE", "HEI.DE", "HEN3.DE", "IFX.DE", "MBG.DE", "MRK.DE", "MTX.DE", "MUV2.DE", "PUM.DE", "PAH3.DE", "RWE.DE", "SAP.DE", "SIE.DE", "SHL.DE", "SY1.DE", "TKA.DE", "VOW3.DE", "VNA.DE", "ZAL.DE", "BEI.DE", "CBK.DE", "RHM.DE"],
    "EuroStoxx 50": ["ASML.AS", "MC.PA", "OR.PA", "SAP.DE", "TTE.PA", "SIE.DE", "AIR.PA", "SAN.MC", "ITX.MC", "CS.PA", "BNP.PA", "IBE.MC", "SU.PA", "ADYEN.AS", "EL.PA", "BAS.DE"],
    "Nasdaq 100": ["AAPL", "MSFT", "NVDA", "AMZN", "TSLA", "GOOGL", "META", "AVGO", "COST", "NFLX", "ADBE", "AMD", "PEP", "INTC", "CSCO"],
    "BIST 100": ["THYAO.IS", "TUPRS.IS", "AKBNK.IS", "ISCTR.IS", "EREGL.IS", "ASELS.IS", "KCHOL.IS", "SAHOL.IS", "BIMAS.IS", "ARCLK.IS", "SISE.IS"],
    "NIFTY 50": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS", "SBIN.NS", "BHARTIARTL.NS", "AXISBANK.NS", "LT.NS"]
}

st.markdown("<br><div class='header-text'>🔭 Markt Screener 🔭</div>", unsafe_allow_html=True)
if 'scan_active' not in st.session_state: st.session_state.scan_active = False

with st.expander("Index-Auswahl & Scan", expanded=True):
    col_sel, col_btn = st.columns(2)
    with col_sel: choice = st.radio("Markt:", list(index_data.keys()), horizontal=True)
    with col_btn:
        st.write("<br>", unsafe_allow_html=True)
        if st.button("🚀 Scan Start/Stop", use_container_width=True):
            st.session_state.scan_active = not st.session_state.scan_active

if st.session_state.scan_active:
    tickers = index_data[choice]
    total = len(tickers)
    st.markdown(f"<div class='scan-info'>Scanne {choice}... ({total} Werte insgesamt) | Zeige nur Signale.</div>", unsafe_allow_html=True)
    
    with ThreadPoolExecutor(max_workers=30) as ex:
        results = [r for r in ex.map(fetch_data, tickers) if r]
        
    if len(results) >= (total * 0.8):
        hits = [r for r in results if r['signal'] != "Wait"]
        st.success(f"{len(hits)} Signale in {choice} gefunden ({len(results)}/{total} geladen).")
        for r in sorted(hits, key=lambda x: -x['prob']): render_row(r)
    else:
        st.warning(f"⏳ Warte auf Daten... ({len(results)}/{total} geladen)")
else:
    st.warning("Scanner im Standby.")

# --- 7. BACKTESTING ---
st.markdown("---")
with st.expander("📈 Backtesting-Details (Beispiel SAP)"):
    sap_res = fetch_data("SAP.DE")
    if sap_res:
        st.write(f"Analyse für: **{sap_res['name']}**")
        c1, c2 = st.columns(2)
        c1.metric("Trefferwahrscheinlichkeit", f"{sap_res['prob']:.1f}%")
        c2.metric("Trendstärke (ADX)", f"{sap_res['adx']:.1f}")
