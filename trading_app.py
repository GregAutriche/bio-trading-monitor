import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd

# --- 1. CONFIG & STYLING (Bleibt unverändert) ---
st.set_page_config(layout="wide", page_title="Börsen-Wetter Terminal")

st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    div[data-testid="stSlider"], .stSlider { display: none !important; }
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
    
    .stTable { background-color: #050505; color: #e0e0e0; }
    hr { border-top: 1px solid #444; margin: 10px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SESSION STATE ---
if 'initial_values' not in st.session_state:
    st.session_state.initial_values = {}
if 'history_log' not in st.session_state:
    st.session_state.history_log = []

# --- 3. LOGIK (Zieht nun die 7 US und 7 EU Werte) ---
def get_weather_info(delta):
    if delta > 0.5: return "☀️", "SONNIG", "🟢", "BUY"
    elif delta >= 0: return "🌤️", "HEITER", "🟢", "BULL"
    elif delta > -0.5: return "☁️", "WOLKIG", "⚪", "WAIT"
    else: return "⛈️", "GEWITTER", "🔴", "SELL"

def fetch_data():
    # Definition der 7 US und 7 EU Werte als Index-Ableitungen
    symbols = {
        # 7x USA
        "APPLE": "AAPL", "MICROSOFT": "MSFT", "AMAZON": "AMZN", 
        "NVIDIA": "NVDA", "ALPHABET": "GOOGL", "META": "META", "TESLA": "TSLA",
        # 7x EUROPA
        "ASML": "ASML", "LVMH": "MC.PA", "SAP": "SAP.DE", 
        "SIEMENS": "SIE.DE", "TOTALENERGIES": "TTE.PA", "ALLIANZ": "ALV.DE", "L'OREAL": "OR.PA"
    }
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
                
                results[label] = {"price": curr, "delta": delta, "diff": diff, "w": w_icon, "wt": w_txt, "a": a_icon, "at": a_txt}
                
                st.session_state.history_log.append({
                    "Zeit": current_time,
                    "Asset": label,
                    "Betrag": f"{curr:.2f}",
                    "Veränderung": f"{diff:+.4f}",
                    "Anteil %": f"{delta:+.3f}%"
                })
        except: pass
    return results

data = fetch_data()
now_display = datetime.now() - timedelta(hours=1)
datum_heute = datetime.now().strftime('%d.%m.%Y')

# --- 4. ZEILEN-AUFBAU ---
def render_row(label, d):
    if not d: return
    cols = st.columns([0.4, 0.8, 0.4, 0.8, 1.5, 2.0])
    with cols[0]: st.markdown(f"<p class='weather-icon'>{d['w']}</p>", unsafe_allow_html=True)
    with cols[1]: st.write(f"{d['wt']}")
    with cols[2]: st.markdown(f"<p class='weather-icon'>{d['a']}</p>", unsafe_allow_html=True)
    with cols[3]: st.write(f"{d['at']}")
    with cols[4]: 
        st.metric(label="", value=f"{d['price']:.2f}", delta=f"{d['delta']:+.3f}%")
        color_class = "pos-val" if d['diff'] >= 0 else "neg-val"
        st.markdown(f"<p class='effektiver-wert'>Absolut: <span class='{color_class}'>{d['diff']:+.4f}</span></p>", unsafe_allow_html=True)
    with cols[5]: st.markdown(f"<p class='product-label'>{label}</p>", unsafe_allow_html=True)

# --- 5. HEADER (Mit Datum & Zeit) ---
h1, h2 = st.columns([2, 1])
with h1: st.title("☁️ BÖRSEN-WETTER")
with h2: 
    st.markdown(f"""
        <div style='text-align:right;'>
            <p style='margin:0; color:#888888; font-size:12px;'>STATUS: {datum_heute}</p>
            <h3 style='margin:0; color:#00ff00;'>{now_display.strftime('%H:%M:%S')}</h3>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# --- 6. ANZEIGE US & EU ---
st.markdown("<p class='focus-header'>### 🇺🇸 US MARKET DERIVATIVES (SELECTED 7)</p>", unsafe_allow_html=True)

with st.expander("📊 PROTOKOLLIERUNG DER VERÄNDERUNG EINBLENDEN"):
    if st.session_state.history_log:
        st.table(pd.DataFrame(st.session_state.history_log).iloc[::-1])

# US Sektion
us_list = ["APPLE", "MICROSOFT", "AMAZON", "NVIDIA", "ALPHABET", "META", "TESLA"]
for asset in us_list:
    render_row(asset, data.get(asset))

st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<p class='focus-header'>### 🇪🇺 EU MARKET DERIVATIVES (SELECTED 7)</p>", unsafe_allow_html=True)

# EU Sektion
eu_list = ["ASML", "LVMH", "SAP", "SIEMENS", "TOTALENERGIES", "ALLIANZ", "L'OREAL"]
for asset in eu_list:
    render_row(asset, data.get(asset))

# --- 8. SIDEBAR ---
with st.sidebar:
    if st.button("🔄 MANUAL REFRESH"):
        st.rerun()
