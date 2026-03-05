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
    .indicator-label { color: #888; font-size: 0.75rem; margin-top: 2px; }
    .kurs-label { color: #888; font-size: 0.85rem; }
    .row-container { border-bottom: 1px solid #1a202c; padding: 12px 0; width: 100%; }
    .scan-info { color: #ffd700; font-style: italic; font-size: 0.9rem; margin-bottom: 10px; font-weight: bold; }
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
    # RSI (14)
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # ADX (Trendstärke)
    plus_dm = df['High'].diff()
    minus_dm = df['Low'].diff()
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm > 0] = 0
    tr = pd.concat([df['High']-df['Low'], abs(df['High']-df['Close'].shift()), abs(df['Low']-df['Close'].shift())], axis=1).max(axis=1)
    atr = tr.rolling(window=14).mean()
    df['ADX'] = (abs(plus_dm - abs(minus_dm)) / (plus_dm + abs(minus_dm))).rolling(window=14).mean() * 100
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
    delta = ((curr - open_t) / open_t) * 100
    stop = curr - (last_atr * 1.5) if signal == "C" else curr + (last_atr * 1.5) if signal == "P" else 0
    icon = "☀️" if (curr > sma20 and delta > 0.3) else "⚖️" if abs(delta) < 0.3 else "⛈️"
    
    return {
        "display_name": name, "ticker": ticker, "price": curr, 
        "delta": delta, "signal": signal, "stop": stop, "icon": icon, 
        "prob": calculate_probability(df, signal), "rsi": rsi_val, "adx": adx_val
    }

# --- 3. UI RENDERER ---
def render_row(res):
    if not res: return
    is_forex = ("=" in res['ticker'])
    fmt = "{:.6f}" if is_forex else "{:.2f}"
    st.markdown("<div class='row-container'>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns([1.2, 0.6, 0.5, 1.2])
    
    with c1:
        rsi_c = "#ff4b4b" if res['rsi'] > 70 else "#3fb950" if res['rsi'] < 30 else "#888"
        adx_c = "#ffd700" if res['adx'] > 25 else "#888"
        st.markdown(f"""
            **{res['display_name']}**<br>
            <span class='kurs-label'>Kurs: {fmt.format(res['price'])}</span><br>
            <span class='indicator-label'>RSI: <b style='color:{rsi_c};'>{res['rsi']:.1f}</b> | 
            ADX: <b style='color:{adx_c};'>{res['adx']:.1f}</b></span>
        """, unsafe_allow_html=True)
    
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
            prob_txt = f"<span style='color:#ffd700 !important; font-weight:bold; font-size:1.0rem;'>{res['prob']:.1f}%</span>" if res['prob'] >= 60.0 else f"<span style='color:#888 !important;'>({res['prob']:.1f}%)</span>"
            st.markdown(f"<span class='sl-label'>Stop-Loss</span> {prob_txt}<br><span class='sl-value'>{fmt.format(res['stop'])}</span>", unsafe_allow_html=True)
        else:
            st.markdown("<span class='sl-label'>Stop-Loss</span><br><span style='color:#444;'>---</span>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- 4. MAIN APP ---
st.markdown("<div class='header-text'>📡 Dr. Gregor Bauer Strategie Pro</div>", unsafe_allow_html=True)
st.write(f"Update: {datetime.now().strftime('%H:%M:%S')} | Auto-Refresh: 45s")

# --- WIEDERHERGESTELLTE BESCHREIBUNG ---
with st.expander("ℹ️ Strategie-Leitfaden & Markt-Symbole", expanded=False):
    st.markdown("""
    ### 📡 Die Bauer-Strategie Pro 2026
    Dieser Scanner analysiert Märkte basierend auf Momentum und Trendbestätigung.
    
    **1. Markt-Zustand (Symbole):**
    *   ☀️ **Bullish:** Kurs > SMA20 und Tagesplus > 0,3%.
    *   ⚖️ **Neutral:** Geringe Volatilität oder Seitwärtsphase.
    *   ⛈️ **Bearish:** Kurs < SMA20 oder deutlicher Abverkauf.
    
    **2. Die Signal-Logik & RSI:**
    *   <span style='color:#3fb950; border:1px solid #3fb950; padding:2px 5px; border-radius:3px; font-weight:bold;'>C</span> **(Call/Long):** Kurs > SMA20 und 3 steigende Tage. (RSI < 30 leuchtet GRÜN für Erholungschance).
    *   <span style='color:#007bff; border:1px solid #007bff; padding:2px 5px; border-radius:3px; font-weight:bold;'>P</span> **(Put/Short):** Kurs < SMA20 und 3 fallende Tage. (RSI > 70 leuchtet ROT für Korrekturgefahr).
    
    **3. Wahrscheinlichkeit (Gold-Logik):**
    Die Prozentzahl zeigt die historische Trefferquote (12 Monate). Signale mit <span style='color:#ffd700; font-weight:bold;'>≥ 60,0%</span> werden gold markiert.
    
    **4. ADX (Trendstärke):**
    Ein ADX-Wert über <b style='color:#ffd700;'>25</b> zeigt einen starken Trend an, was die Zuverlässigkeit der Signale erhöht.
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
    "DAX 40": ["ADS.DE", "AIR.DE", "ALV.DE", "BAS.DE", "BAYN.DE", "BMW.DE", "DTE.DE", "DBK.DE", "SAP.DE", "SIE.DE", "VOW3.DE"],
    "EuroStoxx 50": ["ASML.AS", "MC.PA", "OR.PA", "SAP.DE", "TTE.PA", "SIE.DE", "AIR.PA", "SAN.MC"],
    "Nasdaq 100": ["AAPL", "MSFT", "NVDA", "AMZN", "TSLA", "GOOGL", "META", "AVGO", "COST"],
    "BIST 100": ["THYAO.IS", "TUPRS.IS", "AKBNK.IS", "ISCTR.IS", "EREGL.IS", "ASELS.IS", "KCHOL.IS"],
    "NIFTY 50": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS", "SBIN.NS"]
}

with st.expander("Index-Auswahl & Scan", expanded=True):
    col_sel, col_btn = st.columns(2) # FIX: st.columns(2) verhindert den TypeError
    if 'scan_active' not in st.session_state: st.session_state.scan_active = False
    with col_sel:
        choice = st.radio("Wähle Markt:", list(index_data.keys()), horizontal=True)
    with col_btn:
        st.write("<br>", unsafe_allow_html=True)
        if st.button("🚀 Scan Start/Stop", use_container_width=True):
            st.session_state.scan_active = not st.session_state.scan_active

if st.session_state.scan_active:
    st.markdown(f"<div class='scan-info'>Scanne {choice}... Zeige nur Treffer mit Signal.</div>", unsafe_allow_html=True)
    with ThreadPoolExecutor(max_workers=30) as executor:
        results = list(executor.map(fetch_data, index_data[choice]))
        signal_hits = [r for r in results if r is not None and r['signal'] != "Wait"]
        if signal_hits:
            sorted_hits = sorted(signal_hits, key=lambda x: (x['prob'] < 60.0, -x['prob']))
            for r in sorted_hits: render_row(r)
        else: st.info("Keine aktiven Signale.")
else:
    st.warning("Scanner im Standby.")
