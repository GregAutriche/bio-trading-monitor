import streamlit as st
import yfinance as yf
from datetime import datetime

# --- 1. KONFIGURATION & TICKER ---
st.set_page_config(page_title="Trading & Bio Monitor", layout="wide")

meine_ticker = {
    "EUR/USD": {"symbol": "EURUSD=X", "default": 1.1778, "datum": "06.02. 00:00"},
    "DAX Index": {"symbol": "^GDAXI", "default": 24721.46, "datum": "06.02. 00:00"},
    "NASDAQ 100": {"symbol": "^IXIC", "default": 23031.21, "datum": "06.02. 00:00"}
}

# --- 2. DATEN-STATUS PRÜFEN ---
def hole_status_und_daten(info):
    try:
        t = yf.Ticker(info["symbol"])
        df = t.history(period="1d")
        if not df.empty and df.index[-1].date() == datetime.now().date():
            return df['Close'].iloc[-1], df.index[-1].strftime('%d.%m. %H:%M'), True
        return info["default"], info["datum"], False
    except:
        return info["default"], info["datum"], False

# --- 3. HEADER & METRIKEN ---
st.title("📊 Dein Trading- & Bio-Monitor")
cols = st.columns(len(meine_ticker))
ist_live = False

for i, (name, info) in enumerate(meine_ticker.items()):
    preis, zeit, live = hole_status_und_daten(info)
    if live: ist_live = True
    
    format_str = "{:.4f}" if "USD" in name else "{:,.2f}"
    cols[i].metric(label=name, value=format_str.format(preis))
    # Datum und Status [no data] in Rot [cite: 2026-02-07]
    cols[i].write(f"{zeit} :red[[no data]]" if not live else f"{zeit} :green[[data]]")

st.divider()

# --- 4. MARKT-CHECK & BEWERTUNGSSKALA ---
status_label = ":red[[no data]]" if not ist_live else ":green[[data]]"
st.subheader(f"📈 Markt-Check & China-Exposure Logik {status_label}")

# Dein Analyse-Wert (5%) [cite: 2026-02-07]
wert = st.number_input("Aktueller Analyse-Wert (%)", value=5, step=1)
st.write(f"### Bewertungsskala: {status_label}")

l, m, r = st.columns(3)

# LOGIK: PUNKTE IMMER ZEIGEN, ABER BOX NUR AKTIV BEI [data]
with l:
    if ist_live and wert < 10:
        st.error("🔴 **EXTREM TIEF**\n\nStatus: AKTIV")
    else:
        # Punkt bleibt rot, aber Box ist neutral grau/blau [cite: 2026-02-07]
        st.write("🔴 **Extrem Tief**")
        st.info("Möglichkeit: < 10%")

with m:
    if ist_live and 10 <= wert <= 90:
        st.success("🟢 **Normalbereich**\n\nStatus: AKTIV")
    else:
        # Punkt bleibt grün [cite: 2026-02-07]
        st.write("🟢 **Normalbereich**")
        st.info("Möglichkeit: 10% - 90%")

with r:
    if ist_live and wert > 90:
        st.error("🔴 **EXTREM HOCH**\n\nStatus: AKTIV")
    else:
        # Punkt bleibt violett/dunkelblau [cite: 2026-02-07]
        st.write("🟣 **Extrem Hoch**")
        st.info("Möglichkeit: > 90%")

st.divider()

# --- 5. BIO-BACKUP ZUSAMMENFASSUNG ---
with st.expander("🧘 Gesundheit & Wandsitz-Routine"):
    st.write("### Routine: **WANDSITZ**")
    st.info("⏱️ Ziel: **05 bis 08 Minuten** [cite: 2026-02-03]")
    # Wichtigste Warnung für isometrisches Training [cite: 2025-12-20]
    st.warning("**Sicherheitsregel:** Gleichmäßig atmen! Keine Preßatmung! [cite: 2025-12-20]")
    st.write("* **Blutdruck:** Senkung durch Sprossen und Rote Bete [cite: 2025-12-20].")
    st.write("* **Mund:** Keine Mundspülungen mit Chlorhexidin verwenden [cite: 2025-12-20].")
    st.write("* **Zähne:** Erst Zeit nach dem Essen vergehen lassen [cite: 2025-12-20].")

with st.expander("✈️ Reisen & Ernährung"):
    st.write(f"* **Ticket:** Österreich Ticket vorhanden [cite: 2026-01-25].")
    st.write("* **Snacks:** Nüsse für die Reise einplanen [cite: 2026-02-03].")
    st.write("* **Vorsicht:** Wechselwirkungen mit Grapefruit beachten [cite: 2025-12-20].")
