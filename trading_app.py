import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd

# --- 1. CONFIG & STYLING ---
st.set_page_config(layout="wide", page_title="Börsen-Wetter Terminal")

st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    div[data-testid="stSlider"] { display: none !important; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    h1, h2, h3, p, span, label, div {
        color: #e0e0e0 !important;
        font-family: 'Courier New', Courier, monospace;
    }
    [data-testid="stMetricValue"] { font-size: 24px !important; color: #ffffff !important; }
    [data-testid="stMetricDelta"] { font-size: 16px !important; }
    .effektiver-wert { font-size: 14px; color: #aaaaaa; margin-top: -15px; font-weight: bold; }
    .weather-icon { font-size: 24px !important; margin: 0; }
    .product-label { font-size: 22px !important; font-weight: bold; color: #00ff00 !important; margin-left: -25px; }
    .focus-header { color: #888888 !important; font-weight: bold; margin-top: 15px; }
    .log-container { background-color: #111; border: 1px solid #444; padding: 10px; border-radius: 5px; }
    .legend-box { background-color: #0e1117; border: 2px solid #00ff00; padding: 15px; border-radius: 10px; }
    .pos-val { color: #00ff00; font-weight: bold; }
    .neg-val { color: #ff4b4b; font-weight: bold; }
    hr { border-top: 1px solid #444; margin: 10px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SESSION STATE (Für Protokollierung) ---
if 'initial_values' not in st.session_state:
    st.session_state.initial_values = {}
if 'history_log' not in st.session_state:
    st.session_state.history_log = []

# --- 3. LOGIK ---
def get_weather_info(delta):
    if delta > 0.5: return "☀️", "SONNIG", "🟢", "BUY"
    elif delta >= 0: return "🌤️", "HEITER", "🟢", "BULL"
    elif delta > -0.5: return "☁️", "WOLKIG", "⚪", "WAIT"
    else: return "⛈️", "GEWITTER", "🔴", "SELL"

def fetch_data():
    symbols = {"EUR/USD": "EURUSD=X", "EUROSTOXX": "^STOXX50E", "S&P 500": "^GSPC", "APPLE": "AAPL", "MICROSOFT": "MSFT"}
    results = {}
    current_time = datetime.now().strftime('%H:%M:%S')
    
    for label, ticker in symbols.items():
        try:
            t = yf.Ticker(ticker)
            df = t.history(period="1d")
            if not df.empty:
                curr = df['Close'].iloc[-1]
                if label not in st.session_state.initial_values:
                    st.session_state.initial_values[label] = curr
                
                start = st.session_state.initial_values[label]
                diff = curr - start
                delta = (diff / start) * 100
                w_icon, w_txt, a_icon, a_txt = get_weather_info(delta)
                
                results[label] = {"price": curr, "delta": delta, "diff": diff, "start": start, "w": w_icon, "wt": w_txt, "a": a_icon, "at": a_txt}
                
                # Protokoll-Eintrag hinzufügen
                st.session_state.history_log.append({
                    "Zeit": current_time,
                    "Asset": label,
                    "Preis": f"{curr:.6f}" if label == "EUR/USD" else f"{curr:.2f}",
                    "Veränderung": f"{diff:+.6f}" if label == "EUR/USD" else f"{diff:+.6f}",
                    "Prozent": f"{delta:+.3f}%"
                })
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
    with cols[4]: 
        st.metric(label="", value=f_str.format(d['price']), delta=f"{d['delta']:+.3f}%")
        color_class = "pos-val" if d['diff'] >= 0 else "neg-val"
        st.markdown(f"<p class='effektiver-wert'>Absolut: <span class='{color_class}'>{d['diff']:+.6f if label == 'EUR/USD' else d['diff']:+.4f}</span></p>", unsafe_allow_html=True)
    with cols[5]: st.markdown(f"<p class='product-label'>{label}</p>", unsafe_allow_html=True)

# --- 5. HEADER ---
h1, h2 = st.columns([2, 1])
with h1: st.title("☁️ TERMINAL")
with h2: 
    st.markdown(f"<div style='text-align:right;'><p style='margin:0; color:#00ff00;'>LETZTES UPDATE (KORR.):</p><h3 style='margin:0;'>{now.strftime('%H:%M:%S')}</h3></div>", unsafe_allow_html=True)

st.markdown("---")

# --- 6. FOCUS / CURRENCIES & INDICES ---
st.markdown("<p class='focus-header'>### 🌍 FOCUS / CURRENCIES & INDICES</p>", unsafe_allow_html=True)

# --- NEU: PROTOKOLL EXPANDER ---
with st.expander("📊 PROTOKOLLIERUNG DER VERÄNDERUNG EINBLENDEN (Sitzungsbeginn bis aktuell)"):
    if st.session_state.history_log:
        log_df = pd.DataFrame(st.session_state.history_log).tail(20) # Zeigt letzte 20 Einträge
        st.table(log_df)
    else:
        st.write("Warte auf Dateneingang...")

if "EUR/USD" in data:
    render_row("EUR/USD", data["EUR/USD"], "{:.6f}") 
if "EUROSTOXX" in data:
    render_row("EUROSTOXX 50", data["EUROSTOXX"])
if "S&P 500" in data:
    render_row("S&P 500", data["S&P 500"])

st.markdown("<hr>", unsafe_allow_html=True)

# --- 7. STOCKS / EQUITIES ---
st.markdown("<p class='focus-header'>### 🍏 SELECTED EQUITIES</p>", unsafe_allow_html=True)

if "APPLE" in data:
    render_row("APPLE INC.", data["APPLE"])
if "MICROSOFT" in data:
    render_row("MICROSOFT CORP.", data["MICROSOFT"])

# --- 8. SIDEBAR ---
with st.sidebar:
    st.markdown("### 🗺️ LEGEND")
    st.markdown("""<div class='legend-box'>... (wie bisher) ...</div>""", unsafe_allow_html=True)
    if st.button("🔄 MANUAL REFRESH"):
        st.rerun()

