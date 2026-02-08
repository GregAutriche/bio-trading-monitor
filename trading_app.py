import streamlit as st
import yfinance as yf
from datetime import datetime

# Seite konfigurieren
st.set_page_config(page_title="Trading & Bio Dashboard", layout="wide")

# --- 1. VARIABLE TICKER-LISTE ---
meine_ticker = {
    "EUR/USD": "EURUSD=X",
    "DAX Index": "^GDAXI",
    "NASDAQ 100": "^IXIC"
}

# --- 2. FUNKTION MIT FEHLERSCHUTZ ---
def hole_daten(symbol):
    try:
        t = yf.Ticker(symbol)
        df = t.history(period="1d")
        if not df.empty:
            kurs = df['Close'].iloc[-1]
            zeit = df.index[-1].strftime('%d.%m. %H:%M')
            return kurs, zeit
        return None, "Markt geschlossen"
    except Exception:
        return None, "Verbindungsfehler"

# --- 3. DYNAMISCHE ANZEIGE ---
st.title("📊 Dein Trading- & Bio-Monitor")

cols = st.columns(len(meine_ticker))

for i, (name, symbol) in enumerate(meine_ticker.items()):
    preis, zeitpunkt = hole_daten(symbol)
    
    # Hier verhindern wir den Absturz:
    # Nur wenn 'preis' ein echter Wert ist, wird formatiert
    if preis is not None:
        format_str = "{:.4f}" if "EUR/USD" in name else "{:,.2f}"
        anzeige_wert = format_str.format(preis)
    else:
        anzeige_wert = "--" # Platzhalter statt Fehlermeldung
    
    cols[i].metric(
        label=name, 
        value=anzeige_wert,
        help=f"Info: {zeitpunkt}"
    )

st.caption(f"Letzte System-Prüfung: {datetime.now().strftime('%H:%M:%S')} Uhr")
st.divider()

# --- 4. BEWERTUNGS-LOGIK (10/90 REGEL) ---
st.subheader("📈 Markt-Check & China-Exposure Logik")

# Dein "Fünfer" (05%) - bleibt stabil
wert = st.number_input("Aktueller Analyse-Wert (%)", value=5, step=1)

st.write("### Bewertungs-Skala:")
l_col, m_col, r_col = st.columns(3)

with l_col:
    if wert < 10:
        st.error(f"🔴 **EXTREM TIEF**\n\nBereich: < 10%\n\nStatus: AKTIV")
    else:
        st.info("⚪ Extrem Tief")

with m_col:
    if 10 <= wert <= 90:
        st.success(f"🟢 **NORMALBEREICH**\n\nBereich: 10% - 90%\n\nStatus: AKTIV")
    else:
        st.info("⚪ Normalbereich")

with r_col:
    if wert > 90:
        st.error(f"🔴 **EXTREM HOCH**\n\nBereich: > 90%\n\nStatus: AKTIV")
    else:
        st.info("⚪ Extrem Hoch")

st.divider()

# --- 5. BIO-ROUTINEN (IMMERSICHTBAR) ---
with st.expander("🧘 Gesundheit & Wandsitz-Routine"):
    st.write("### Routine: **WANDSITZ**")
    st.info("⏱️ Ziel: 05 bis 08 Minuten")
    st.warning("**Atem-Check:** Gleichmäßig atmen! Keine Preßatmung.")
    st.write("Backup: Keine Mundspülung mit Chlorhexidin.")

with st.expander("✈️ Reisen & Ernährung"):
    st.write(f"* **Ticket:** Österreich-Ticket vorhanden.")
    st.write("* **Ernährung:** Sprossen und Rote Bete.")
    st.write("* **Snacks:** Nüsse einplanen.")
