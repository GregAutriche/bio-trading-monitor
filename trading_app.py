import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd

# --- 1. CONFIG & STYLING ---
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
    .product-label { font-size: 20px !important; font-weight: bold; color: #00ff00 !important; margin-left: -20px; }
    .focus-header { color: #888888 !important; font-weight: bold; margin-top: 20px; border-bottom: 1px solid #444; }
    
    .pos-val { color: #00ff00; font-weight: bold; }
    .neg-val { color: #ff4b4b; font-weight: bold; }
    hr { border-top: 1px solid #444; margin: 10px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SESSION STATE ---
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
    symbols = {
        "e/u": "EURUSD=X", "e-stox": "^STOXX50E", "^GSPC": "S&P 500",
        "AAPL": "APPLE", "MSFT": "MICROSOFT", "AMZN": "AMAZON", "NVDA": "NVIDIA", "GOOGL": "ALPHABET", "META": "META", "TSLA": "TESLA",
        "ASML": "ASML", "MC.PA": "LVMH", "SAP.DE": "SAP", "SIE.DE": "SIEMENS", "TTE.PA": "TOTALENERGIES", "ALV.DE": "ALLIANZ", "OR.PA": "L'OREAL"
    }
    results = {}
    current_time = datetime.now().strftime('%H:%M:%S')
    
    for ticker, label in symbols.items():
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
                
                # Nur loggen wenn sich wirklich was verändert hat (optional)
                st.session_state.history_log.append({
                    "Zeit": current_time, "Asset": label, "Betrag": f"{curr:.6f}" if "USD" in label else f"{curr:.2f}",
                    "Veränderung": f"{diff:+.6f}" if "USD" in label else f"{diff:+.4f}", "Anteil %": f"{delta:+.3f}%"
                })
        except: pass
    return results

data = fetch_data()
now_display = datetime.now() - timedelta(hours=1)
datum_heute = datetime.now().strftime('%d.%m.%Y')

# --- 4. ZEILEN-AUFBAU ---
def render_row(label, d, f_str="{:.2f}"):
    if not d: return
    cols = st.columns([0.4, 0.8, 0.4, 0.8, 1.5, 2.0])
    with cols[0]: st.write(d['w'])
    with cols[1]: st.write(d['wt'])
    with cols[2]: st.write(d['a'])
    with cols[3]: st.write(d['at'])
    with cols[4]: 
        st.metric(label="", value=f_str.format(d['price']), delta=f"{d['delta']:+.3f}%")
        color_class = "pos-val" if d['diff'] >= 0 else "neg-val"
        diff_fmt = f"{d['diff']:+.6f}" if "USD" in label else f"{d['diff']:+.4f}"
        st.markdown(f"<p class='effektiver-wert'>Absolut: <span class='{color_class}'>{diff_fmt}</span></p>", unsafe_allow_html=True)
    with cols[5]: st.markdown(f"<p class='product-label'>{label}</p>", unsafe_allow_html=True)

# --- 5. HEADER ---
h1, h2 = st.columns([2, 1])
with h1: st.title("☁️ BÖRSEN-WETTER")
with h2: 
    st.markdown(f"<div style='text-align:right;'><p style='margin:0; color:#888888;'>{datum_heute}</p><h3 style='margin:0; color:#00ff00;'>{now_display.strftime('%H:%M:%S')}</h3></div>", unsafe_allow_html=True)

# --- 6. MAIN FOCUS (Währung & Indizes) ---
st.markdown("<p class='focus-header'>### 🌍 GLOBAL MACRO FOCUS</p>", unsafe_allow_html=True)

# Protokoll-Fenster
with st.expander("📊 PROTOKOLLIERUNG DER VERÄNDERUNG EINBLENDEN"):
    if st.session_state.history_log:
        st.table(pd.DataFrame(st.session_state.history_log).iloc[::-1].head(15))

# EUR/USD ANZEIGE-FIX
# Wir suchen explizit nach dem Schlüssel "EUR/USD"
eur_data = data.get("EUR/USD")

if eur_data:
    render_row("EUR/USD", eur_data, "{:.6f}")
else:
    # Das ist die Meldung, die du im letzten Bild siehst. 
    # Wenn das erscheint, konnte yfinance den Kurs "EURUSD=X" nicht abrufen.
    st.warning("⚠️ EUR/USD Daten aktuell nicht verfügbar (Ticker: EURUSD=X)")

# Indizes folgen darunter
if "EUROSTOXX 50" in data:
    render_row("EUROSTOXX 50", data["EUROSTOXX 50"])

if "S&P 500" in data:
    render_row("S&P 500", data["S&P 500"])
st.markdown("<hr>", unsafe_allow_html=True)

# --- 7. US DERIVATIVES (7 SELECTED) ---
st.markdown("<p class='focus-header'>### 🇺🇸 US MARKET DERIVATIVES</p>", unsafe_allow_html=True)
us_list = ["APPLE", "MICROSOFT", "AMAZON", "NVIDIA", "ALPHABET", "META", "TESLA"]
for asset in us_list: render_row(asset, data.get(asset))

# --- 8. EU DERIVATIVES (7 SELECTED) ---
st.markdown("<p class='focus-header'>### 🇪🇺 EU MARKET DERIVATIVES</p>", unsafe_allow_html=True)
eu_list = ["ASML", "LVMH", "SAP", "SIEMENS", "TOTALENERGIES", "ALLIANZ", "L'OREAL"]
for asset in eu_list: render_row(asset, data.get(asset))

with st.sidebar:
    if st.button("🔄 MANUAL REFRESH"): st.rerun()











