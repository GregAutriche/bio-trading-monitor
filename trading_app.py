import streamlit as st
import yfinance as yf

# Seite konfigurieren
st.set_page_config(page_title="Trading & Bio Dashboard", layout="wide")

# --- 1. FUNKTION FÜR DATENABRUF ---
def get_live_data(symbol):
    try:
        ticker = yf.Ticker(symbol)
        # 1 Tag Zeitraum. Wenn leer (z.B. Sonntag), wird None zurückgegeben.
        df = ticker.history(period="1d")
        return df['Close'].iloc[-1] if not df.empty else None
    except:
        return None

# Daten abrufen (Indizes & Deine Ticker)
eurusd = get_live_data("EURUSD=X")
dax = get_live_data("^GDAXI")
nasdaq = get_live_data("^IXIC")
# Deine Ticker für Ungarn und Bulgarien
otp_bank = get_live_data("OTP.BU")   # Ungarn
sopharma = get_live_data("SFA.SO")   # Bulgarien

# --- 2. HEADER & METRIKEN ---
st.title("📊 Dein Trading- & Bio-Monitor")

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("EUR/USD", f"{eurusd:.4f}" if eurusd else "Markt zu")
col2.metric("DAX Index", f"{dax:,.2f} pkt" if dax else "Markt zu")
col3.metric("NASDAQ 100", f"{nasdaq:,.2f}" if nasdaq else "Markt zu")
col4.metric("OTP Bank (HU)", f"{otp_bank:,.0f} HUF" if otp_bank else "Markt zu")
col5.metric("Sopharma (BG)", f"{sopharma:,.2f} BGN" if sopharma else "Markt zu")

st.divider()

# --- 3. DIE GESAMTE LOGIK-ABBILDUNG (IMMER SICHTBAR) ---
st.subheader("📈 Markt-Check & China-Exposure Logik")

# Status festlegen (Beispielwert 05% wie im Bild oder Live-Daten)
# Falls keine Daten da sind, zeigen wir die Skala neutral
aktueller_wert = 5 # Hier kannst du deinen dynamischen Wert einsetzen

# Die "Logik-Leiste" - Zeigt immer alle drei Bereiche an
st.write("### Bewertungs-Skala:")
l_col, m_col, r_col = st.columns(3)

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

# --- 4. AUFKLAPPBARE INFORMATIONEN (GESUNDHEIT, REISE, ERNÄHRUNG) ---

with st.expander("🧘 Gesundheit & Wandsitz-Routine"):
    st.write("### Routine: **WANDSITZ**")
    st.info("⏱️ **Empfohlene Dauer:** 05 bis 08 Minuten")
    st.warning("**Sicherheitsregeln:**")
    st.write("* **Atmung:** Gleichmäßig atmen! Keine Preßatmung (Valsalva-Manöver).")
    st.write("* **Mundhygiene:** Keine Mundspülungen mit Chlorhexidin.")
    st.write("* **Nach dem Essen:** Nicht sofort Zähne putzen oder Kaugummi kauen.")

with st.expander("✈️ Reisen & Ernährung"):
    st.write("### Unterwegs")
    st.write("* **Ticket:** Österreich Ticket vorhanden.")
    st.write("* **Snacks:** Nüsse für die Reise einplanen.")
    st.write("### Blutdruck-Ernährung")
    st.write("* **Fokus:** Sprossen und Rote Bete.")
    st.write("* **Vermeiden:** Phosphate in Fertiggerichten.")
    st.write("* **Medikamente:** Wechselwirkung von Grapefruit beachten.")

with st.expander("🆕 Letzte 7 Tage Übersicht"):
    st.write("### Wochenzusammenfassung")
    st.write("Hier werden deine Fortschritte beim Wandsitz und Marktbeobachtungen gelistet.")
