import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta
import time

# --- 1. CONFIG ---
st.set_page_config(layout="wide", page_title="Börsen-Wetter Terminal")

# CSS für maximale Sichtbarkeit auf dem Projektor
st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    h1, h2, h3, p, span, label, div {
        color: #e0e0e0 !important;
        font-family: 'Courier New', Courier, monospace;
    }
    /* Macht die Metriken und Icons auf der Leinwand größer */
    [data-testid="stMetricValue"] { font-size: 40px !important; color: #ffffff !important; }
    [data-testid="stMetricDelta"] { font-size: 24px !important; }
    .big-icon { font-size: 50px !important; }
    hr { border-top: 1px solid #444; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SESSION STATE ---
if 'initial_values' not in st.session_state:
    st.session_state.initial_values = {}

# --- 3. LOGIK ---
def get_weather_info(delta):
    # Logik für das IMMER-ANZEIGEN (auch bei 0)
    if delta > 0.5: return "☀️", "SONNIG", "🟢", "BUY"
    elif delta >= 0: return "🌤️", "HEITER", "🟢", "BULL"
    elif delta > -0.5: return "☁️", "WOLKIG", "⚪", "WAIT"
    else: return "⛈️", "GEWITTER", "🔴", "SELL"

def fetch_data():
    symbols = {
        "EUR/USD": "EURUSD=X", "EUROSTOXX": "^STOXX50E", 
        "S&P 500": "^GSPC", "APPLE": "AAPL", "MICROSOFT": "MSFT"
    }
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
                results[label] = {"price": curr, "delta": delta, "w": w_icon, "wt": w_txt, "a": a_icon, "at": a_txt}
        except: pass
    return results

data = fetch_data()
now = datetime.now() - timedelta(hours=1) # Zeit-Korrektur

# --- 4. ZEILEN-AUFBAU (Die besprochene Reihenfolge) ---
def render_weather_row(label, d, format_str="{:.2f}"):
    if not d: return
    # Spalten-Gewichtung für Projektor: Wetter(2) | Action(2) | Kurs(4) | Name(3)
    c1, c2, c3, c4, c5, c6 = st.columns([1, 1.5, 1, 1.5, 4, 3])
    with c1: st.markdown(f"<p class='big-icon'>{d['w']}</p>", unsafe_allow_html=True)
    with c2: st.markdown(f"### {d['wt']}")
    with c3: st.markdown(f"### {d['a']}")
    with c4: st.markdown(f"### {d['at']}")
    with c5: st.metric(label="Aktuell", value=format_str.format(d['price']), delta=f"{d['delta']:+.4f}%")
    with c6: st.markdown(f"## {label}")

# --- 5. HEADER ---
col_h1, col_h2 = st.columns([2, 1])
with col_h1: st.title("☁️ BÖRSEN-WETTER LIVE")
with col_h2:
    st.markdown(f"<div style='text-align:right;'><h2 style='color:#00ff00 !important;'>{now.strftime('%H:%M:%S')}</h2><p>{now.strftime('%d.%m.%Y')}</p></div>", unsafe_allow_html=True)

st.markdown("---")

# --- 6. SEKTIONEN ---
st.subheader("🌍 WÄHRUNGEN")
render_weather_row("EUR/USD", data.get("EUR/USD"), "{:.4f}")

st.markdown("---")
st.subheader("📈 INDIZES")
render_weather_row("EUROSTOXX", data.get("EUROSTOXX"))
render_weather_row("S&P 500", data.get("S&P 500"))

# DER SLIDER ALS ERGÄNZUNG UNTER DEN INDIZES
st.write("")
update_sec = st.slider("Update-Takt (Sekunden):", 10, 300, 60)
st.markdown("---")

st.subheader("🍎 AKTIEN")
render_weather_row("APPLE", data.get("APPLE"))
render_weather_row("MICROSOFT", data.get("MICROSOFT"))

# --- 7. REFRESH ---
time.sleep(update_sec)
st.rerun()
