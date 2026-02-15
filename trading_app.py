import streamlit as st
import yfinance as yf
from datetime import datetime

# --- 1. TERMINAL LOOK & FARBEN (CSS) ---
st.set_page_config(layout="wide", page_title="Börsen-Wetter Terminal")

st.markdown("""
    <style>
    /* Hintergrund und Schriftfarben */
    .stApp { background-color: #000000; }
    h1, h2, h3, p, span, label, div {
        color: #e0e0e0 !important;
        font-family: 'Courier New', Courier, monospace;
    }
    
    /* Styling für den Slider (Metrik): Kurs oben, Delta unten */
    [data-testid="stMetricValue"] { 
        font-size: 32px !important; 
        color: #ffffff !important; 
        font-weight: bold !important;
    }
    [data-testid="stMetricDelta"] { 
        font-size: 20px !important; 
    }
    
    /* Trennlinien */
    hr { border-top: 1px solid #333; }
    
    /* Kompakte Darstellung */
    .stMarkdown div p { margin-bottom: 0px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SESSION STATE (Startwerte für Slider-Vergleich) ---
if 'initial_values' not in st.session_state:
    st.session_state.initial_values = {}

# --- 3. DATENFUNKTION ---
def get_live_data():
    # Ticker-Mapping für stabilere Abfragen
    mapping = {
        "EURUSD": "EURUSD=X", 
        "STOXX": "^STOXX50E", 
        "SP": "^GSPC",
        "AAPL": "AAPL", 
        "MSFT": "MSFT"
    }
    results = {}
    for key, ticker in mapping.items():
        try:
            t = yf.Ticker(ticker)
            df = t.history(period="1d")
            if not df.empty:
                current_price = df['Close'].iloc[-1]
                
                # Startwert der Session fixieren, falls noch nicht vorhanden
                if key not in st.session_state.initial_values:
                    st.session_state.initial_values[key] = current_price
                
                start_price = st.session_state.initial_values[key]
                # Slider-Logik: Vergleich Aktuell vs. Session-Start
                session_delta = ((current_price - start_price) / start_price) * 100
                
                results[key] = {
                    "price": current_price,
                    "delta": session_delta
                }
            else:
                results[key] = None
        except:
            results[key] = None
    return results

data = get_live_data()
now = datetime.now()

# --- 4. LAYOUT-FUNKTION (Wetter -> Aktion -> Slider untereinander) ---
def compact_row(label, weather_icon, weather_text, signal_icon, signal_text, price, delta_val):
    """Erzeugt Zeile mit Wetter links und Kurs/Delta untereinander rechts"""
    cols = st.columns([2, 0.8, 1.5, 0.8, 1.5, 3])
    
    with cols[0]:
        st.write(f"**{label}**")
    with cols[1]:
        st.write(weather_icon)
    with cols[2]:
        st.write(weather_text)
    with cols[3]:
        st.write(signal_icon)
    with cols[4]:
        st.write(signal_text)
    with cols[5]:
        # Das Slider-Layout: Wert oben, Veränderung direkt darunter
        st.metric(label="Session-Kurs", value=f"{price}", delta=f"{delta_val:+.4f}%")

# --- 5. HEADER (Datum & Uhrzeit rechtsbündig) ---
header_col1, header_col2 = st.columns([2, 1])

with header_col1:
    st.title("☁️ Börsen-Wetter Terminal")

with header_col2:
    # Rechtsbündiges Update mit Datum und sekundengenauer Uhrzeit
    st.markdown(f"""
        <div style="text-align: right; border-right: 4px solid #00ff00; padding-right: 15px;">
            <p style="margin:0; font-size: 14px; opacity: 0.6; color: #00ff00 !important;">LETZTES UPDATE</p>
            <p style="margin:0; font-size: 24px; font-weight: bold;">{now.strftime('%d.%m.%Y')}</p>
            <p style="margin:0; font-size: 18px; color: #00ff00 !important;">{now.strftime('%H:%M:%S')} LIVE</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# --- 6. ANZEIGE DER SEKTIONEN ---

# WÄHRUNG
st.markdown("### 🌍 FOKUS/ Währung")
if data.get("EURUSD"):
    compact_row("EUR/USD", "☀️", "Heiter", "🟢", "Bullisch", 
                f"{data['EURUSD']['price']:.4f}", data['EURUSD']['delta'])
else:
    st.info("EUR/USD: Daten aktuell nicht verfügbar.")

st.markdown("---")

# MARKT-INDIZES
st.markdown("### 📈 FOKUS/ Markt-Indizes")
if data.get("STOXX"):
    compact_row("EUROSTOXX", "☁️", "Bewölkt", "⚪", "Wait", 
                f"{data['STOXX']['price']:.2f}", data['STOXX']['delta'])
else:
    st.info("EUROSTOXX: Keine Daten (Ticker prüfen oder Wochenende).")

if data.get("SP"):
    compact_row("S&P 500", "☀️", "Sonnig", "🟢", "Buy", 
                f"{data['SP']['price']:.2f}", data['SP']['delta'])

st.markdown("---")

# AKTIEN
st.markdown("### 🍎 FOKUS/ Aktien-Analyse")
for label, sym in [("APPLE", "AAPL"), ("MICROSOFT", "MSFT")]:
    if data.get(sym):
        compact_row(label, "☀️", "Sonnig", "🟢", "Buy", 
                    f"{data[sym]['price']:.2f}", data[sym]['delta'])
