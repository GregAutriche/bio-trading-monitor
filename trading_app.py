import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta
import time

# --- 1. CONFIG & CSS ---
st.set_page_config(layout="wide", page_title="Börsen-Wetter Terminal")

st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    h1, h2, h3, p, span, label, div {
        color: #e0e0e0 !important;
        font-family: 'Courier New', Courier, monospace;
    }
    [data-testid="stMetricValue"] { 
        font-size: 32px !important; 
        color: #ffffff !important; 
        font-weight: bold !important;
    }
    hr { border-top: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SESSION STATE (Speicher für Startwerte & Fallback) ---
if 'initial_values' not in st.session_state:
    st.session_state.initial_values = {}
if 'last_valid_data' not in st.session_state:
    st.session_state.last_valid_data = {}

# --- 3. LOGIK-FUNKTIONEN ---

def get_weather_logic(delta):
    """Ermittelt Wetter und Action. Delta 0 wird als 'Heiter' abgefangen."""
    if delta > 0.5: 
        return "☀️", "Sonnig", "🟢", "BUY"
    elif delta >= 0: # Deckt auch exakt 0.0 ab (Startzustand)
        return "🌤️", "Heiter", "🟢", "BULL"
    elif delta > -0.5: 
        return "☁️", "Bewölkt", "⚪", "WAIT"
    else: 
        return "⛈️", "Gewitter", "🔴", "SELL"

def get_live_data():
    mapping = {
        "EUR/USD": "EURUSD=X", 
        "EUROSTOXX": "^STOXX50E", 
        "S&P 500": "^GSPC",
        "APPLE": "AAPL", 
        "MICROSOFT": "MSFT"
    }
    results = {}
    for label, ticker in mapping.items():
        try:
            t = yf.Ticker(ticker)
            df = t.history(period="1d")
            if not df.empty:
                curr = df['Close'].iloc[-1]
                # Fixiere Startwert der Session
                if label not in st.session_state.initial_values:
                    st.session_state.initial_values[label] = curr
                
                start = st.session_state.initial_values[label]
                delta = ((curr - start) / start) * 100
                
                w_icon, w_txt, a_icon, a_txt = get_weather_logic(delta)
                
                # In Ergebnisse und Fallback-Speicher schreiben
                res = {
                    "price": curr, "delta": delta, 
                    "w_icon": w_icon, "w_txt": w_txt, 
                    "a_icon": a_icon, "a_txt": a_txt
                }
                results[label] = res
                st.session_state.last_valid_data[label] = res
            else:
                # Falls yfinance leere Daten liefert, nimm alte Daten
                results[label] = st.session_state.last_valid_data.get(label)
        except:
            # Falls API-Fehler, nimm alte Daten
            results[label] = st.session_state.last_valid_data.get(label)
    return results

# Daten abrufen
data = get_live_data()
# ZEITKORREKTUR: -1 Stunde für die Projektor-Anzeige
now = datetime.now() - timedelta(hours=1)

# --- 4. LAYOUT FUNKTION (Reihenfolge: Wetter -> Action -> Kurs -> Name) ---
def weather_row(label, d, f_str="{:.2f}"):
    if not d:
        # Falls gar keine Daten da sind (auch kein Fallback), zeige Platzhalter
        st.write(f"⌛ Lade Daten für {label}...")
        return
    
    # Spaltenaufteilung: Wetter | Action | Kurs/Delta | Bezeichnung
    cols = st.columns([1, 1, 1, 1, 3, 2])
    with cols[0]: st.write(f"### {d['w_icon']}")
    with cols[1]: st.write(d['w_txt'])
    with cols[2]: st.write(f"### {d['a_icon']}")
    with cols[3]: st.write(d['a_txt'])
    with cols[4]: 
        st.metric(label="Live-Kurs (Session)", value=f_str.format(d['price']), delta=f"{d['delta']:+.4f}%")
    with cols[5]: 
        st.write(f"## {label}")

# --- 5. HEADER ---
h1, h2 = st.columns([2, 1])
with h1: 
    st.title("☁️ Börsen-Wetter")
with h2:
    st.markdown(f"""
        <div style="text-align: right; border-right: 4px solid #00ff00; padding-right: 15px;">
            <p style="margin:0; font-size: 24px; font-weight: bold;">{now.strftime('%d.%m.%Y')}</p>
            <p style="margin:0; font-size: 18px; color: #00ff00
            !important;">{now.strftime('%H:%M:%S')} LIVE</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# --- 6. ANZEIGE DER SEKTIONEN ---

# WÄHRUNG
st.markdown("### 🌍 WÄHRUNG")
weather_row("EUR/USD", data.get("EUR/USD"), "{:.4f}")

st.markdown("---")

# INDIZES
st.markdown("### 📈 MARKT-INDIZES")
weather_row("EUROSTOXX", data.get("EUROSTOXX"))
weather_row("S&P 500", data.get("S&P 500"))

# SLIDER (Ergänzung zur Steuerung unter den Indizes)
st.write("")
update_seconds = st.slider("Update-Intervall (Sekunden):", 10, 300, 60, step=10)
st.markdown("---")

# AKTIEN
st.markdown("### 🍎 AKTIEN-ANALYSE")
weather_row("APPLE", data.get("APPLE"))
weather_row("MICROSOFT", data.get("MICROSOFT"))

# --- 7. AUTO-REFRESH ---
time.sleep(update_seconds)
st.rerun()
