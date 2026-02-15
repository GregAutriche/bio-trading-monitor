import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta
import time

# --- 1. CONFIG & STYLING ---
st.set_page_config(layout="wide", page_title="Börsen-Wetter Terminal")

st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    h1, h2, h3, p, span, label, div {
        color: #e0e0e0 !important;
        font-family: 'Courier New', Courier, monospace;
    }
    [data-testid="stMetricValue"] { font-size: 24px !important; color: #ffffff !important; }
    .weather-icon { font-size: 22px !important; margin: 0; display: inline; }
    .product-label { font-size: 20px !important; font-weight: bold; color: #00ff00 !important; margin-left: -25px; }
    .focus-header { color: #888888 !important; font-weight: bold; margin-bottom: 5px; margin-top: 10px; }
    .log-box { border-left: 3px solid #00ff00; padding-left: 15px; background-color: #111; margin: 10px 0; }
    hr { border-top: 1px solid #333; margin: 8px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SESSION STATE ---
if 'initial_values' not in st.session_state:
    st.session_state.initial_values = {}
if 'last_valid' not in st.session_state:
    st.session_state.last_valid = {}

# --- 3. LOGIK ---
def get_weather_info(delta):
    if delta > 0.5: return "☀️", "SONNIG", "🟢", "BUY"
    elif delta >= 0: return "🌤️", "HEITER", "🟢", "BULL"
    elif delta > -0.5: return "☁️", "WOLKIG", "⚪", "WAIT"
    else: return "⛈️", "GEWITTER", "🔴", "SELL"

def fetch_data():
    symbols = {"EUR/USD": "EURUSD=X", "EUROSTOXX": "^STOXX50E", "S&P 500": "^GSPC", "APPLE": "AAPL", "MICROSOFT": "MSFT"}
    results = {}
    for label, ticker in symbols.items():
        try:
            t = yf.Ticker(ticker)
            df = t.history(period="1d")
            if not df.empty:
                curr = df['Close'].iloc[-1]
                if label not in st.session_state.initial_values:
                    st.session_state.initial_values[label] = curr
                start = st.session_state.initial_values[label]
                delta = ((curr - start) / start) * 100
                w_icon, w_txt, a_icon, a_txt = get_weather_info(delta)
                res = {"price": curr, "delta": delta, "start": start, "w": w_icon, "wt": w_txt, "a": a_icon, "at": a_txt}
                results[label] = res
                st.session_state.last_valid[label] = res
            else: results[label] = st.session_state.last_valid.get(label)
        except: results[label] = st.session_state.last_valid.get(label)
    return results

data = fetch_data()
now = datetime.now() - timedelta(hours=1)

# --- 4. ZEILEN-AUFBAU ---
def render_row(label, d, f_str="{:.2f}"):
    if not d: return
    cols = st.columns([0.4, 0.8, 0.4, 0.8, 1.5, 2.0])
    with cols[0]: st.markdown(f"<p class='weather-icon'>{d['w']}</p>", unsafe_allow_html=True)
    with cols[1]: st.write(f"{d['wt']}")
    with cols[2]: st.markdown(f"<p class='weather-icon'>{d['a']}</p>", unsafe_allow_html=True)
    with cols[3]: st.write(f"{d['at']}")
    with cols[4]: st.metric(label="", value=f_str.format(d['price']), delta=f"{d['delta']:+.3f}%")
    with cols[5]: st.markdown(f"<p class='product-label'>{label}</p>", unsafe_allow_html=True)

# --- 5. HEADER ---
h1, h2 = st.columns([2, 1])
with h1: st.title("☁️ BÖRSEN-WETTER")
with h2: 
    st.markdown(f"<div style='text-align:right;'><p style='margin:0; color:#00ff00;'>Letztes Update:</p><h3 style='margin:0;'>{now.strftime('%H:%M:%S')}</h3><small>{now.strftime('%d.%m.%Y')}</small></div>", unsafe_allow_html=True)

st.markdown("---")

# --- 6. SEKTION WÄHRUNG & INDIZES ---
st.markdown("<p class='focus-header'>### 🌍 FOCUS/ WÄHRUNG</p>", unsafe_allow_html=True)
render_row("EUR/USD", data.get("EUR/USD"), "{:.4f}")

st.markdown("---")

st.markdown("<p class='focus-header'>### 📈 FOCUS/ INDIZES</p>", unsafe_allow_html=True)
render_row("EUROSTOXX", data.get("EUROSTOXX"))
render_row("S&P 500", data.get("S&P 500"))

# --- SLIDER 1: PROTOKOLLIERUNG DER VERÄNDERUNG ---
st.write("")
show_log = st.slider("PROTOKOLLIERUNG DER VERÄNDERUNG (Details einblenden):", 0, 1, 1, key="slider_log")
if show_log:
    with st.container():
        st.markdown("<div class='log-box'>", unsafe_allow_html=True)
        st.write("**Session-Protokoll (Start vs. Aktuell):**")
        c_log = st.columns(len(data))
        for i, (name, vals) in enumerate(data.items()):
            if vals:
                c_log[i].caption(f"{name}")
                c_log[i].code(f"S: {vals['start']:.2f}\nA: {vals['price']:.2f}")
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# --- 7. SEKTION AKTIEN ---
st.markdown("<p class='focus-header'>### 🍎 FOCUS/ AKTIEN</p>", unsafe_allow_html=True)
render_row("APPLE", data.get("APPLE"))
render_row("MICROSOFT", data.get("MICROSOFT"))

# --- SLIDER 2: BESCHREIBUNG SYMBOLE & INFO ---
st.write("")
show_desc = st.slider("BESCHREIBUNG DER SYMBOLE & INFORMATION (Details einblenden):", 0, 1, 1, key="slider_desc")
if show_desc:
    with st.container():
        st.info("**LEGENDE:** ☀️ >0.5% | 🌤️ >0% | ☁️ <0% | ⛈️ <-0.5%  ---  🟢 BUY | 🔴 SELL | ⚪ WAIT")

# --- 8. REFRESH LOGIK ---
# Festes Update-Intervall (z.B. 60 Sek), da Slider nun Funktionen steuern
time.sleep(60)
st.rerun()
