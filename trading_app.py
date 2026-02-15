import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta
import time

# --- 1. CONFIG & STYLING (Stabilisierte Größen) ---
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
    .product-label { font-size: 20px !important; font-weight: bold; color: #00ff00 !important; margin-left: -20px; }
    .focus-header { color: #888888 !important; font-weight: bold; margin-bottom: 5px; margin-top: 10px; }
    hr { border-top: 1px solid #333; margin: 8px 0; }
    /* Style für den neuen Beschreibungsblock */
    .info-block { border: 1px solid #444; padding: 15px; background-color: #111; border-radius: 5px; }
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

# --- 4. ZEILEN-AUFBAU (Kurs und Name eng beieinander) ---
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

# --- 6. ANZEIGE ---
st.markdown("<p class='focus-header'>### 🌍 FOCUS/ WÄHRUNG</p>", unsafe_allow_html=True)
render_row("EUR/USD", data.get("EUR/USD"), "{:.4f}")

st.markdown("---")

st.markdown("<p class='focus-header'>### 📈 FOCUS/ INDIZES</p>", unsafe_allow_html=True)
render_row("EUROSTOXX", data.get("EUROSTOXX"))
render_row("S&P 500", data.get("S&P 500"))

# DER SLIDER (wie gehabt unter den Indizes)
st.write("")
update_sec = st.slider("Update-Intervall (Sekunden):", 10, 300, 60, key="main_slider")

st.markdown("---")

st.markdown("<p class='focus-header'>### 🍎 FOCUS/ AKTIEN</p>", unsafe_allow_html=True)
render_row("APPLE", data.get("APPLE"))
render_row("MICROSOFT", data.get("MICROSOFT"))

st.markdown("---")

# --- 7. ERGÄNZUNG UNTEN: BESCHREIBUNG INFORMATION ---
st.subheader("📝 BESCHREIBUNG DER SYMBOLE & INFORMATION")
with st.container():
    st.markdown("<div class='info-block'>", unsafe_allow_html=True)
    c_info1, c_info2 = st.columns(2)
    with c_info1:
        st.write("**Bedeutung Wetter & Signale:**")
        st.write("☀️ **Sonnig**: Starker Trend (> 0.5%) | 🌤️ **Heiter**: Positiv (>= 0%)")
        st.write("☁️ **Wolkig**: Leicht negativ | ⛈️ **Gewitter**: Starker Abfall (< -0.5%)")
        st.write("🟢 **BUY**: Kaufsignal | 🔴 **SELL**: Verkaufssignal | ⚪ **WAIT**: Neutral")
    with c_info2:
        st.write("**Session-Dokumentation (Startkurse):**")
        for label, values in data.items():
            if values:
                st.write(f"• {label}: Startwert `{values['start']:.4f}`")
    st.markdown("</div>", unsafe_allow_html=True)

# --- 8. REFRESH ---
time.sleep(update_sec)
st.rerun()
