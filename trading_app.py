import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# --- 0. AUTO-REFRESH ---
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
    .header-text { font-size: 24px; font-weight: bold; margin-bottom: 10px; display: flex; align-items: center; gap: 10px; }
    .sig-box-p { color: #ff4b4b; border: 1px solid #ff4b4b; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
    .sig-box-c { color: #3fb950; border: 1px solid #3fb950; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
    .sl-label { color: #888; font-size: 0.85rem; }
    .sl-value { color: #e0e0e0; font-weight: bold; font-size: 1rem; }
    .prob-val { color: #888; font-size: 0.85rem; margin-left: 5px; }
    .row-container { border-bottom: 1px solid #1a202c; padding: 10px 0; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ERWEITERTE NAMENS-DATENBANK ---
NAME_DB = {
    "EURUSD=X": "Euro / US-Dollar", "^GDAXI": "DAX 40", "^STOXX50E": "EURO STOXX 50",
    "^IXIC": "NASDAQ Composite", "XU100.IS": "BIST 100", "^NSEI": "NIFTY 50",
    # EuroStoxx 50 Klarnamen
    "ASML.AS": "ASML Holding", "MC.PA": "LVMH Moët Hennessy", "OR.PA": "L'Oréal S.A.", 
    "SAP.DE": "SAP SE", "TTE.PA": "TotalEnergies", "SAN.MC": "Banco Santander",
    # DAX
    "ADS.DE": "Adidas AG", "ALV.DE": "Allianz SE", "BAS.DE": "BASF SE", "BMW.DE": "BMW AG"
}

# --- 3. DATEN-ENGINE ---
def analyze_ticker(ticker):
    try:
        df = yf.download(ticker, period="1y", interval="1d", progress=False, auto_adjust=True)
        if df.empty or len(df) < 25: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        # Deep Clean EUR/USD
        if "EURUSD=X" in ticker:
            mask = (df['Close'] > 2.0) | (df['Close'] < 0.5)
            if mask.any():
                df.loc[mask, ['Open', 'High', 'Low', 'Close']] = df.loc[~mask, 'Close'].median() or 1.1622

        curr = float(df['Close'].iloc[-1])
        prev, prev2 = df['Close'].iloc[-2], df['Close'].iloc[-3]
        open_t = df['Open'].iloc[-1]
        sma20 = df['Close'].rolling(window=20).mean().iloc[-1]
        atr = (df['High']-df['Low']).rolling(window=14).mean().iloc[-1]
        
        signal = "C" if (curr > prev > prev2 and curr > sma20) else "P" if (curr < prev < prev2 and curr < sma20) else "Wait"
        delta = ((curr - open_t) / open_t) * 100
        stop = curr - (atr * 1.5) if signal == "C" else curr + (atr * 1.5) if signal == "P" else 0
        icon = "☀️" if (curr > sma20 and delta > 0.3) else "⚖️" if abs(delta) < 0.3 else "⛈️"
        
        # Klarnamen-Logik verbessern: Wenn nicht in DB, frage yfinance Info ab
        display_name = NAME_DB.get(ticker)
        if not display_name:
            try:
                display_name = yf.Ticker(ticker).info.get('shortName') or ticker
            except:
                display_name = ticker

        return {
            "display_name": display_name, "ticker": ticker, "price": curr, 
            "delta": delta, "signal": signal, "stop": stop, "icon": icon, 
            "prob": 44.7 # Beispielwert für Wahrscheinlichkeit
        }
    except: return None

# --- 4. UI RENDERER ---
def render_row(res):
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
            prob_txt = f"{res['prob']:.1f}%" if res['prob'] >= 60 else f"({res['prob']:.1f}%)"
            st.markdown(f"<span class='sl-label'>Stop-Loss</span> <span class='prob-val'>(({prob_txt}))</span><br><span class='sl-value'>{fmt.format(res['stop'])}</span>", unsafe_allow_html=True)
        else: st.markdown("<span class='sl-label'>Stop-Loss</span><br><span style='color:#444;'>---</span>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- 5. MAIN APP ---
st.markdown("<div class='header-text'>📡 Dr. Gregor Bauer Strategie Pro</div>", unsafe_allow_html=True)
st.write(f"Update: {datetime.now().strftime('%H:%M:%S')}")

# Macro Indices
macro_tickers = ["EURUSD=X", "^GDAXI", "^STOXX50E", "^IXIC", "XU100.IS", "^NSEI"]
with ThreadPoolExecutor(max_workers=6) as executor:
    results = list(executor.map(analyze_ticker, macro_tickers))
    for res in filter(None, results): render_row(res)

# Scanner Section
st.markdown("<br><div class='header-text'>🔭 Market Scanner</div>", unsafe_allow_html=True)
index_data = {
    "EuroStoxx 50": ["ASML.AS", "MC.PA", "OR.PA", "SAP.DE", "TTE.PA"],
    "DAX 40": ["ADS.DE", "ALV.DE", "BAS.DE", "BMW.DE"],
    "Nasdaq 100": ["AAPL", "MSFT", "NVDA", "AMZN"]
}
choice = st.radio("", list(index_data.keys()), horizontal=True)

if st.button(f"Scan {choice} starten"):
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(analyze_ticker, index_data[choice]))
        for r in filter(None, results): render_row(r)
