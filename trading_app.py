import streamlit as st
import yfinance as yf
from datetime import datetime

# --- KONFIGURATION ---
st.set_page_config(page_title="Trading & Bio Dashboard", layout="wide")

# --- 1. VARIABLE TICKER-LISTE & DEFAULTS ---
meine_ticker = {
    "EUR/USD": {"symbol": "EURUSD=X", "default": 1.1820},
    "DAX Index": {"symbol": "^GDAXI", "default": 24717.53},
    "NASDAQ 100": {"symbol": "^IXIC", "default": 23031.21}
}

# --- 2. FUNKTION FÜR DATENABRUF ---
def hole_daten(info):
    try:
        t = yf.Ticker(info["symbol"])
        df = t.history(period="1d")
        if not df.empty:
            ist_aktuell = df.index[-1].date() == datetime.now().date()
            return df['Close'].iloc[-1], ist_aktuell
        return info["default"], False
    except:
        return info["default"], False

# --- 3. DATEN LADEN & HEADER ---
st.title("📊 Dein Trading- & Bio-Monitor")

cols = st.columns(len(meine_ticker))
daten_da = False

for i, (name, info) in enumerate(meine_ticker.items()):
    preis, vorhanden = hole_daten(info)
    if vorhanden: 
        daten_da = True
    
    format_str = "{:.4f}" if "USD" in name else "{:,.2f}"
    cols[i].metric(label=name, value=format_str.format(preis))

st.divider()

# --- 4. MARKT-CHECK & BEWERTUNGSSKALA ---
# Status-Text einheitlich [no data] oder [data]
status_text = ":green[[data]]" if daten_da else ":red[[no data]]"

st.subheader(f"📈 Markt-Check & China-Exposure Logik {status_text}")
wert = st.number_input("Aktueller Analyse-Wert (%)", value=5, step=1)
st.write(f"### Bewertungsskala: {status_text}")

l_col, m_col, r_col = st.columns(3)

# LINKS: EXTREM TIEF (Jetzt mit der gleichen Logik)
with l_col:
    if wert < 10: # Deine Regel: < 10% ist extrem tief
        st.error(f"🔴 **EXTREM TIEF**\n\nStatus: AKTIV")
    else:
        st.write("🔴 **Extrem Tief**")
        st.info("Möglichkeit: < 10%")

# MITTE: NORMALBEREICH
with m_col:
    if 10 <= wert <= 90: # Deine Regel: 10% - 90% ist normal
        st.success(f"🟢 **Normalbereich**\n\nStatus: AKTIV")
    else:
        st.write("🟢 **Normalbereich**")
        st.info("Möglichkeit: 10% - 90%")

# RECHTS: EXTREM HOCH
with r_col:
    if wert > 90: # Deine Regel: > 90% ist extrem hoch
        st.error(f"🔴 **EXTREM HOCH**\n\nStatus: AKTIV")
    else:
        st.write("🟣 **Extrem Hoch**")
        st.info("Möglichkeit: > 90%")

st.divider()

# --- 5. BIO-BACKUP INFORMATIONEN ---
with st.expander("🧘 Gesundheit & Wandsitz-Routine"):
    st.write("### Routine: **WANDSITZ**")
    st.info("⏱️ Ziel: **05 bis 08 Minuten**")
    st.warning("**Wichtig:** Gleichmäßig atmen! Keine Preßatmung (Valsalva-Manöver)!")
    st.write("* **Mundhygiene:** Keine Mundspülungen mit Chlorhexidin verwenden.")
    st.write("* **Timing:** Nicht unmittelbar nach dem Essen Zähne putzen.")

with st.expander("✈️ Reisen & Ernährung"):
    st.write(f"* **Ticket:** Österreich-Ticket vorhanden.")
    st.write("* **Snacks:** Nüsse für die Reise einplanen.")
    st.write("* **Blutdruck:** Fokus auf Sprossen und Rote Bete.")
    st.write("* **Vorsicht:** Phosphate in Fertiggerichten und Grapefruit meiden.")

# --- 6. 7-TAGE ÜBERSICHT ---
with st.expander("📅 Letzte 7 Tage Übersicht"):
    st.table({
        "Datum": ["02.02.", "03.02.", "04.02.", "05.02.", "06.02.", "07.02.", "08.02."],
        "Wandsitz (Min)": [6, 5, 7, 6, 8, 5, "-"],
        "Analyse-Wert (%)": [15, 12, 8, 45, 92, 5, wert],
        "Status": ["Normal", "Normal", "Tief", "Normal", "Hoch", "Tief", "Check"]
    })
