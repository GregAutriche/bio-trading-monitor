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

st_autorefresh(interval=45000, key="datarefresh")

# --- 1. CONFIG & STYLING ---
st.set_page_config(layout="wide", page_title="Dr. Bauer Strategie-Terminal")

st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    h1, h2, h3, p, span, label, div { color: #e0e0e0 !important; font-family: 'Courier New', Courier, monospace; }
    .ticker-name { color: #00ff00; font-size: 16px; font-weight: bold; margin-bottom: 0px; }
    .open-price { color: #888888; font-size: 11px; margin-top: -5px; margin-bottom: 10px; }
    .expander-style { border: 1px solid #333; border-radius: 10px; padding: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGIK: ANALYSE ---
def analyze_bauer_style(df):
    if len(df) < 20: return None
    curr = df['Close'].iloc[-1]
    prev_high = df['High'].iloc[-2]
    
    # Candlestick-Stärke (Schlusskurs im oberen Drittel?)
    body_size = abs(curr - df['Open'].iloc[-1])
    upper_wick = df['High'].iloc[-1] - max(curr, df['Open'].iloc[-1])
    is_strong_body = upper_wick < (body_size * 0.3)
    
    # Trend (SMA20)
    sma20 = df['Close'].rolling(window=20).mean().iloc[-1]
    
    # ATR Stop-Loss
    df['TR'] = pd.concat([df['High']-df['Low'], abs(df['High']-df['Close'].shift()), abs(df['Low']-df['Close'].shift())], axis=1).max(axis=1)
    atr = df['TR'].rolling(window=14).mean().iloc[-1]
    
    return {
        "signal": (curr > prev_high) and is_strong_body and (curr > sma20),
        "stop": curr - (atr * 1.5),
        "open_today": df['Open'].iloc[-1]
    }

def fetch_data(symbols):
    results = {}
    for ticker, label in symbols.items():
        try:
            t = yf.Ticker(ticker)
            df = t.history(period="1mo")
            if not df.empty:
                analysis = analyze_bauer_style(df)
                curr = df['Close'].iloc[-1]
                results[label] = {
                    "price": curr, "open": analysis['open_today'],
                    "is_breakout": analysis['signal'], "stop": analysis['stop'],
                    "delta": ((curr - analysis['open_today']) / analysis['open_today']) * 100
                }
        except: pass
    return results

# --- 3. DEFINITION DER TICKER ---
main_stocks = {
    "AAPL": "APPLE", "MSFT": "MICROSOFT", "NVDA": "NVIDIA", "SAP.DE": "SAP"
}

global_markets = {
    "EURUSD=X": "EUR/USD", 
    "XU100.IS": "BIST 100 (TR)", 
    "^NSEI": "NIFTY 50 (IN)", 
    "RTSI.ME": "RTS INDEX (RU)", 
    "IMOEX.ME": "MOEX RUSSIA", 
    "EURRUB=X": "EUR/RUB"
}

# --- 4. RENDER ---
st.title("📡 Dr. Bauer Strategie-Terminal")
st.write(f"Update: {datetime.now().strftime('%H:%M:%S')} | Intervall: 45s")

# Sektion 1: Fokus-Aktien
st.subheader("🔥 Fokus-Werte")
data_main = fetch_data(main_stocks)
for label, d in data_main.items():
    cols = st.columns([1, 1, 1, 1])
    with cols[0]:
        st.markdown(f"<div class='ticker-name'>{label}</div><div class='open-price'>Start: {d['open']:.2f}</div>", unsafe_allow_html=True)
    with cols[1]: st.metric("Kurs", f"{d['price']:.2f}", f"{d['delta']:+.2f}%")
    with cols[2]: st.markdown(f"### {'🚀 BUY' if d['is_breakout'] else 'WAIT'}")
    with cols[3]: st.markdown(f"<small>Stop:</small><br><b style='color:#ff4b4b;'>{d['stop']:.2f}</b>", unsafe_allow_html=True)
    st.divider()

# Sektion 2: Expander für globale Märkte
with st.expander("🌍 GLOBALE MÄRKTE & WÄHRUNGEN (EURUSD, BIST, NIFTY, MOEX)"):
    data_global = fetch_data(global_markets)
    for label, d in data_global.items():
        g_cols = st.columns([1, 1, 1, 1])
        with g_cols[0]:
            st.markdown(f"**{label}**<br><small>Start: {d['open']:.4f}</small>", unsafe_allow_html=True)
        with g_cols[1]: st.metric("", f"{d['price']:.4f}", f"{d['delta']:+.2f}%")
        with g_cols[2]: st.write("🚀" if d['is_breakout'] else "⚪")
        with g_cols[3]: st.write(f"Stop: {d['stop']:.4f}")
        st.markdown("<hr style='margin:5px; border-color:#222;'>", unsafe_allow_html=True)
