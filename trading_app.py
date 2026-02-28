import os
import streamlit as st
import yfinance as yf
from datetime import datetime
import pandas as pd

# --- 0. AUTO-REFRESH (45 Sekunden) ---
try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    os.system('pip install streamlit-autorefresh')
    from streamlit_autorefresh import st_autorefresh

st_autorefresh(interval=45000, key="datarefresh")

# --- 1. CONFIG & STYLING ---
st.set_page_config(layout="wide", page_title="Dr. Bauer Wetter-Terminal")

st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    h1, h2, h3, p, span, label, div { color: #e0e0e0 !important; font-family: 'Courier New', Courier, monospace; }
    .ticker-name { color: #00ff00; font-size: 18px; font-weight: bold; margin-bottom: 0px; }
    .open-price { color: #888888; font-size: 12px; margin-top: -5px; }
    .weather-icon { font-size: 35px; text-align: center; }
    .weather-text { font-size: 10px; color: #888; text-align: center; margin-top: -10px; }
    hr { border-color: #222 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. WETTER-LOGIK NACH BAUER (Trend & Vola) ---
def get_bauer_weather(curr, sma20, delta):
    # Dr. Bauer: Trend ist "Sonnig", wenn über SMA20 UND positivem Delta
    if curr > sma20 and delta > 0.5: return "☀️", "STARKER TREND"
    elif curr > sma20: return "🌤️", "BULLISH"
    elif curr < sma20 and delta < -0.5: return "⛈️", "GEWITTER"
    else: return "☁️", "NEUTRAL / ABWARTEN"

def analyze_bauer(df):
    if len(df) < 20: return None
    curr = df['Close'].iloc[-1]
    open_today = df['Open'].iloc[-1]
    prev_high = df['High'].iloc[-2]
    sma20 = df['Close'].rolling(window=20).mean().iloc[-1]
    delta = ((curr - open_today) / open_today) * 100
    
    # Candlestick-Check (Stärke-Signal)
    body_size = abs(curr - open_today)
    upper_wick = df['High'].iloc[-1] - max(curr, open_today)
    is_strong = upper_wick < (body_size * 0.35)
    
    # ATR Stop
    df['TR'] = pd.concat([df['High']-df['Low'], abs(df['High']-df['Close'].shift()), abs(df['Low']-df['Close'].shift())], axis=1).max(axis=1)
    atr = df['TR'].rolling(window=14).mean().iloc[-1]
    
    icon, txt = get_bauer_weather(curr, sma20, delta)
    
    return {
        "price": curr, "open": open_today, "delta": delta,
        "icon": icon, "weather_txt": txt,
        "signal": (curr > prev_high) and is_strong and (curr > sma20),
        "stop": curr - (atr * 1.5)
    }

def fetch_data(symbols):
    results = {}
    for ticker, label in symbols.items():
        try:
            t = yf.Ticker(ticker)
            df = t.history(period="1mo")
            if not df.empty: results[label] = analyze_bauer(df)
        except: pass
    return results

# --- 3. DATA & UI ---
main_list = {"AAPL": "APPLE", "MSFT": "MICROSOFT", "NVDA": "NVIDIA", "SAP.DE": "SAP"}
global_list = {
    "EURUSD=X": "EUR/USD", "XU100.IS": "BIST 100", "^NSEI": "NIFTY 50", 
    "RTSI.ME": "RTS INDEX", "IMOEX.ME": "MOEX RUSSIA", "EURRUB=X": "EUR/RUB"
}

st.title("📡 Dr. Bauer Börsen-Wetter")
st.write(f"Refreshed: {datetime.now().strftime('%H:%M:%S')} (45s Takt)")

# FOKUS WERTE
data_main = fetch_data(main_list)
for label, d in data_main.items():
    cols = st.columns([1, 1, 1, 1, 1])
    with cols[0]:
        st.markdown(f"<div class='ticker-name'>{label}</div><div class='open-price'>Start: {d['open']:.2f}</div>", unsafe_allow_html=True)
    with cols[1]:
        st.markdown(f"<div class='weather-icon'>{d['icon']}</div><div class='weather-text'>{d['weather_txt']}</div>", unsafe_allow_html=True)
    with cols[2]:
        st.metric("Kurs", f"{d['price']:.2f}", f"{d['delta']:+.2f}%")
    with cols[3]:
        color = "#00ff00" if d['signal'] else "#444"
        st.markdown(f"<h2 style='color:{color}; margin:0;'>{'🚀' if d['signal'] else 'Wait'}</h2>", unsafe_allow_html=True)
    with cols[4]:
        st.markdown(f"<small>Bauer-Stop:</small><br><b style='color:#ff4b4b;'>{d['stop']:.2f}</b>", unsafe_allow_html=True)
    st.divider()

# GLOBAL EXPANDER
with st.expander("🌍 GLOBALE MÄRKTE & WÄHRUNGEN"):
    data_global = fetch_data(global_list)
    for label, d in data_global.items():
        g_cols = st.columns([1.5, 1, 1.5, 1, 1])
        with g_cols[0]: st.markdown(f"**{label}**<br><small>Start: {d['open']:.4f}</small>", unsafe_allow_html=True)
        with g_cols[1]: st.write(d['icon'])
        with g_cols[2]: st.metric("", f"{d['price']:.4f}", f"{d['delta']:+.2f}%")
        with g_cols[3]: st.write("🚀" if d['signal'] else "⚪")
        with g_cols[4]: st.write(f"Stop: {d['stop']:.4f}")
        st.markdown("<hr style='margin:5px; border-color:#222;'>", unsafe_allow_html=True)
