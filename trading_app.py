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
    
    /* RADIKALE KOMPRIMIERUNG */
    [data-testid="stVerticalBlock"] {
        gap: 0rem !important;
    }
    
    [data-testid="stVerticalBlock"] > div {
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
        margin-top: -2px !important; /* Zieht Zeilen aktiv zusammen */
        margin-bottom: 0px !important;
    }

    .row-container { 
        border-bottom: 1px solid #1a202c; 
        padding: 0px !important; 
        margin: 0px !important; 
        line-height: 0.9 !important; /* Extrem eng */
    }
    
    .stock-title { font-weight: bold; font-size: 1.0rem; display: block; margin: 0; }
    .kurs-label { color: #e0e0e0 !important; font-weight: normal; font-size: 1.0rem; margin: 0; }
    .indicator-label { color: #555; font-size: 0.65rem; margin: 0; line-height: 0.8; }
    .sl-label { color: #777; font-size: 0.65rem; }
    .sl-value { color: #e0e0e0; font-weight: bold; font-size: 0.9rem; }

    .sig-box-p { color: #007bff !important; border: 1px solid #007bff !important; padding: 0px 3px; border-radius: 2px; font-weight: bold; font-size: 0.75rem; }
    .sig-box-c { color: #3fb950 !important; border: 1px solid #3fb950 !important; padding: 0px 3px; border-radius: 2px; font-weight: bold; font-size: 0.75rem; }
    .sig-box-high { color: #ffd700 !important; border: 1px solid #ffd700 !important; padding: 0px 3px; border-radius: 2px; font-weight: bold; font-size: 0.75rem; }
    
    .header-text { font-size: 16px; font-weight: bold; margin-top: 2px; margin-bottom: 0px; color: #ffd700 !important; }
    
    /* Scrollbar Styling für Kompaktansicht */
    ::-webkit-scrollbar { width: 5px; height: 5px; }
    ::-webkit-scrollbar-thumb { background: #1a202c; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATEN-ENGINE ---
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
    rs = gain / loss.replace(0, np.nan)
    df['RSI'] = 100 - (100 / (1 + rs))
    
    plus_dm = df['High'].diff()
    minus_dm = df['Low'].diff()
    plus_dm[plus_dm < 0] = 0; minus_dm[minus_dm > 0] = 0
    tr = pd.concat([df['High']-df['Low'], abs(df['High']-df['Close'].shift()), abs(df['Low']-df['Close'].shift())], axis=1).max(axis=1)
    atr = tr.rolling(window=14).mean()
    
    diff = (plus_dm + abs(minus_dm))
    adx_raw = (abs(plus_dm - abs(minus_dm)) / diff.replace(0, np.nan))
    df['ADX'] = adx_raw.rolling(window=14).mean() * 100
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
    curr = float(df['Close'].iloc[-1]); prev = df['Close'].iloc[-2]; prev2 = df['Close'].iloc[-3]
    open_t = df['Open'].iloc[-1]; sma20 = df['Close'].rolling(window=20).mean().iloc[-1]
    rsi_val = df['RSI'].iloc[-1]; adx_val = df['ADX'].iloc[-1]
    
    signal = "C" if (curr > prev > prev2 and curr > sma20) else "P" if (curr < prev < prev2 and curr < sma20) else "Wait"
    delta = ((curr - open_t) / open_t) * 100
    stop = curr - (last_atr * 1.5) if signal == "C" else curr + (last_atr * 1.5) if signal == "P" else 0
    icon = "☀️" if (curr > sma20 and delta > 0.3) else "⚖️" if abs(delta) < 0.3 else "⛈️"
    
    return {
        "display_name": name, "ticker": ticker, "price": curr, "delta": delta, 
        "signal": signal, "stop": stop, "icon": icon, "prob": calculate_probability(df, signal), 
        "rsi": rsi_val, "adx": adx_val
    }

# --- 3. UI RENDERER ---
def render_row(res):
    fmt = "{:.6f}" if ("=" in res['ticker']) else "{:.2f}"
    st.markdown("<div class='row-container'>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns([2.0, 0.5, 0.5, 2.0]) # Spalten breiter für Text
    
    with c1:
        rsi_c = "#3fb950" if res['rsi'] < 30 else "#ff4b4b" if res['rsi'] > 70 else "#555"
        adx_c = "#ffd700" if (not np.isnan(res['adx']) and res['adx'] > 25) else "#555"
        adx_txt = f"{res['adx']:.1f}" if not np.isnan(res['adx']) else "---"
        st.markdown(f"<span class='stock-title'>{res['display_name']}</span><span class='kurs-label'>K: {fmt.format(res['price'])}</span><br><span class='indicator-label'>RSI: <b style='color:{rsi_c};'>{res['rsi']:.1f}</b> | ADX: <b style='color:{adx_c};'>{adx_txt}</b></span>", unsafe_allow_html=True)
    with c2:
        color = "#3fb950" if res['delta'] >= 0 else "#007bff"
        st.markdown(f"<div style='text-align:center;'>{res['icon']}<br><span style='color:{color} !important; font-size:0.7rem;'>{res['delta']:+.2f}%</span></div>", unsafe_allow_html=True)
    with c3:
        if res['signal'] != "Wait":
            cls = "sig-box-high" if res['prob'] >= 60.0 else ("sig-box-c" if res['signal'] == "C" else "sig-box-p")
            st.markdown(f"<div style='margin-top:2px; text-align:center;'><span class='{cls}'>{res['signal']}</span></div>", unsafe_allow_html=True)
        else: st.markdown(f"<div style='margin-top:2px; text-align:center; color:#222;'>---</div>", unsafe_allow_html=True)
    with c4:
        if res['stop'] != 0:
            p_c = "#ffd700" if res['prob'] >= 60.0 else "#555"
            st.markdown(f"<div style='text-align:right;'><span class='sl-label'>SL</span> <b style='color:{p_c};'>{res['prob']:.1f}%</b><br><span class='sl-value'>{fmt.format(res['stop'])}</span></div>", unsafe_allow_html=True)
        else: st.markdown("<div style='text-align:right; margin-top:2px; color:#222;'>---</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- 4. MAIN APP ---
st.markdown("<div class='header-text'>📡 Dr. Gregor Bauer Strategie Pro</div>", unsafe_allow_html=True)

with st.expander("ℹ️ INFO", expanded=False):
    st.write("Bauer-Momentum via SMA20 | RSI < 30 (Kauf) / > 70 (Verkauf) | Gold ≥ 60%")

st.markdown("<div class='header-text'>🌍 Macro & Indices</div>", unsafe_allow_html=True)
macro_tickers = ["EURUSD=X", "^GDAXI", "^STOXX50E", "^IXIC", "XU100.IS", "^NSEI"]
for t in macro_tickers:
    res = fetch_data(t)
    if res: render_row(res)

st.markdown("<div class='header-text' style='margin-top:10px;'>🔭 Market Scanner</div>", unsafe_allow_html=True)
index_data = {
    "DAX 40": ["ADS.DE", "AIR.DE", "ALV.DE", "BAS.DE", "BAYN.DE", "BMW.DE", "DTE.DE", "DBK.DE", "SAP.DE", "SIE.DE", "VOW3.DE"],
    "EuroStoxx 50": ["ASML.AS", "MC.PA", "OR.PA", "SAP.DE", "TTE.PA", "SIE.DE", "AIR.PA", "SAN.MC"],
    "Nasdaq 100": ["AAPL", "MSFT", "NVDA", "AMZN", "TSLA", "GOOGL", "META", "AVGO", "COST"],
    "BIST 100": ["THYAO.IS", "TUPRS.IS", "AKBNK.IS", "ISCTR.IS", "EREGL.IS", "ASELS.IS", "KCHOL.IS"],
    "NIFTY 50": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS", "SBIN.NS"]
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
else: st.warning("Scanner im Standby.")
