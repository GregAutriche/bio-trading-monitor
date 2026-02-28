import os
import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd

# --- AUTO-REFRESH ---
try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    os.system('pip install streamlit-autorefresh')
    from streamlit_autorefresh import st_autorefresh

st_autorefresh(interval=30000, key="datarefresh")

# --- CONFIG & STYLING (Dr. Bauer Edition) ---
st.set_page_config(layout="wide", page_title="Dr. Bauer Strategie-Terminal")

st.markdown("""
    <style>
    .stApp { background-color: #0a0a0a; }
    h1 { color: #00ff00 !important; font-family: 'Arial'; }
    .status-box { background-color: #111; padding: 10px; border-radius: 5px; border-left: 5px solid #00ff00; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIK: DR. BAUER ANALYSE ---
def analyze_bauer_style(df):
    """Implementiert Dr. Bauers Fokus: Candlesticks + Trend + Vola"""
    if len(df) < 20: return None
    
    curr = df['Close'].iloc[-1]
    prev_close = df['Close'].iloc[-2]
    prev_high = df['High'].iloc[-2]
    low_20 = df['Low'].tail(20).min()
    high_20 = df['High'].tail(20).max()
    
    # 1. Candlestick Check (Dr. Bauer Spezialität)
    # Ein bullischer Hammer oder ein starker Body ohne langen Docht oben
    body_size = abs(curr - df['Open'].iloc[-1])
    upper_wick = df['High'].iloc[-1] - max(curr, df['Open'].iloc[-1])
    is_strong_body = upper_wick < (body_size * 0.3) # Wenig Verkaufsdruck oben
    
    # 2. Trend-Check (GD 20 als kurzfristige Basis)
    sma20 = df['Close'].rolling(window=20).mean().iloc[-1]
    is_uptrend = curr > sma20
    
    # 3. Breakout-Logik
    pure_breakout = curr > prev_high
    bauer_signal = pure_breakout and is_strong_body and is_uptrend
    
    # 4. Volatilität (ATR-Basis für Stop-Loss nach Bauer)
    # Dr. Bauer nutzt oft das 1.5- bis 2-fache der ATR für Stops
    df['TR'] = pd.concat([df['High']-df['Low'], abs(df['High']-df['Close'].shift()), abs(df['Low']-df['Close'].shift())], axis=1).max(axis=1)
    atr = df['TR'].rolling(window=14).mean().iloc[-1]
    suggested_stop = curr - (atr * 1.5)

    return {
        "signal": bauer_signal,
        "is_strong_body": is_strong_body,
        "stop_loss": suggested_stop,
        "atr": atr,
        "sma20": sma20
    }

def fetch_data():
    symbols = {
        "^STOXX50E": "EUROSTOXX 50", "^IXIC": "NASDAQ",
        "AAPL": "APPLE", "MSFT": "MICROSOFT", "NVDA": "NVIDIA", 
        "SAP.DE": "SAP", "ASML": "ASML"
    }
    results = {}
    
    for ticker, label in symbols.items():
        try:
            t = yf.Ticker(ticker)
            # Wir brauchen mehr Daten für SMA und ATR (mind. 20 Tage)
            df = t.history(period="1mo")
            if len(df) >= 20:
                bauer_data = analyze_bauer_style(df)
                curr = df['Close'].iloc[-1]
                
                # Wetter-Logik (Dr. Bauer Fokus: Über dem SMA20 = Sonnig)
                delta_sma = ((curr - bauer_data['sma20']) / bauer_data['sma20']) * 100
                w_icon = "☀️" if delta_sma > 0 else "⛈️"
                
                results[label] = {
                    "price": curr,
                    "is_breakout": bauer_data['signal'],
                    "stop": bauer_data['stop_loss'],
                    "w": w_icon,
                    "delta": ((curr - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100,
                    "d_range": (df['Low'].iloc[-1], df['High'].iloc[-1]),
                    "w_range": (df['Low'].tail(5).min(), df['High'].tail(5).max())
                }
        except Exception as e:
            print(f"Error {ticker}: {e}")
    return results

# --- DISPLAY FUNKTIONEN (Vereinfacht für Übersicht) ---
def render_bauer_row(label, d):
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    with col1:
        st.markdown(f"**{label}**")
        st.write(f"{d['w']} Trend-Check")
    with col2:
        st.metric("Preis", f"{d['price']:.2f}", f"{d['delta']:+.2f}%")
    with col3:
        color = "#00ff00" if d['is_breakout'] else "#555"
        st.markdown(f"<span style='color:{color}; font-size:20px; font-weight:bold;'>{'🚀 SIGNAL' if d['is_breakout'] else 'Beobachtung'}</span>", unsafe_allow_html=True)
    with col4:
        st.markdown(f"<div style='font-size:12px; color:#ff4b4b;'>Stop-Loss (ATR):<br><b>{d['stop']:.2f}</b></div>", unsafe_allow_html=True)

# --- MAIN ---
st.title("📡 Dr. Gregor Bauer: Methodik-Terminal")
st.write("Fokus: Candlestick-Stärke + Trendbestätigung (SMA20) + ATR-Stop")

data = fetch_data()
for label, d in data.items():
    render_bauer_row(label, d)
    st.divider()

with st.expander("Methodik nach Dr. Bauer"):
    st.write("""
    1. **Trendfilter:** Nur Long, wenn Preis über SMA 20 (Sonne).
    2. **Candlestick-Bestätigung:** Das Signal '🚀' erscheint nur, wenn die Kerze im oberen Drittel schließt (keine Dochte).
    3. **Risikomanagement:** Der Stop-Loss wird automatisch auf 1.5 * ATR (Volatilität) unter den Kurs gesetzt.
    """)
