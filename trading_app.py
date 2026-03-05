import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# --- 0. AUTO-REFRESH & SETUP ---
try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    import os
    os.system('pip install streamlit-autorefresh')
    from streamlit_autorefresh import st_autorefresh

# Automatischer Refresh alle 45 Sekunden
st_autorefresh(interval=45000, key="datarefresh")

# --- 1. CONFIG & STYLING ---
st.set_page_config(layout="wide", page_title="Bauer Strategy Pro 2026", page_icon="📡")

st.markdown("""
    <style>
    .stApp { background-color: #050a0f; }
    h1, h2, h3, p, span, label, div { color: #e0e0e0 !important; font-family: 'Courier New', Courier, monospace; }
    .header-text { font-size: 24px; font-weight: bold; margin-bottom: 5px; display: flex; align-items: center; gap: 10px; }
    
    /* Signal Design: P = BLAU, C = GRÜN, HIGH = GOLD */
    .sig-box-p { color: #007bff !important; border: 1px solid #007bff !important; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
    .sig-box-c { color: #3fb950 !important; border: 1px solid #3fb950 !important; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
    .sig-box-high { color: #ffd700 !important; border: 1px solid #ffd700 !important; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
    
    .sl-label { color: #888; font-size: 0.85rem; }
    .sl-value { color: #e0e0e0; font-weight: bold; font-size: 1.1rem; }
    .kurs-label { color: #888; font-size: 0.85rem; }
    .row-container { border-bottom: 1px solid #1a202c; padding: 12px 0; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATEN-ENGINE ---
def calculate_probability(df, signal_type):
    if df is None or len(df) < 50: return 50.0
    bt_df = df.copy()
    bt_df['SMA20'] = bt_df['Close'].rolling(window=20).mean()
    hits, signals = 0, 0
    # Backtest über das letzte Jahr (ca. 250 Handelstage)
    for i in range(25, len(bt_df) - 5):
        c, p, p2 = bt_df['Close'].iloc[i], bt_df['Close'].iloc[i-1], bt_df['Close'].iloc[i-2]
        sma = bt_df['SMA20'].iloc[i]
        h_sig = "C" if (c > p > p2 and c > sma) else "P" if (c < p < p2 and c < sma) else None
        if h_sig == signal_type:
            signals += 1
            # Check: War der Kurs 3 Tage später im Profit?
            if (signal_type == "C" and bt_df['Close'].iloc[i+3] > c) or \
               (signal_type == "P" and bt_df['Close'].iloc[i+3] < c):
                hits += 1
    return (hits / signals * 100) if signals > 0 else 50.0

def fetch_data(ticker):
    try:
        t_obj = yf.Ticker(ticker)
        df = t_obj.history(period="1y", interval="1d", auto_adjust=True)
        if df.empty or len(df) < 25: return None
        
        display_name = t_obj.info.get('shortName') or ticker
        curr = float(df['Close'].iloc[-1])
        prev, prev2 = df['Close'].iloc[-2], df['Close'].iloc[-3]
        open_t = df['Open'].iloc[-1]
        sma20 = df['Close'].rolling(window=20).mean().iloc[-1]
        
        tr = pd.concat([df['High']-df['Low'], abs(df['High']-df['Close'].shift()), abs(df['Low']-df['Close'].shift())], axis=1).max(axis=1)
        atr = tr.rolling(window=14).mean().iloc[-1]
        
        signal = "C" if (curr > prev > prev2 and curr > sma20) else "P" if (curr < prev < prev2 and curr < sma20) else "Wait"
        delta = ((curr - open_t) / open_t) * 100
        stop = curr - (atr * 1.5) if signal == "C" else curr + (atr * 1.5) if signal == "P" else 0
        icon = "☀️" if (curr > sma20 and delta > 0.3) else "⚖️" if abs(delta) < 0.3 else "⛈️"
        
        return {
            "display_name": display_name, "ticker": ticker, "price": curr, 
            "delta": delta, "signal": signal, "stop": stop, "icon": icon, 
            "prob": calculate_probability(df, signal)
        }
    except: return None

# --- 3. UI RENDERER ---
def render_row(res):
    if not res: return
    is_forex = ("=" in res['ticker'])
    fmt = "{:.6f}" if is_forex else "{:.2f}"
    st.markdown("<div class='row-container'>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns([1.2, 0.6, 0.5, 1.2])
    
    with c1:
        st.markdown(f"**{res['display_name']}**<br><span class='kurs-label'>Kurs: {fmt.format(res['price'])}</span>", unsafe_allow_html=True)
    with c2:
        color = "#3fb950" if res['delta'] >= 0 else "#007bff"
        st.markdown(f"<div style='text-align:center;'>{res['icon']}<br><span style='color:{color} !important; font-size:0.85rem;'>{res['delta']:+.2f}%</span></div>", unsafe_allow_html=True)
    
    with c3:
        if res['signal'] != "Wait":
            cls = "sig-box-high" if res['prob'] >= 60.0 else ("sig-box-c" if res['signal'] == "C" else "sig-box-p")
            st.markdown(f"<br><span class='{cls}'>{res['signal']}</span>", unsafe_allow_html=True)
        else: 
            st.markdown(f"<br><span style='color:#444;'>{res['signal']}</span>", unsafe_allow_html=True)
            
    with c4:
        if res['stop'] != 0:
            if res['prob'] >= 60.0:
                prob_txt = f"<span style='color:#ffd700 !important; font-weight:bold; font-size:1.0rem;'>{res['prob']:.1f}%</span>"
            else:
                prob_txt = f"<span style='color:#888 !important;'>({res['prob']:.1f}%)</span>"
            st.markdown(f"<span class='sl-label'>Stop-Loss</span> {prob_txt}<br><span class='sl-value'>{fmt.format(res['stop'])}</span>", unsafe_allow_html=True)
        else: 
            st.markdown("<span class='sl-label'>Stop-Loss</span><br><span style='color:#444;'>---</span>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- 4. MAIN APP ---
st.markdown("<div class='header-text'>📡 Dr. Gregor Bauer Strategie Pro</div>", unsafe_allow_html=True)
st.write(f"Update: {datetime.now().strftime('%H:%M:%S')} | Auto-Refresh: 45s")

with st.expander("ℹ️ Strategie-Leitfaden & Markt-Symbole", expanded=False):
    st.markdown("""
    **1. Markt-Zustand:** ☀️ Bullish | ⚖️ Neutral | ⛈️ Bearish  
    **2. Signale:** <span style='color:#3fb950;'>C</span> (Call/Long) | <span style='color:#007bff;'>P</span> (Put/Short)  
    **3. Gold-Logik:** Trefferquoten <span style='color:#ffd700; font-weight:bold;'>≥ 60,0%</span> (Backtest 12 Monate) werden gelb markiert.
    """, unsafe_allow_html=True)

# MACRO
st.markdown("<div class='header-text'>🌍 Macro & Indices</div>", unsafe_allow_html=True)
macro_tickers = ["EURUSD=X", "^GDAXI", "^STOXX50E", "^IXIC", "XU100.IS", "^NSEI"]
for t in macro_tickers:
    res = fetch_data(t)
    if res: render_row(res)

# SCANNER
st.markdown("<br><div class='header-text'>🔭 Market Scanner</div>", unsafe_allow_html=True)

index_data = {
    "DAX 40": [
        "ADS.DE", "AIR.DE", "ALV.DE", "BAS.DE", "BAYN.DE", "BEI.DE", "BMW.DE", "CON.DE", "1COV.DE", "DTG.DE", 
        "DTE.DE", "DB1.DE", "DBK.DE", "EON.DE", "FME.DE", "FRE.DE", "HLAG.DE", "HEN3.DE", "IFX.DE", "MBG.DE", 
        "MRK.DE", "MTX.DE", "MUV2.DE", "PAH3.DE", "PUM.DE", "RWE.DE", "SAP.DE", "SRT3.DE", "SIE.DE", "SHL.DE", 
        "SY1.DE", "TKA.DE", "VOW3.DE", "VNA.DE", "ZAL.DE"
    ],
    "EuroStoxx 50": [
        "ASML.AS", "MC.PA", "OR.PA", "SAP.DE", "TTE.PA", "SIE.DE", "AIR.PA", "SAN.MC", "EL.PA", "IBE.MC", 
        "BNP.PA", "ITX.MC", "BBVA.MC", "BAS.DE", "ALV.DE", "BMW.DE", "BAYN.DE", "ADS.DE", "DTE.DE", "IFX.DE", 
        "MBG.DE", "MUV2.DE", "RWE.DE", "VOW3.DE", "ABI.BR", "ENI.MI", "ISP.MI", "CS.PA", "DG.PA", "SGO.PA"
    ],
    "Nasdaq 100 Top": [
        "AAPL", "MSFT", "NVDA", "AMZN", "TSLA", "GOOGL", "GOOG", "META", "AVGO", "PEP", "COST", "ADBE", 
        "CSCO", "NFLX", "AMD", "CMCSA", "TMUS", "INTC", "INTU", "AMAT", "QCOM", "TXN", "AMGN", "HON", 
        "ISRG", "BKNG", "VRTX", "SBUX", "ADP", "GILD", "MDLZ", "REGN", "PYPL", "ADI", "MU", "PANW"
    ],
    "BIST 100": ["THYAO.IS", "TUPRS.IS", "AKBNK.IS", "ISCTR.IS", "EREGL.IS", "ASELS.IS", "KCHOL.IS", "SAHOL.IS"],
    "NIFTY 50": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS", "HINDUNILVR.NS", "SBIN.NS"]
}

with st.expander("Index-Auswahl & Scan", expanded=True):
    col_sel, col_btn = st.columns([3, 1])
    if 'scan_active' not in st.session_state: st.session_state.scan_active = False
    with col_sel:
        choice = st.radio("Index:", list(index_data.keys()), horizontal=True)
    with col_btn:
        st.write("<br>", unsafe_allow_html=True)
        if st.button("🚀 Scan Start/Stop", use_container_width=True):
            st.session_state.scan_active = not st.session_state.scan_active

if st.session_state.scan_active:
    st.info(f"Scan läuft für {len(index_data[choice])} Aktien...")
    # Erhöhte Anzahl an Workers für schnellere Abfrage der großen Listen
    with ThreadPoolExecutor(max_workers=30) as executor:
        results = list(executor.map(fetch_data, index_data[choice]))
        # Sortierung: Signale zuerst, dann nach Wahrscheinlichkeit
        valid_results = sorted([r for r in results if r is not None], 
                               key=lambda x: (x['signal'] == "Wait", -x['prob']))
        for r in valid_results: render_row(r)
else:
    st.warning("Scanner im Standby.")
