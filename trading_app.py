import streamlit as st
import yfinance as yf
from datetime import datetime  # Wichtig für den Zeitstempel-Fix

# Seite konfigurieren
st.set_page_config(page_title="Trading & Bio Dashboard", layout="wide")

# --- 1. VARIABLE TICKER-LISTE (Zentral steuerbar) ---
# Du kannst hier jederzeit Paare hinzufügen oder entfernen
meine_ticker = {
    "EUR/USD": "EURUSD=X",
    "DAX Index": "^GDAXI",
    "NASDAQ 100": "^IXIC",
    "OTP Bank (HU)": "OTP.BU",
    "Sopharma (BG)": "SFA.SO"
}

# --- 2. FUNKTION FÜR VARIABLEN DATENABRUF ---
def hole_daten(symbol):
    try:
        t = yf.Ticker(symbol)
        # 1m-Intervall für die exakte Zeit am Handelstag
        df = t.history(period="1d", interval="1m")
        if df.empty:
            df = t.history(period="1d")
        
        if not df.empty:
            kurs = df['Close'].iloc[-1]
            # Zeitstempel formatieren
            zeit = df.index[-1].strftime('%d.%m. %H:%M')
            return kurs, zeit
        return None, "Keine Daten"
    except:
        return None, "Fehler"

# --- 3. DYNAMISCHE ANZEIGE DER WERTE ---
st.title("📊 Dein Trading- & Bio-Monitor")

# Erstellt automatisch Spalten basierend auf der Anzahl deiner Ticker
cols = st.columns(len(meine_ticker))

for i, (name, symbol) in enumerate(meine_ticker.items()):
    preis, zeitpunkt = hole_daten(symbol)
    
    # Dezimalstellen je nach Typ anpassen
    format_str = "{:.4f}" if "EUR/USD" in name else "{:,.2f}"
    
    cols[i].metric(
        label=name, 
        value=format_str.format(preis) if preis else "Markt zu",
        help=f"Daten von: {zeitpunkt}"
    )

# Fix für den Zeitstempel unter den Werten
st.caption(f"Letzte Aktualisierung der Liste: {datetime.now().strftime('%H:%M:%S')} Uhr")
st.divider()

# --- 4. BEWERTUNGS-LOGIK (10/90 REGEL) ---
st.subheader("📈 Markt-Check & China-Exposure Logik")

# Das Eingabefeld mit +/- (dein "Fünfer")
wert = st.number_input("Aktueller Analyse-Wert (%)", value=5, step=1)

st.write("### Bewertungs-Skala:")
l_col, m_col, r_col = st.columns(3)

with l_col:
    if wert < 10:
        st.error(f"🔴 **EXTREM TIEF**\n\nBereich: < 10%\n\nStatus: AKTIV")
    else:
        st.info("⚪ Extrem Tief\n\n(< 10%)")

with m_col:
    if 10 <= wert <= 90:
        st.success("🟢 **NORMALBEREICH**\n\nBereich: 10% - 90%")
    else:
        st.info("⚪ Normalbereich\n\n(10% - 90%)")

with r_col:
    if wert > 90:
        st.error(f"🔴 **EXTREM HOCH**\n\nBereich: > 90%")
    else:
        st.info("⚪ Extrem Hoch\n\n(> 90%)")

st.divider()

# --- 5. BIO-ROUTINEN (EXPANDER) ---
with st.expander("🧘 Gesundheit & Wandsitz-Routine"):
    st.write("### Routine: **WANDSITZ**")
    st.info("⏱️ Dauer: **05** bis **08** Minuten")
    st.warning("**Sicherheitsregeln:**")
    st.write("* **Atmung:** Gleichmäßig atmen! Keine Preßatmung (Valsalva-Manöver).")
    st.write("* **Mundhygiene:** Keine Mundspülungen mit Chlorhexidin verwenden.")

with st.expander("✈️ Reisen & Ernährung"):
    st.write(f"* **Ticket:** Österreich-Ticket vorhanden.")
    st.write("* **Snacks:** Nüsse für die Reise einplanen.")
    st.write("* **Fokus:** Sprossen und Rote Bete zur Blutdrucksenkung.")
    st.write("* **Vermeiden:** Phosphate in Fertiggerichten.")
