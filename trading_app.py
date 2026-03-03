import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# --- 0. AUTO-REFRESH (45 Sekunden) ---
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
    
    /* Header & Titel */
    .header-text { font-size: 24px; font-weight: bold; margin-bottom: 10px; display: flex; align-items: center; gap: 10px; }
    
    /* Signal Design */
    .sig-box-p { color: #ff4b4b; border: 1px solid #ff4b4b; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
    .sig-box-c { color: #3fb950; border: 1px solid #3fb950; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
    .sig-wait { color: #888; font-weight: normal; margin-top: 10px; display: inline-block; }
    
    /* Stop Loss & Wahrscheinlichkeit Design */
    .sl-label { color: #888; font-size: 0.85rem; }
    .sl-value { color: #e0e0e0; font-weight: bold; font-size: 1rem; }
    .prob-val { color: #888; font-size: 0.85rem; margin-left: 5px; }
    .kurs-label { color: #888; font-size: 0.85rem; }
    .price-display { font-size: 1rem; font-weight: bold; }
    
    /* Layout Straffung */
    .row-container { border-bottom: 1px solid #1a202c; padding: 10px 0; width: 100%; }
    .fix-badge { background-color: #3fb950; color: white !important; padding: 1px 5px; border-radius: 3px; font-size: 10px; font-weight: bold; margin-left: 8px; vertical-align: middle; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. NAMENS-DATENBANK (KLARNAMEN) ---
NAME_DB = {
    "EURUSD=X": "Euro / US-Dollar", "^GDAXI": "DAX 40", "^STOXX50E": "EURO STOXX 50",
    "^IXIC": "NASDAQ Composite", "XU100.IS": "BIST 100", "^NSEI": "NIFTY 50"
}

# --- 3. DATEN-ENGINE ---
def clean_df(df):
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df

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

def analyze_ticker(ticker):
    try:
        # Tickerspezifischer Download ohne geteilten Cache
        df = yf.download(ticker, period="1y", interval="1d", progress=False, auto_adjust=True)
        if df.empty or len(df) < 25: return None
        df = clean_df(df)
        
        is_recovered = False
        if "EURUSD=X" in ticker:
            mask = (df['Close'] > 2.0) | (df['Close'] < 0.5)
            if mask.any():
                is_recovered = True
                valid_median = df.loc[~mask, 'Close'].median()
                if pd.isna(valid_median): valid_median = 1.1622 # Manueller Fallback
                df.loc[mask, ['Open', 'High', 'Low', 'Close']] = valid_median

        curr = float(df['Close'].iloc[-1])
        prev, prev2 = df['Close'].iloc[-2], df['Close'].iloc[-3]
        open_t = df['Open'].iloc[-1]
        sma20 = df['Close'].rolling(window=20).mean().iloc[-1]
        atr = (df['High']-df['Low']).rolling(window=14).mean().iloc[-1]
        
        signal = "C" if (curr > prev > prev2 and curr > sma20) else "P" if (curr < prev < prev2 and curr < sma20) else "Wait"
        delta = ((curr - open_t) / open_t) * 100
        stop = curr - (atr * 1.5) if signal == "C" else curr + (atr * 1.5) if signal == "P" else 0
        icon = "☀️" if (curr > sma20 and delta > 0.3) else "⚖️" if abs(delta) < 0.3 else "⛈️"
        
        # Jedes Ergebnis als neues, isoliertes Dictionary zurückgeben
        return {
            "display_name": NAME_DB.get(ticker, ticker), 
            "ticker": ticker, 
            "price": curr, 
            "delta": delta, 
            "signal": signal, 
            "stop": stop, 
            "icon": icon, 
            "is_recovered": is_recovered, 
            "prob": calculate_probability(df, signal)
        }
    except Exception as e:
        return None

# --- 4. UI RENDERER ---
def render_row(res):
    is_forex = ("=" in res['ticker'])
    # Währung auf 6 Nachkommastellen, Indizes auf 2
    fmt = "{:.6f}" if is_forex else "{:.2f}"
    
    st.markdown("<div class='row-container'>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns([1.2, 0.6, 0.5, 1.2])
    
    with c1:
        fix = "<span class='fix-badge'>FIX</span>" if res.get('is_recovered') else ""
        st.markdown(f"**{res['display_name']}** {fix}<br><span class='kurs-label'>Kurs: </span><span class='price-display'>{fmt.format(res['price'])}</span>", unsafe_allow_html=True)
    
    with c2:
        color = "#3fb950" if res['delta'] >= 0 else "#ff4b4b"
        st.markdown(f"<div style='text-align:center;'>{res['icon']}<br><span style='color:{color}; font-size:0.85rem;'>{res['delta']:+.2f}%</span></div>", unsafe_allow_html=True)
    
    with c3:
        if res['signal'] == "Wait":
            st.markdown(f"<span class='sig-wait'>{res['signal']}</span>", unsafe_allow_html=True)
        else:
            cls = "sig-box-c" if res['signal'] == "C" else "sig-box-p"
            st.markdown(f"<br><span class='{cls}'>{res['signal']}</span>", unsafe_allow_html=True)
            
    with c4:
        if res['stop'] != 0:
            # Wahrscheinlichkeit direkt hinter dem Stop-Loss Label
            prob_txt = f"{res['prob']:.1f}%" if res['prob'] >= 60 else f"({res['prob']:.1f}%)"
            st.markdown(f"<span class='sl-label'>Stop-Loss</span> <span class='prob-val'>({prob_txt})</span><br><span class='sl-value'>{fmt.format(res['stop'])}</span>", unsafe_allow_html=True)
        else:
            st.markdown("<span class='sl-label'>Stop-Loss</span><br><span style='color:#444;'>---</span>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- 5. MAIN APP ---
st.markdown("<div class='header-text'>📡 Dr. Gregor Bauer Strategie Pro</div>", unsafe_allow_html=True)
st.write(f"Letztes Update: {datetime.now().strftime('%H:%M:%S')} | Auto-Refresh: 45s")

with st.expander("ℹ️ Strategie-Logik & System-Erklärung (Vollständige Ausführung)"):
    st.markdown("""
    ### **1. Trend-Check (2-Tage-Regel)**
    *   **Call (C):** Heute > Gestern UND Gestern > Vorgestern.
    *   **Put (P):** Heute < Gestern UND Gestern < Vorgestern.

    ### **2. SMA 20 Filter**
    *   **Call:** Nur wenn Kurs > SMA 20.
    *   **Put:** Nur wenn Kurs < SMA 20.

    ### **3. Dynamischer Stop-Loss**
    Absicherung mittels **ATR 14** (Faktor 1.5).

    ### **4. Wahrscheinlichkeit**
    Historische Trefferquote (Backtest 1 Jahr). Werte unter 60% werden in Klammern angezeigt.
    """)

st.markdown("<div class='header-text'>🌍 Macro & Indices</div>", unsafe_allow_html=True)
macro_tickers = ["EURUSD=X", "^GDAXI", "^STOXX50E", "^IXIC", "XU100.IS", "^NSEI"]

with ThreadPoolExecutor(max_workers=6) as executor:
    # Sequentielles Mapping für korrekte Reihenfolge und Daten-Integrität
    results = list(executor.map(analyze_ticker, macro_tickers))
    for res in filter(None, results):
        render_row(res)

st.markdown("<br><div class='header-text'>🔭 Market Scanner</div>", unsafe_allow_html=True)
with st.expander("Scanner-Einstellungen & Index-Auswahl", expanded=True):
    index_data = {
        "DAX 40": ["ADS.DE", "ALV.DE", "BAS.DE", "BMW.DE", "SAP.DE", "SIE.DE"],
        "Nasdaq 100": ["AAPL", "MSFT", "NVDA", "AMZN", "TSLA", "GOOGL"],
        "EuroStoxx 50": ["ASML.AS", "MC.PA", "OR.PA", "SAP.DE", "TTE.PA"],
        "BIST 100": ["THYAO.IS", "TUPRS.IS", "AKBNK.IS", "ISCTR.IS"],
        "NIFTY 50": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS"]
    }
    choice = st.radio("Wähle einen Index für den Live-Scan:", list(index_data.keys()), horizontal=True)
    scan_button = st.button(f"Scan {choice} starten")

if scan_button:
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(analyze_ticker, index_data[choice]))
        for r in sorted([r for r in results if r], key=lambda x: (x['signal'] == "Wait", -x['prob'])):
            render_row(r)
