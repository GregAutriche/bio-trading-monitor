import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta
import time

# --- 1. KONFIGURATION & STYLING (Projektor-Optimiert) ---
st.set_page_config(layout="wide", page_title="Börsen-Wetter Terminal")

st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    h1, h2, h3, p, span, label, div {
        color: #e0e0e0 !important;
        font-family: 'Courier New', Courier, monospace;
    }
    /* Große Metriken für die Leinwand */
    [data-testid="stMetricValue"] { font-size: 38px !important; color: #ffffff !important; font-weight: bold !important; }
    [data-testid="stMetricDelta"] { font-size: 22px !important; }
    .big-icon { font-size: 48px !important; margin: 0; padding: 0; }
    hr { border-top: 1px solid #444; }
    
    /* Slider Styling */
    .stSlider label { font-size: 20px !important; color: #00ff00 !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SESSION STATE (Startwerte für Session-Vergleich) ---
if 'initial_values' not in st.session_state:
    st.session_state.initial_values = {}
if 'last_valid_data' not in st.session_state:
    st.session_state.last_valid_data = {}

# --- 3. WETTER- & DATEN-LOGIK ---
def get_weather_info(delta):
    # Logik für das IMMER-ANZEIGEN (auch bei Start = 0)
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
                # Startwert beim ersten Ausführen fixieren
                if label not in st.session_state.initial_values:
                    st.session_state.initial_values[label] = curr
                
                start = st.session_state.initial_values[label]
                delta = ((curr - start) / start) * 100
                w_icon, w_txt, a_icon, a_txt = get_weather_info(delta)
                
                res = {
                    "price": curr, "delta": delta, "start": start,
                    "w": w_icon, "wt": w_txt, "a": a_icon, "at": a_txt
                }
                results[label] = res
                st.session_state.last_valid_data[label] = res
            else:
                results[label] = st.session_state.last_valid_data.get(label)
        except:
            results[label] = st.session_state.last_valid_data.get(label)
    return results

# Daten laden & Zeitkorrektur (-1 Stunde)
data = fetch_data()
now = datetime.now() - timedelta(hours=1)

# --- 4. ZEILEN-AUFBAU (Hierarchie: Wetter -> Action -> Kurs -> Name) ---
def render_weather_row(label, d, format_str="{:.2f}"):
    if not d: return
    # Spaltenaufteilung: Wetter(2) | Action(2) | Kurs/Delta(4) | Produktname(3)
    c1, c2, c3, c4, c5, c6 = st.columns([0.8, 1.2, 0.8, 1.2, 4, 3])
    with c1: st.markdown(f"<p class='big-icon'>{d['w']}</p>", unsafe_allow_html=True)
    with c2: st.write(f"### {d['wt']}")
    with c3: st.markdown(f"<p class='big-icon'>{d['a']}</p>", unsafe_allow_html=True)
    with c4: st.write(f"### {d['at']}")
    with c5: st.metric(label="Session-Kurs", value=format_str.format(d['price']), delta=f"{d['delta']:+.4f}%")
    with c6: st.write(f"## {label}")

# --- 5. HEADER (Zeitkorrektur integriert) ---
h_col1, h_col2 = st.columns([2, 1])
with h_col1: 
    st.title("☁️ BÖRSEN-WETTER TERMINAL")
with h_col2:
    st.markdown(f"""
        <div style='text-align:right; border-right: 5px solid #00ff00; padding-right: 15px;'>
            <h2 style='color:#00ff00 !important; margin:0;'>{now.strftime('%H:%M:%S')}</h2>
            <p style='margin:0; opacity: 0.7;'>{now.strftime('%d.%m.%Y')} LIVE</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# --- 6. ANZEIGE DER SEKTIONEN ---

# 1. Währung
st.subheader("🌍 WÄHRUNG")
render_weather_row("EUR/USD", data.get("EUR/USD"), "{:.4f}")

st.markdown("---")

# 2. Indizes
st.subheader("📈 INDIZES")
render_weather_row("EUROSTOXX", data.get("EUROSTOXX"))
render_weather_row("S&P 500", data.get("S&P 500"))

# 3. ERGÄNZUNG: SLIDER & SESSION-INFO (Zentral platziert)
st.write("")
with st.container():
    # Klappbarer Bereich für die Startwerte
    with st.expander("📊 SESSION-DETAILS (STARTWERTE VERGLEICH)"):
        cols_info = st.columns(len(data))
        for i, (name, vals) in enumerate(data.items()):
            if vals:
                cols_info[i].write(f"**{name}**")
                cols_info[i].info(f"Start: {vals['start']:.4f}")

    # Der Slider zur Intervallsteuerung
    update_sec = st.slider("UPDATE-INTERVALL (SEKUNDEN):", 10, 300, 60)
    st.caption(f"Aktualisierung erfolgt alle {update_sec} Sekunden.")

st.markdown("---")

# 4. Aktien
st.subheader("🍎 AKTIEN")
render_weather_row("APPLE", data.get("APPLE"))
render_weather_row("MICROSOFT", data.get("MICROSOFT"))

# --- 7. AUTOMATISCHER REFRESH ---
time.sleep(update_sec)
st.rerun()
