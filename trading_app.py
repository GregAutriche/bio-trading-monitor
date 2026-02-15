import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta
import time

# --- 1. CONFIG & CSS (Maximale Sichtbarkeit) ---
st.set_page_config(layout="wide", page_title="Börsen-Wetter Terminal")

st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    h1, h2, h3, p, span, label, div {
        color: #e0e0e0 !important;
        font-family: 'Courier New', Courier, monospace;
    }
    [data-testid="stMetricValue"] { font-size: 26px !important; color: #ffffff !important; }
    .weather-icon { font-size: 24px !important; margin: 0; }
    .product-label { font-size: 22px !important; font-weight: bold; color: #00ff00 !important; margin-left: -20px; }
    .focus-header { color: #aaaaaa !important; font-weight: bold; margin-top: 15px; text-transform: uppercase; }
    
    /* Protokoll Box */
    .log-container { background-color: #111; border: 1px solid #444; padding: 10px; border-radius: 5px; }
    .pos-val { color: #00ff00; font-weight: bold; }
    .neg-val { color: #ff4b4b; font-weight: bold; }
    
    /* Legende Box */
    .legend-box { background-color: #0e1117; border: 2px solid #00ff00; padding: 15px; border-radius: 10px; }
    
    hr { border-top: 1px solid #444; margin: 10px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SESSION STATE ---
if 'initial_values' not in st.session_state:
    st.session_state.initial_values = {}

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
                results[label] = {"price": curr, "delta": delta, "start": start, "w": w_icon, "wt": w_txt, "a": a_icon, "at": a_txt}
        except: pass
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
    st.markdown(f"<div style='text-align:right;'><p style='margin:0; color:#00ff00;'>LETZTES UPDATE:</p><h3 style='margin:0;'>{now.strftime('%H:%M:%S')}</h3></div>", unsafe_allow_html=True)

st.markdown("---")

# --- 6. FOCUS/ WÄHRUNG & INDIZES ---
st.markdown("<p class='focus-header'>### 🌍 FOCUS/ WÄHRUNG</p>", unsafe_allow_html=True)
render_row("EUR/USD", data.get("EUR/USD"), "{:.4f}")

st.markdown("---")
st.markdown("<p class='focus-header'>### 📈 FOCUS/ INDIZES</p>", unsafe_allow_html=True)
render_row("EUROSTOXX", data.get("EUROSTOXX"))
render_row("S&P 500", data.get("S&P 500"))

# --- SLIDER 1 & PROTOKOLL ---
st.write("")
show_log = st.slider("PROTOKOLLIERUNG DER VERÄNDERUNG EINBLENDEN", 0, 1, 1)
if show_log:
    st.markdown("<div class='log-container'>", unsafe_allow_html=True)
    cols_log = st.columns(len(data))
    for i, (name, v) in enumerate(data.items()):
        color_class = "pos-val" if v['delta'] >= 0 else "neg-val"
        cols_log[i].markdown(f"**{name}**")
        cols_log[i].markdown(f"Start: `{v['start']:.2f}`")
        cols_log[i].markdown(f"Diff: <span class='{color_class}'>{v['delta']:+.2f}%</span>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# --- 7. FOCUS/ AKTIEN ---
st.markdown("<p class='focus-header'>### 🍎 FOCUS/ AKTIEN</p>", unsafe_allow_html=True)
render_row("APPLE", data.get("APPLE"))
render_row("MICROSOFT", data.get("MICROSOFT"))

# --- SLIDER 2 & BESCHREIBUNG ---
st.write("")
show_desc = st.slider("BESCHREIBUNG DER SYMBOLE & INFORMATION EINBLENDEN", 0, 1, 1)
if show_desc:
    st.markdown("""
    <div class='legend-box'>
        <table style='width:100%; border:none;'>
            <tr>
                <td>☀️ <b>SONNIG:</b> > +0.5%</td>
                <td>🌤️ <b>HEITER:</b> > 0%</td>
                <td>☁️ <b>WOLKIG:</b> < 0%</td>
                <td>⛈️ <b>GEWITTER:</b> < -0.5%</td>
            </tr>
            <tr>
                <td>🟢 <b>BUY/BULL:</b> Positiv</td>
                <td>🔴 <b>SELL/BEAR:</b> Negativ</td>
                <td>⚪ <b>WAIT:</b> Neutral</td>
                <td><b style='color:#00ff00;'>LIVE DATA ACTIVE</b></td>
            </tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

# --- 8. REFRESH ---
time.sleep(60)
st.rerun()
