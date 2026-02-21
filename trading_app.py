import os
import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd

# --- 0. AUTO-REFRESH ---
try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    os.system('pip install streamlit-autorefresh')
    from streamlit_autorefresh import st_autorefresh

st_autorefresh(interval=30000, key="datarefresh")

def play_alarm():
    audio_html = """<audio autoplay style="display:none;"><source src="https://assets.mixkit.co" type="audio/mpeg"></audio>"""
    st.markdown(audio_html, unsafe_allow_html=True)

# --- 1. CONFIG & STYLING ---
st.set_page_config(layout="wide", page_title="Börsen-Wetter Terminal")
st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    h1, h2, p, span, div { color: #e0e0e0 !important; font-family: 'Courier New', monospace; }
    [data-testid="stMetricValue"] { font-size: 22px !important; color: #ffffff !important; }
    .product-label { font-size: 18px !important; font-weight: bold; color: #00ff00 !important; }
    .focus-header { color: #888888 !important; font-weight: bold; margin-top: 25px; border-bottom: 1px solid #444; }
    .header-time { color: #00ff00 !important; font-size: 32px !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SESSION STATE ---
if 'initial_values' not in st.session_state:
    st.session_state.initial_values = {}
if 'triggered_breakouts' not in st.session_state:
    st.session_state.triggered_breakouts = set()
if 'breakout_history' not in st.session_state:
    st.session_state.breakout_history = []
if 'session_start' not in st.session_state:
    st.session_state.session_start = (datetime.now() + timedelta(hours=1)).strftime('%H:%M:%S')

# --- 3. LOGIK ---
def get_weather_info(delta):
    if delta > 0.5: return "☀️", "SONNIG", "🟢", "BUY"
    elif delta >= 0: return "🌤️", "HEITER", "🟢", "BULL"
    elif delta > -0.5: return "☁️", "WOLKIG", "⚪", "WAIT"
    else: return "⛈️", "GEWITTER", "🔴", "SELL"

def fetch_data():
    symbols = {
        "EURUSD=X": "EUR/USD", "^STOXX50E": "EUROSTOXX 50", "^IXIC": "NASDAQ",
        "^CRSLDX": "NIFTY 500 (IN)", "XUTUM.IS": "BIST ALL (TR)",
        "AAPL": "APPLE", "MSFT": "MICROSOFT", "AMZN": "AMAZON", "NVDA": "NVIDIA", 
        "GOOGL": "ALPHABET", "META": "META", "TSLA": "TSLA",
        "ASML": "ASML", "MC.PA": "LVMH", "SAP.DE": "SAP", "NOVO-B.CO": "NOVO NORDISK"
    }
    results = {}
    aktuell = datetime.now() + timedelta(hours=1)
    st.session_state.last_update = aktuell.strftime('%H:%M:%S')
    
    for ticker, label in symbols.items():
        try:
            t = yf.Ticker(ticker)
            df = t.history(period="5d") 
            if len(df) >= 2:
                curr = df['Close'].iloc[-1]
                prev_high = df['High'].iloc[-2]
                is_breakout = curr > prev_high
                
                # Alarm-Ausschluss (kein Alarm für Indizes/FX)
                is_index_or_fx = any(x in ticker for x in ["X", "^", ".IS"])

                if is_breakout and label not in st.session_state.triggered_breakouts and not is_index_or_fx:
                    st.session_state.triggered_breakouts.add(label)
                    st.session_state.breakout_history.append({"Zeit": st.session_state.last_update, "Aktie": label, "Preis": f"{curr:.2f}"})
                    play_alarm()
                
                if label not in st.session_state.initial_values:
                    st.session_state.initial_values[label] = curr
                
                delta = ((curr - st.session_state.initial_values[label]) / st.session_state.initial_values[label]) * 100
                w_icon, w_txt, a_icon, a_txt = get_weather_info(delta)
                results[label] = {"price": curr, "prev_high": prev_high, "is_breakout": is_breakout, "delta": delta, "w": w_icon, "wt": w_txt, "a": a_icon, "at": a_txt}
        except: pass
    return results

def render_row(label, d, f_str="{:.2f}"):
    if not d: return
    border_col = "#00ff00" if d['is_breakout'] else "#333"
    with st.container():
        st.markdown(f"<div style='padding: 12px; border-radius: 10px; border: 1px solid {border_col}; border-left: 6px solid {border_col}; margin-bottom: 12px;'>", unsafe_allow_html=True)
        cols = st.columns([0.6, 0.6, 1.2, 1.4, 1.4])
        cols[0].markdown(f"{d['w']}<br><span style='font-size:9px;'>{d['wt']}</span>", unsafe_allow_html=True)
        cols[1].markdown(f"{d['a']}<br><span style='font-size:9px;'>{d['at']}</span>", unsafe_allow_html=True)
        cols[2].metric("", f_str.format(d['price']), f"{d['delta']:+.3f}%")
        cols[3].markdown(f"<span style='color:{'#00ff00' if d['is_breakout'] else '#666'};'>{'🚀 BREAKOUT' if d['is_breakout'] else 'Target'}: {d['prev_high']:.2f}</span>", unsafe_allow_html=True)
        cols[4].markdown(f"<p class='product-label'>{label}</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# --- 4. DISPLAY ---
data = fetch_data()
st.markdown(f"<h1>📡 TERMINAL <span style='float:right;' class='header-time'>{st.session_state.last_update}</span></h1>", unsafe_allow_html=True)

st.markdown("<p class='focus-header'>🌍 GLOBAL MACRO FOCUS</p>", unsafe_allow_html=True)
render_row("EUR/USD", data.get("EUR/USD"), "{:.6f}")
render_row("EUROSTOXX 50", data.get("EUROSTOXX 50"))
render_row("NASDAQ", data.get("NASDAQ"))

st.markdown("<p class='focus-header'>📈 EMERGING MARKETS FOCUS</p>", unsafe_allow_html=True)
render_row("NIFTY 500 (IN)", data.get("NIFTY 500 (IN)"))
render_row("BIST ALL (TR)", data.get("BIST ALL (TR)"))

st.markdown("<p class='focus-header'>🚀 AKTIVE BREAKOUTS</p>", unsafe_allow_html=True)
for k, v in data.items():
    if v['is_breakout'] and k not in ["EUR/USD", "EUROSTOXX 50", "NASDAQ", "NIFTY 500 (IN)", "BIST ALL (TR)"]:
        render_row(k, v)
