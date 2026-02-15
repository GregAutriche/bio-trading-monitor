import streamlit as st
import yfinance as yf
from datetime import datetime

# --- 1. SESSION STATE (Startwerte speichern) ---
if 'initial_values' not in st.session_state:
    st.session_state.initial_values = {}

# --- 2. DATENFUNKTION ---
def get_live_data():
    mapping = {"EURUSD": "EURUSD=X", "STOXX": "^STOXX50E", "SP": "^GSPC"}
    results = {}
    for key, ticker in mapping.items():
        try:
            t = yf.Ticker(ticker)
            df = t.history(period="1d")
            if not df.empty:
                current_price = df['Close'].iloc[-1]
                
                # Startwert der Session fixieren
                if key not in st.session_state.initial_values:
                    st.session_state.initial_values[key] = current_price
                
                start_price = st.session_state.initial_values[key]
                # Vergleich: Aktuell vs. Start der Session
                session_delta = ((current_price - start_price) / start_price) * 100
                
                results[key] = {"price": current_price, "delta": session_delta}
        except: results[key] = None
    return results

data = get_live_data()
now = datetime.now()

# --- 3. SLIDER-LAYOUT (Werte untereinander) ---
def compact_row(label, weather_icon, weather_text, signal_icon, signal_text, price, delta_val):
    cols = st.columns([2, 1, 1.5, 1, 1.5, 3])
    with cols[0]: st.write(f"**{label}**")
    with cols[1]: st.write(weather_icon)
    with cols[2]: st.write(weather_text)
    with cols[3]: st.write(signal_icon)
    with cols[4]: st.write(signal_text)
    with cols[5]:
        # Hier ist der "Slider": Preis oben, Delta direkt darunter
        st.metric(label="Session-Vergleich", value=f"{price}", delta=f"{delta_val:.4f}%")

# --- 4. HEADER (Rechtsbündig) ---
c1, c2 = st.columns([2, 1])
with c2:
    st.markdown(f"""
        <div style="text-align: right;">
            <p style="margin:0; font-size: 22px; font-weight: bold;">{now.strftime('%d.%m.%Y')}</p>
            <p style="margin:0; font-size: 18px; color: #00ff00;">{now.strftime('%H:%M:%S')} LIVE</p>
        </div>
    """, unsafe_allow_html=True)

# --- 5. ANZEIGE ---
st.markdown("### 🌍 FOKUS/ Währung")
if data.get("EURUSD"):
    compact_row("EUR/USD", "☀️", "Heiter", "🟢", "Bullisch", f"{data['EURUSD']['price']:.4f}", data['EURUSD']['delta'])

st.markdown("---")
st.markdown("### 📈 FOKUS/ Markt-Indizes")
if data.get("STOXX"):
    compact_row("EUROSTOXX", "☁️", "Bewölkt", "⚪", "Wait", f"{data['STOXX']['price']:.2f}", data['STOXX']['delta'])
