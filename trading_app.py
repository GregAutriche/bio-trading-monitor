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

st_autorefresh(interval=45000, key="datarefresh")

# --- 1. CONFIG & STYLING ---
st.set_page_config(layout="wide", page_title="Bauer Strategy Pro 2026", page_icon="📡")

st.markdown("""
    <style>
    .stApp { background-color: #050a0f; }
    h1, h2, h3, p, span, label, div { color: #e0e0e0 !important; font-family: 'Courier New', Courier, monospace; }
    
    .row-container { border-bottom: 1px solid #1a202c; padding: 2px 0px !important; margin: 0px !important; line-height: 1.2 !important; }
    .stock-title { font-weight: bold; font-size: 1.05rem; display: block; }
    .kurs-label { color: #e0e0e0 !important; font-weight: normal; font-size: 1.05rem; }
    .indicator-label { color: #666; font-size: 0.75rem; margin-top: 1px; }
    .sig-box-p { color: #007bff !important; border: 1px solid #007bff !important; padding: 1px 5px; border-radius: 3px; font-weight: bold; font-size: 0.85rem; }
    .sig-box-c { color: #3fb950 !important; border: 1px solid #3fb950 !important; padding: 1px 5px; border-radius: 3px; font-weight: bold; font-size: 0.85rem; }
    .sig-box-high { color: #ffd700 !important; border: 1px solid #ffd700 !important; padding: 1px 5px; border-radius: 3px; font-weight: bold; font-size: 0.85rem; }
    .header-text { font-size: 18px; font-weight: bold; margin-top: 5px; color: #ffd700 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATEN-ENGINE ---
@st.cache_data(ttl=300)
def get_historical_data(ticker):
    try:
        t_obj = yf.Ticker(ticker)
        df = t_obj.history(period="1y", interval="1d", auto_adjust=True)
        return df, t_obj.info.get('shortName') or ticker
    except: return None, None

def calculate_indicators(df):
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss.replace(0, np.nan)
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # NEU: ROC (Rate of Change) statt ADX für schnellere Reaktion
    df['ROC'] = ((df['Close'] - df['Close'].shift(14)) / df['Close'].shift(14)) * 100
    
    tr = pd.concat([df['High']-df['Low'], abs(df['High']-df['Close'].shift()), abs(df['Low']-df['Close'].shift())], axis=1).max(axis=1)
    atr = tr.rolling(window=14).mean()
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
    if df is None or df.empty: return None
    df, last_atr = calculate_indicators(df)
    curr = float(df['Close'].iloc[-1]); prev = df['Close'].iloc[-2]; prev2 = df['Close'].iloc[-3]
    open_t = df['Open'].iloc[-1]; sma20 = df['Close'].rolling(window=20).mean().iloc[-1]
    
    signal = "C" if (curr > prev > prev2 and curr > sma20) else "P" if (curr < prev < prev2 and curr < sma20) else "Wait"
    delta = ((curr - open_t) / open_t) * 100
    stop = curr - (last_atr * 1.5) if signal == "C" else curr + (last_atr * 1.5) if signal == "P" else 0
    return {
        "display_name": name, "ticker": ticker, "price": curr, "delta": delta, 
        "signal": signal, "stop": stop, "prob": calculate_probability(df, signal), 
        "rsi": df['RSI'].iloc[-1], "roc": df['ROC'].iloc[-1]
    }

# --- 3. UI RENDERER ---
def render_row(res):
    fmt = "{:.6f}" if ("=" in res['ticker']) else "{:.2f}"
    st.markdown("<div class='row-container'>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns([1.8, 0.6, 0.6, 1.8])
    
    with c1:
        rsi_c = "#3fb950" if res['rsi'] < 35 else "#ff4b4b" if res['rsi'] > 65 else "#888"
        roc_c = "#3fb950" if res['roc'] > 0 else "#ff4b4b"
        st.markdown(f"""<span class='stock-title'>{res['display_name']}</span>
            <span class='kurs-label'>K: {fmt.format(res['price'])}</span><br>
            <span class='indicator-label'>RSI: <b style='color:{rsi_c};'>{res['rsi']:.1f}</b> | ROC: <b style='color:{roc_c};'>{res['roc']:+.1f}%</b></span>
        """, unsafe_allow_html=True)
    with c2:
        color = "#3fb950" if res['delta'] >= 0 else "#007bff"
        st.markdown(f"<div style='text-align:center; margin-top:5px;'><span style='color:{color} !important; font-size:0.85rem;'>{res['delta']:+.2f}%</span></div>", unsafe_allow_html=True)
    with c3:
        if res['signal'] != "Wait":
            cls = "sig-box-high" if res['prob'] >= 60.0 else ("sig-box-c" if res['signal'] == "C" else "sig-box-p")
            st.markdown(f"<div style='margin-top:10px; text-align:center;'><span class='{cls}'>{res['signal']}</span></div>", unsafe_allow_html=True)
    with c4:
        if res['stop'] != 0:
            p_c = "#ffd700" if res['prob'] >= 60.0 else "#666"
            st.markdown(f"<div style='text-align:right;'><span class='sl-label'>SL</span> <b style='color:{p_c};'>{res['prob']:.1f}%</b><br><span class='sl-value'>{fmt.format(res['stop'])}</span></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- 4. MAIN APP ---
st.markdown("<div class='header-text'>📡 Dr. Gregor Bauer Strategie Pro 2026</div>", unsafe_allow_html=True)

# KORRIGIERTE BESCHREIBUNG: Fester dunkler Hintergrund für Lesbarkeit
with st.expander("ℹ️ DETAILLIERTE STRATEGIE-BESCHREIBUNG", expanded=False):
    st.markdown("""
    <div style='background-color: #0d1117; padding: 15px; border-radius: 8px; border: 1px solid #30363d;'>
        <p style='color: #ffffff !important; margin-bottom: 8px;'><strong>1. Bauer-Signal:</strong> Momentum-Bestätigung über SMA20 mit 3-Tage-Muster.</p>
        <p style='color: #ffffff !important; margin-bottom: 8px;'><strong>2. Filter:</strong> 
            <span style='color:#3fb950;'>RSI < 35</span> (Kaufchance), 
            <span style='color:#ff4b4b;'>RSI > 65</span> (Gefahr). 
            ROC zeigt die Kursgeschwindigkeit an.</p>
        <p style='color: #ffffff !important;'><strong>3. Gold-Logik:</strong> Signale mit Trefferquote <b style='color:#ffd700;'>≥ 60%</b> werden gelb markiert.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div class='header-text'>🌍 Macro & Indices</div>", unsafe_allow_html=True)
macro_tickers = ["EURUSD=X", "^GDAXI", "^STOXX50E", "^IXIC"]
for t in macro_tickers:
    res = fetch_data(t); render_row(res) if res else None

st.markdown("<br><div class='header-text'>🔭 Market Scanner</div>", unsafe_allow_html=True)
index_data = {
    "DAX 40": ["ADS.DE", "ALV.DE", "BAS.DE", "BMW.DE", "SAP.DE", "SIE.DE", "VOW3.DE"],
    "Nasdaq 100": ["AAPL", "MSFT", "NVDA", "AMZN", "TSLA", "GOOGL", "META"]
}

col_sel, col_btn = st.columns(2)
if 'scan_active' not in st.session_state: st.session_state.scan_active = False
with col_sel: choice = st.radio("Markt:", list(index_data.keys()), horizontal=True)
with col_btn:
    st.write("<br>", unsafe_allow_html=True)
    if st.button("🚀 Scan Start/Stop", use_container_width=True):
        st.session_state.scan_active = not st.session_state.scan_active

if st.session_state.scan_active:
    with ThreadPoolExecutor(max_workers=30) as executor:
        results = list(executor.map(fetch_data, index_data[choice]))
        hits = sorted([r for r in results if r and r['signal'] != "Wait"], key=lambda x: (x['prob'] < 60.0, -x['prob']))
        for r in hits: render_row(r)
