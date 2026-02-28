import os
import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd

# --- 0. AUTO-REFRESH (45 Sekunden) ---
try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    os.system('pip install streamlit-autorefresh')
    from streamlit_autorefresh import st_autorefresh

# Intervall auf 45000ms = 45 Sekunden gesetzt
st_autorefresh(interval=45000, key="datarefresh")

# --- 1. CONFIG & STYLING ---
st.set_page_config(layout="wide", page_title="Dr. Bauer Strategie-Terminal")

st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    h1, h2, h3, p, span, label, div { color: #e0e0e0 !important; font-family: 'Courier New', Courier, monospace; }
    .ticker-name { color: #00ff00; font-size: 16px; font-weight: bold; margin-bottom: 0px; }
    .open-price { color: #888888; font-size: 11px; margin-top: -5px; margin-bottom: 10px; }
    [data-testid="stMetricValue"] { font-size: 22px !important; color: #ffffff !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGIK: DR. BAUER ANALYSE ---
def analyze_bauer_style(df):
    """Bauer-Methodik: Candlestick-Stärke + Trend + Vola-Stop"""
    if len(df) < 20: return None
    
    curr = df['Close'].iloc[-1]
    prev_high = df['High'].iloc[-2]
    
    # 1. Candlestick Check: Schließt die Kerze im oberen Drittel? (Stärke-Signal)
    body_size = abs(curr - df['Open'].iloc[-1])
    upper_wick = df['High'].iloc[-1] - max(curr, df['Open'].iloc[-1])
    is_strong_body = upper_wick < (body_size * 0.3)
    
    # 2. Trend-Check (Preis über SMA20)
    sma20 = df['Close'].rolling(window=20).mean().iloc[-1]
    is_uptrend = curr > sma20
    
    # 3. Breakout-Signal nach Bauer
    bauer_signal = (curr > prev_high) and is_strong_body and is_uptrend
    
    # 4. ATR für Stop-Loss (1.5x Volatilität)
    df['TR'] = pd.concat([df['High']-df['Low'], abs(df['High']-df['Close'].shift()), abs(df['Low']-df['Close'].shift())], axis=1).max(axis=1)
    atr = df['TR'].rolling(window=14).mean().iloc[-1]
    
    return {
        "signal": bauer_signal,
        "stop": curr - (atr * 1.5),
        "sma20": sma20,
        "open_today": df['Open'].iloc[-1] # Heutiger Eröffnungspreis
    }

def fetch_data():
    symbols = {
        "^STOXX50E": "EUROSTOXX 50", "^IXIC": "NASDAQ",
        "AAPL": "APPLE", "MSFT": "MICROSOFT", "NVDA": "NVIDIA", 
        "SAP.DE": "SAP", "ASML": "ASML"
    }
    results = {}
    aktuell = datetime.now()
    
    for ticker, label in symbols.items():
        try:
            t = yf.Ticker(ticker)
            df = t.history(period="1mo")
            if len(df) >= 20:
                analysis = analyze_bauer_style(df)
                curr = df['Close'].iloc[-1]
                
                results[label] = {
                    "price": curr,
                    "open": analysis['open_today'],
                    "is_breakout": analysis['signal'],
                    "stop": analysis['stop'],
                    "delta": ((curr - analysis['open_today']) / analysis['open_today']) * 100,
                    "sma_dist": curr > analysis['sma20']
                }
        except: pass
    return results

# --- 3. RENDER ---
st.title("📡 Dr. Bauer Strategie-Terminal")
st.write(f"Letztes Update: {datetime.now().strftime('%H:%M:%S')} (Intervall: 45s)")

data = fetch_data()

for label, d in data.items():
    with st.container():
        # Name und Eröffnungspreis direkt darunter
        st.markdown(f"""
            <div class='ticker-name'>{label}</div>
            <div class='open-price'>Eröffnung heute: {d['open']:.2f}</div>
        """, unsafe_allow_html=True)
        
        cols = st.columns([1, 1, 1])
        with cols[0]:
            st.metric("Kurs", f"{d['price']:.2f}", f"{d['delta']:+.2f}%")
        with cols[1]:
            color = "#00ff00" if d['is_breakout'] else "#444"
            st.markdown(f"<h3 style='color:{color};'>{'🚀 SIGNAL' if d['is_breakout'] else 'WAIT'}</h3>", unsafe_allow_html=True)
        with cols[2]:
            st.markdown(f"<div style='color:#ff4b4b; font-size:12px;'>Bauer-Stop (ATR):<br><b>{d['stop']:.2f}</b></div>", unsafe_allow_html=True)
        st.divider()
