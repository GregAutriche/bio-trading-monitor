import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta
import time

# --- 1. CONFIG & STYLING (Größen angepasst) ---
st.set_page_config(layout="wide", page_title="Börsen-Wetter Terminal")

st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    h1, h2, h3, p, span, label, div {
        color: #e0e0e0 !important;
        font-family: 'Courier New', Courier, monospace;
    }
    /* Metriken */
    [data-testid="stMetricValue"] { font-size: 28px !important; color: #ffffff !important; }
    [data-testid="stMetricDelta"] { font-size: 18px !important; }
    
    /* Symbole kleiner machen */
    .weather-icon { font-size: 24px !important; margin: 0; }
    
    /* Produktbezeichnung kleiner */
    .product-label { font-size: 20px !important; font-weight: bold; color: #00ff00 !important; }
    
    hr { border-top: 1px solid #333; margin: 10px 0; }
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
                res = {"price": curr, "delta": delta, "w": w_icon, "wt": w_txt, "a": a_icon, "at": a_txt}
                results[label] = res
                st.session_state.last_valid[label] = res
            else: results[label] = st.session_state.last_valid.get(label)
        except: results[label] = st.session_state.last_valid.get(label)
    return results

data = fetch_data()
now = datetime.now() - timedelta(hours=1)

# --- 4. ZEILEN-AUFBAU (Reihenfolge: Wetter -> Action -> Kurs -> Name) ---
def render_row(label, d, f_str="{:.2f}"):
    if not d: return
    cols = st.columns([0.5, 1, 0.5, 1, 3, 2])
    with cols[0]: st.markdown(f"<p class='weather-icon'>{d['w']}</p>", unsafe_allow_html=True)
    with cols[1]: st.write(f"{d['wt']}")
    with cols[2]: st.markdown(f"<p class='weather-icon'>{d['a']}</p>", unsafe_allow_html=True)
    with cols[3]: st.write(f"{d['at']}")
    with cols[4]: st.metric(label="Session", value=f_str.format(d['price']), delta=f"{d['delta']:+.4f}%")
    with cols[5]: st.markdown(f"<p class='product-label'>{label}</p>", unsafe_allow_html=True)

# --- 5. HEADER ---
h1, h2 = st.columns([2, 1])
with h1: st.subheader("☁️ BÖRSEN-WETTER")
with h2: st.markdown(f"<div style='text-align:right;'><h3 style='color:#00ff00;margin:0;'>{now.strftime('%H:%M:%S')}</h3><small>{now.strftime('%d.%m.%Y')}</small></div>", unsafe_allow_html=True)

st.markdown("---")

# --- 6. ANZEIGE ---
render_row("EUR/USD", data.get("EUR/USD"), "{:.4f}")
st.markdown("---")
render_row("EUROSTOXX", data.get("EUROSTOXX"))
render_row("S&P 500", data.get("S&P 500"))

# --- SLIDER (Fest unter den Indizes platziert) ---
st.write("")
update_sec = st.slider("UPDATE INTERVALL (SEK):", 10, 300, 60)
st.markdown("---")

render_row("APPLE", data.get("APPLE"))
render_row("MICROSOFT", data.get("MICROSOFT"))

# --- 7. REFRESH ---
time.sleep(update_sec)
st.rerun()
