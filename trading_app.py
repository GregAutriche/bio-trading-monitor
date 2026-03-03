import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# --- 1. CONFIG & STYLING ---
st.set_page_config(layout="wide", page_title="Bauer Strategy Pro 2026")

st.markdown("""
    <style>
    .stApp { background-color: #0d1117; }
    h1, h2, h3, p, span, label, div { color: #c9d1d9 !important; font-family: 'Segoe UI', sans-serif; }
    .ticker-card { background-color: #161b22; padding: 15px; border-radius: 10px; border: 1px solid #30363d; margin-bottom: 10px; }
    .sig-c { color: #3fb950; font-weight: bold; border: 1px solid #3fb950; padding: 3px 10px; border-radius: 5px; }
    .sig-p { color: #f85149; font-weight: bold; border: 1px solid #f85149; padding: 3px 10px; border-radius: 5px; }
    .prob-text { font-size: 0.85rem; color: #8b949e; }
    .focus-header { color: #f0883e !important; font-weight: bold; border-bottom: 1px solid #30363d; padding-bottom: 5px; margin: 20px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. BACKTEST ENGINE (WAHRSCHEINLICHKEIT) ---
def calculate_historical_probability(df, signal_type):
    """ Berechnet die Trefferquote der Strategie für diesen Ticker über 1 Jahr """
    if df is None or len(df) < 60: return 50.0
    
    # Daten für Backtest (letzte 250 Handelstage)
    bt_df = df.copy()
    bt_df['SMA20'] = bt_df['Close'].rolling(window=20).mean()
    
    hits = 0
    signals_found = 0
    
    # Wir prüfen die Historie (bis 5 Tage vor heute)
    for i in range(25, len(bt_df) - 5):
        c = bt_df['Close'].iloc[i]
        p = bt_df['Close'].iloc[i-1]
        p2 = bt_df['Close'].iloc[i-2]
        sma = bt_df['SMA20'].iloc[i]
        
        # Historisches Signal erkennen
        hist_sig = None
        if (c > p > p2) and c > sma: hist_sig = "C"
        elif (c < p < p2) and c < sma: hist_sig = "P"
        
        if hist_sig == signal_type:
            signals_found += 1
            # Check: War der Preis 5 Tage später im Profit?
            future_price = bt_df['Close'].iloc[i+5]
            if signal_type == "C" and future_price > c: hits += 1
            if signal_type == "P" and future_price < c: hits += 1
            
    if signals_found == 0: return 50.0
    return (hits / signals_found) * 100

# --- 3. KERN-LOGIK ---
def get_bauer_analysis(ticker):
    try:
        # Daten laden (1 Jahr für stabilen Backtest)
        df = yf.download(ticker, period="1y", interval="1d", progress=False)
        if df.empty or len(df) < 25: return None
        
        # Aktuelle Werte
        curr = df['Close'].iloc[-1]
        prev = df['Close'].iloc[-2]
        prev2 = df['Close'].iloc[-3]
        open_t = df['Open'].iloc[-1]
        sma20 = df['Close'].rolling(window=20).mean().iloc[-1]
        
        # ATR für dynamischen Stop
        high_low = df['High'] - df['Low']
        atr = high_low.rolling(window=14).mean().iloc[-1]
        
        # Signal Logik
        signal = "Wait"
        if (curr > prev > prev2) and curr > sma20: signal = "C"
        elif (curr < prev < prev2) and curr < sma20: signal = "P"
        
        # Wahrscheinlichkeit berechnen
        prob = 0
        if signal != "Wait":
            prob = calculate_historical_probability(df, signal)
            
        delta = ((curr - open_t) / open_t) * 100
        stop = curr - (atr * 1.5) if signal == "C" else curr + (atr * 1.5) if signal == "P" else 0
        
        return {
            "ticker": ticker,
            "price": curr,
            "delta": delta,
            "signal": signal,
            "stop": stop,
            "prob": prob,
            "icon": "☀️" if delta > 0 else "⛈️"
        }
    except Exception as e:
        return None

# --- 4. UI ANZEIGE ---
def display_signal_row(res):
    with st.container():
        cols = st.columns([1.5, 1, 1, 1, 1, 1.5])
        
        with cols[0]:
            st.markdown(f"**{res['ticker']}**")
            st.caption(f"Kurs: {res['price']:.2f}")
            
        with cols[1]:
            color = "#3fb950" if res['delta'] > 0 else "#f85149"
            st.markdown(f"<span style='color:{color}'>{res['delta']:+.2f}%</span>", unsafe_allow_html=True)
            
        with cols[2]:
            sig_class = "sig-c" if res['signal'] == "C" else "sig-p" if res['signal'] == "P" else "sig-wait"
            st.markdown(f"<span class='{sig_class}'>{res['signal']}</span>", unsafe_allow_html=True)
            
        with cols[3]:
            if res['signal'] != "Wait":
                st.markdown(f"<small>SL:</small><br><code style='color:#f85149'>{res['stop']:.2f}</code>", unsafe_allow_html=True)
            else:
                st.text("---")
                
        with cols[4]:
            if res['signal'] != "Wait":
                p_color = "#3fb950" if res['prob'] > 55 else "#f0883e"
                st.markdown(f"<b style='color:{p_color}'>{res['prob']:.1f}%</b>", unsafe_allow_html=True)
                st.progress(res['prob'] / 100)
            else:
                st.caption("Kein Signal")

        st.divider()

# --- 5. MAIN APP ---
st.title("📡 Dr. Gregor Bauer: Wahrscheinlichkeits-Screener")
st.write(f"Status: Live-Daten | {datetime.now().strftime('%H:%M:%S')}")

# Macro Section
st.markdown("<h3 class='focus-header'>🌍 Markt-Indizes</h3>", unsafe_allow_html=True)
macros = ["^GDAXI", "^IXIC", "EURUSD=X", "BTC-USD"]
with ThreadPoolExecutor(max_workers=5) as executor:
    macro_res = list(executor.map(get_bauer_analysis, macros))
    for r in filter(None, macro_res):
        display_signal_row(r)

# Stock Screener Section
st.markdown("<h3 class='focus-header'>🔭 Aktien-Screener</h3>", unsafe_allow_html=True)
indices = {
    "DAX Top": ["ADS.DE", "ALV.DE", "BAS.DE", "BMW.DE", "DBK.DE", "DTE.DE", "SAP.DE", "SIE.DE", "VOW3.DE"],
    "US Tech": ["AAPL", "MSFT", "NVDA", "TSLA", "GOOGL", "AMZN", "META", "AMD"]
}
choice = st.radio("Asset-Gruppe wählen:", list(indices.keys()), horizontal=True)

if st.button(f"Scan {choice} starten"):
    with st.spinner("Berechne Wahrscheinlichkeiten..."):
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(get_bauer_analysis, indices[choice]))
            
            # Sortieren: Signale zuerst, dann nach Wahrscheinlichkeit
            valid_res = [r for r in results if r is not None]
            valid_res.sort(key=lambda x: (x['signal'] == "Wait", -x['prob']))
            
            for r in valid_res:
                display_signal_row(r)
