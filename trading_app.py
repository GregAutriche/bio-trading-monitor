import streamlit as st
import yfinance as yf
from datetime import datetime

# Seite konfigurieren
st.set_page_config(page_title="Trading & Bio Dashboard", layout="wide")

# --- 1. TICKER & DEFAULTS ---
meine_ticker = {
    "EUR/USD": {"symbol": "EURUSD=X", "default": 1.1820},
    "DAX Index": {"symbol": "^GDAXI", "default": 24717.53},
    "NASDAQ 100": {"symbol": "^IXIC", "default": 23028.59}
}

# --- 2. DATEN-LOGIK ---
def hole_daten(info):
    try:
        t = yf.Ticker(info["symbol"])
        df = t.history(period="1d")
        if not df.empty:
            # Wir prüfen, ob der Zeitstempel von heute ist
            ist_heute = df.index[-1].date() == datetime.now().date()
            return df['Close'].iloc[-1], ist_heute
        return info["default"], False
    except:
        return info["default"], False

# --- 3. HEADER ---
st.title("📊 Dein Trading- & Bio-Monitor")
cols = st.columns(len(meine_ticker))
daten_da = False

for i, (name, info) in enumerate(meine_ticker.items()):
    preis, vorhanden = hole_daten(info)
    if vorhanden: daten_da = True
    format_str = "{:.4f}" if "USD" in name else "{:,.2f}"
    cols[i].metric(label=name, value=format_str.format(preis))

st.divider()

# --- 4. BEWERTUNGS-SKALA MIT STATUS IN ECKIGER KLAMMER ---
st.subheader("📈 Markt-Check & China-Exposure Logik")
wert = st.number_input("Aktueller Analyse-Wert (%)", value=5, step=1)

# Status für die eckige Klammer festlegen
if daten_da:
    status_display = ":green[[Daten vorhanden]]"
else:
    status_display = ":red[[Keine Daten vorhanden]]"

st.write(f"### Bewertungsskala: {status_display}")

l, m, r = st.columns(3)

with l:
    if wert < 10: # Deine 10/90 Regel [cite: 2026-02-07]
        st.error(f"🔴 **EXTREM TIEF**\n\nStatus: AKTIV")
    else:
        st.info("⚪ Extrem Tief (Möglichkeit: < 10%)")

with m:
    if 10 <= wert <= 90: # Normalbereich Definition [cite: 2026-02-07]
        st.success(f"🟢 **NORMALBEREICH**\n\nStatus: AKTIV")
    else:
        # Grüne Info-Anzeige der Möglichkeiten [cite: 2026-02-07]
        st.write(":green[🟢 **Normalbereich**]")
        st.info("Möglichkeit: 10% - 90%")

with r:
    if wert > 90: # Extrem Hoch Definition [cite: 2026-02-07]
        st.error(f"🔴 **EXTREM HOCH**\n\nStatus: AKTIV")
    else:
        st.info("⚪ Extrem Hoch (Möglichkeit: > 90%)")

st.divider()

# --- 5. BIO-BACKUP & ROUTINEN ---
with st.expander("🧘 Gesundheit & Wandsitz-Routine"):
    st.write("### Routine: **WANDSITZ**")
    st.info("⏱️ Ziel: **05 bis 08 Minuten** [cite: 2026-02-03]")
    st.warning("**Sicherheitsregel:** Gleichmäßig atmen! Keine Preßatmung! [cite: 2025-12-20]")
    st.write("* Keine Mundspülungen mit Chlorhexidin verwenden [cite: 2025-12-20].")
    st.write("* Zähneputzen: Nicht unmittelbar nach dem Essen [cite: 2025-12-20].")
