import streamlit as st
import yfinance as yf
from datetime import datetime

# Seite konfigurieren
st.set_page_config(page_title="Trading & Bio Dashboard", layout="wide")

# --- 1. VARIABLE TICKER-LISTE & DEFAULTS ---
# Wir definieren hier Default-Werte für das Wochenende
meine_ticker = {
    "EUR/USD": {"symbol": "EURUSD=X", "default": 1.0850},
    "DAX Index": {"symbol": "^GDAXI", "default": 18500.0},
    "NASDAQ 100": {"symbol": "^IXIC", "default": 22500.0}
}

# --- 2. FUNKTION MIT GRÜNER DEFAULT-LOGIK ---
def hole_daten(name, info):
    try:
        t = yf.Ticker(info["symbol"])
        df = t.history(period="1d")
        if not df.empty:
            kurs = df['Close'].iloc[-1]
            zeit = df.index[-1].strftime('%d.%m. %H:%M')
            return kurs, zeit, False # False bedeutet: Kein Default
        return info["default"], "Markt zu", True # True bedeutet: Default aktiv
    except Exception:
        return info["default"], "Verbindung unterbrochen", True

# --- 3. DYNAMISCHE ANZEIGE ---
st.title("📊 Dein Trading- & Bio-Monitor")

cols = st.columns(len(meine_ticker))
for i, (name, info) in enumerate(meine_ticker.items()):
    preis, zeitpunkt, is_default = hole_daten(name, info)
    
    format_str = "{:.4f}" if "EUR/USD" in name else "{:,.2f}"
    anzeige_wert = format_str.format(preis)
    
    # Wenn es ein Default-Wert ist, färben wir die Info grün
    status_text = f":green[Default ({zeitpunkt})]" if is_default else f"Live: {zeitpunkt}"
    
    cols[i].metric(label=name, value=anzeige_wert, help=status_text)
    cols[i].write(status_text)

st.divider()

# --- 4. BEWERTUNGS-LOGIK (10/90 REGEL) ---
st.subheader("📈 Markt-Check & China-Exposure Logik")

# Dein aktueller Analyse-Wert (der "Fünfer")
wert = st.number_input("Aktueller Analyse-Wert (%)", value=5, step=1)

st.write("### Bewertungs-Skala:")
l_col, m_col, r_col = st.columns(3)

with l_col:
    if wert < 10: # Deine Regel: < 10% ist extrem tief
        st.error(f"🔴 **EXTREM TIEF**\n\nBereich: < 10%\n\nStatus: AKTIV")
    else:
        st.info("⚪ Extrem Tief (< 10%)")

with m_col:
    if 10 <= wert <= 90: # Deine Regel: 10% bis 90% ist normal
        st.success(f"🟢 **NORMALBEREICH**\n\nBereich: 10% - 90%\n\nStatus: AKTIV")
    else:
        st.info("⚪ Normalbereich (10% - 90%)")

with r_col:
    if wert > 90: # Deine Regel: > 90% ist extrem hoch
        st.error(f"🔴 **EXTREM HOCH**\n\nBereich: > 90%\n\nStatus: AKTIV")
    else:
        st.info("⚪ Extrem Hoch (> 90%)")

st.divider()

# --- 5. BACKUP-INFORMATIONEN (WANDSITZ ETC.) ---
with st.expander("🧘 Gesundheit & Wandsitz-Routine"):
    st.write("### Routine: **WANDSITZ**")
    st.info("⏱️ Ziel: **05 bis 08 Minuten**")
    st.warning("**Wichtig:** Gleichmäßig atmen! Keine Preßatmung (Valsalva-Manöver)!")
    st.write("* **Mundhygiene:** Keine Mundspülungen mit Chlorhexidin verwenden.")
    st.write("* **Zähneputzen:** Nicht unmittelbar nach dem Essen putzen.")

with st.expander("✈️ Reisen & Ernährung"):
    st.write(f"* **Ticket:** Österreich-Ticket vorhanden.")
    st.write("* **Snacks:** Immer Nüsse für die Reise einplanen.")
    st.write("* **Blutdruck:** Fokus auf Sprossen und Rote Bete.")
    st.write("* **Vorsicht:** Phosphate in Fertiggerichten und Grapefruit bei Medikamenten meiden.")

with st.expander("🆕 Letzte 7 Tage Übersicht"):
    st.write("### Wöchentlicher Überblick")
    st.write("Protokollierung deiner isometrischen Fortschritte und Marktdaten.")
