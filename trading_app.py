import streamlit as st
import yfinance as yf
from datetime import datetime

# Seite konfigurieren
st.set_page_config(page_title="Trading & Bio Dashboard", layout="wide")

# --- 1. FUNKTION FÜR DATENABRUF MIT ZEITSTEMPEL ---
def get_live_data_with_time(symbol):
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="1d")
        if not df.empty:
            price = df['Close'].iloc[-1]
            time = df.index[-1].strftime('%d.%m. %H:%M')
            return price, time
        return None, "Keine Daten"
    except:
        return None, "Fehler"

# Daten abrufen
eurusd_p, eurusd_t = get_live_data_with_time("EURUSD=X")
dax_p, dax_t = get_live_data_with_time("^GDAXI")
nasdaq_p, nasdaq_t = get_live_data_with_time("^IXIC")
otp_p, otp_t = get_live_data_with_time("OTP.BU")
sopharma_p, sopharma_t = get_live_data_with_time("SFA.SO")

# --- 2. HEADER & METRIKEN MIT ZEITSTEMPEL ---
st.title("📊 Dein Trading- & Bio-Monitor")

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("EUR/USD", f"{eurusd_p:.4f}" if eurusd_p else "Markt zu", help=f"Zeit: {eurusd_t}")
c2.metric("DAX Index", f"{dax_p:,.2f}" if dax_p else "Markt zu", help=f"Zeit: {dax_t}")
c3.metric("NASDAQ 100", f"{nasdaq_p:,.2f}" if nasdaq_p else "Markt zu", help=f"Zeit: {nasdaq_t}")
c4.metric("OTP Bank (HU)", f"{otp_p:,.0f}" if otp_p else "Markt zu", help=f"Zeit: {otp_t}")
c5.metric("Sopharma (BG)", f"{sopharma_p:,.2f}" if sopharma_p else "Markt zu", help=f"Zeit: {sopharma_t}")

# Anzeige der Zeitstempel unter den Metriken für direkte Sichtbarkeit
st.caption(f"Letzte Aktualisierung: DAX ({dax_t}) | HU ({otp_t}) | BG ({sopharma_t})")

st.divider()

# --- 3. CHINA-EXPOSURE & STÄNDIGE LOGIK-ABBILDUNG ---
st.subheader("📈 Markt-Check & China-Exposure Logik")

# Simulation/Eingabe des aktuellen Werts
# (Hier könnte später die automatische Berechnung stehen)
aktueller_wert = st.number_input("Aktueller Analyse-Wert (%)", value=5, step=1)

st.write("### Bewertungs-Skala:")
l_col, m_col, r_col = st.columns(3)

# Die Logik wird immer vollständig angezeigt
with l_col:
    if aktueller_wert < 10:
        st.error("🔴 **EXTREM TIEF**\n\nBereich: < 10%\n\n*Status: AKTIV*")
    else:
        st.info("⚪ Extrem Tief\n\n(< 10%)")

with m_col:
    if 10 <= aktueller_wert <= 90:
        st.success("🟢 **NORMALBEREICH**\n\nBereich: 10% - 90%\n\n*Status: AKTIV*")
    else:
        st.info("⚪ Normalbereich\n\n(10% - 90%)")

with r_col:
    if aktueller_wert > 90:
        st.error("🔴 **EXTREM HOCH**\n\nBereich: > 90%\n\n*Status: AKTIV*")
    else:
        st.info("⚪ Extrem Hoch\n\n(> 90%)")

st.divider()

# --- 4. AUFKLAPPBARE INFORMATIONEN ---
with st.expander("🧘 Gesundheit & Wandsitz-Routine"):
    st.write("### Routine: **WANDSITZ**")
    st.info("⏱️ **Empfohlene Dauer:** 05 bis 08 Minuten")
    st.warning("**Sicherheitsregeln:**")
    st.write("* **Atmung:** Gleichmäßig atmen! Keine Preßatmung (Valsalva-Manöver).")
    st.write("* **Mundhygiene:** Keine Mundspülungen mit Chlorhexidin.")
    st.write("* **Timing:** Nicht unmittelbar nach dem Essen Zähne putzen oder Kaugummi kauen.")

with st.expander("✈️ Reisen & Ernährung"):
    st.write("### Unterwegs")
    st.write(f"* **Ticket:** Österreich-Ticket vorhanden.")
    st.write("* **Snacks:** Nüsse für die Reise einplanen.")
    st.write("### Blutdruck-Ernährung")
    st.write("* **Fokus:** Sprossen und Rote Bete.")
    st.write("* **Vermeiden:** Phosphate in Fertiggerichten.")
    st.write("* **Medikamente:** Wechselwirkung von Grapefruit beachten.")

with st.expander("🆕 Letzte 7 Tage Übersicht"):
    st.write("### Wochenzusammenfassung")
    st.write("Hier werden deine täglichen Fortschritte gelistet.")
