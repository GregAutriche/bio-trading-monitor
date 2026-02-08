import streamlit as st
import yfinance as yf
from datetime import datetime

# --- KONFIGURATION ---
st.set_page_config(page_title="Trading & Bio Dashboard", layout="wide")

# --- 1. VARIABLE TICKER-LISTE & DEFAULTS ---
# Deine Auswahl der wichtigsten globalen Werte
meine_ticker = {
    "EUR/USD": {"symbol": "EURUSD=X", "default": 1.1820},
    "DAX Index": {"symbol": "^GDAXI", "default": 24717.53},
    "NASDAQ 100": {"symbol": "^IXIC", "default": 23028.59}
}

# --- 2. FUNKTION FÜR VARIABLEN DATENABRUF ---
def hole_daten(info):
    try:
        t = yf.Ticker(info["symbol"])
        df = t.history(period="1d")
        if not df.empty:
            # Prüfen, ob die Daten vom aktuellen Tag sind
            ist_aktuell = df.index[-1].date() == datetime.now().date()
            return df['Close'].iloc[-1], ist_aktuell
        return info["default"], False
    except:
        return info["default"], False

# --- 3. DATEN LADEN & HEADER ANZEIGEN ---
st.title("📊 Dein Trading- & Bio-Monitor")

cols = st.columns(len(meine_ticker))
daten_da = False

for i, (name, info) in enumerate(meine_ticker.items()):
    preis, vorhanden = hole_daten(info)
    if vorhanden: 
        daten_da = True
    
    # Formatierung: EUR/USD braucht mehr Nachkommastellen
    format_str = "{:.4f}" if "USD" in name else "{:,.2f}"
    cols[i].metric(label=name, value=format_str.format(preis))

st.divider()

# --- 4. MARKT-CHECK LOGIK [data] / [no data] ---
# Status für die eckige Klammer oben (Englisch wie gewünscht) [cite: 2026-02-07]
status_marktcheck = ":green[[data]]" if daten_da else ":red[[no data]]"
st.subheader(f"📈 Markt-Check & China-Exposure Logik {status_marktcheck}")

# Analyse-Wert Eingabe (Dein "Fünfer") [cite: 2026-02-07]
wert = st.number_input("Aktueller Analyse-Wert (%)", value=5, step=1)

# Status für die Bewertungsskala (Deutsch wie gewünscht) [cite: 2026-02-07]
status_bewertung = ":green[[Daten vorhanden]]" if daten_da else ":red[[Keine Daten vorhanden]]"
st.write(f"### Bewertungsskala: {status_bewertung}")

l_col, m_col, r_col = st.columns(3)

with l_col:
    # 10/90 Regel: < 10% ist EXTREM TIEF [cite: 2026-02-07]
    if wert < 10:
        st.error(f"🔴 **EXTREM TIEF**\n\nBereich: < 10%\n\nStatus: AKTIV")
    else:
        st.info("⚪ Extrem Tief (Möglichkeit: < 10%)")

with m_col:
    # Normalbereich: 10% bis 90% [cite: 2026-02-07]
    if 10 <= wert <= 90:
        st.success(f"🟢 **NORMALBEREICH**\n\nBereich: 10% - 90%\n\nStatus: AKTIV")
    else:
        # Grüne Anzeige der Möglichkeiten im inaktiven Zustand [cite: 2026-02-07]
        st.write(":green[🟢 **Normalbereich**]")
        st.info("Möglichkeit: 10% - 90%")

with r_col:
    # 10/90 Regel: > 90% ist EXTREM HOCH [cite: 2026-02-07]
    if wert > 90:
        st.error(f"🔴 **EXTREM HOCH**\n\nBereich: > 90%\n\nStatus: AKTIV")
    else:
        st.info("⚪ Extrem Hoch (Möglichkeit: > 90%)")

st.divider()

# --- 5. BIO-BACKUP INFORMATIONEN ---
with st.expander("🧘 Gesundheit & Wandsitz-Routine"):
    st.write("### Routine: **WANDSITZ**")
    st.info("⏱️ Ziel: **05 bis 08 Minuten** [cite: 2026-02-03]")
    st.warning("**Sicherheitsregel:** Gleichmäßig atmen! Keine Preßatmung! [cite: 2025-12-20]")
    st.write("* **Mundhygiene:** Keine Mundspülungen mit Chlorhexidin verwenden [cite: 2025-12-20].")
    st.write("* **Timing:** Nicht unmittelbar nach dem Essen Zähne putzen [cite: 2025-12-20].")

with st.expander("✈️ Reisen & Ernährung"):
    st.write(f"* **Ticket:** Österreich-Ticket vorhanden [cite: 2026-01-25].")
    st.write("* **Snacks:** Nüsse für die Reise einplanen [cite: 2026-02-03].")
    st.write("* **Blutdruck:** Fokus auf Sprossen und Rote Bete [cite: 2025-12-20].")
    st.write("* **Vorsicht:** Phosphate in Fertiggerichten und Grapefruit meiden [cite: 2025-12-20].")

# --- 6. 7-TAGE ÜBERSICHT (DEIN WUNSCH) ---
with st.expander("📅 Letzte 7 Tage Übersicht"):
    st.write("### Tägliche Zusammenfassung")
    # Hier könnte eine Tabelle mit deinen Wandsitz-Zeiten stehen
    st.table({
        "Datum": ["02.02.", "03.02.", "04.02.", "05.02.", "06.02.", "07.02.", "08.02."],
        "Wandsitz (Min)": [6, 5, 7, 6, 8, 5, "-"],
        "Status": ["OK", "OK", "OK", "OK", "OK", "OK", "Laufend"]
    })
