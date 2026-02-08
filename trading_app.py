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
    
    # Datum UND Status anzeigen [cite: 2026-02-07]
    status_tag = ":green[[data]]" if live else ":red[[no data]]"
    cols[i].write(f"{zeit} {status_tag}")

st.divider()

# --- 4. MARKT-CHECK & BEWERTUNGSSKALA ---
status_global = ":green[[data]]" if ist_live else ":red[[no data]]"
st.subheader(f"📈 Markt-Check & China-Exposure Logik {status_global}")

wert = st.number_input("Aktueller Analyse-Wert (%)", value=5, step=1)
st.write(f"### Bewertungsskala: {status_global}")

l, m, r = st.columns(3)

# LINKS: EXTREM TIEF
with l:
    if wert < 10:
        st.error("🔴 **EXTREM TIEF**\n\nStatus: AKTIV")
    else:
        # Default-Ansicht wenn inaktiv
        st.write("⚪ **Extrem Tief**")
        st.info("Möglichkeit: < 10%")

# MITTE: NORMALBEREICH (DEIN WUNSCH: DEFAULT-OPTIK)
with m:
    if 10 <= wert <= 90:
        st.success("🟢 **Normalbereich**\n\nStatus: AKTIV")
    else:
        # Hier ist jetzt die neutrale Default-Anzeige [cite: 2026-02-07]
        st.write("⚪ **Normalbereich**") 
        st.info("Möglichkeit: 10% - 90%")

# RECHTS: EXTREM HOCH
with r:
    if wert > 90:
        st.error("🔴 **EXTREM HOCH**\n\nStatus: AKTIV")
    else:
        st.write("⚪ **Extrem Hoch**")
        st.info("Möglichkeit: > 90%")

st.divider()

# --- 5. BIO-BACKUP ZUSAMMENFASSUNG ---
with st.expander("🧘 Gesundheit & Wandsitz-Routine"):
    st.write("### Routine: **WANDSITZ**")
    st.info("⏱️ Ziel: **05 bis 08 Minuten** [cite: 2026-02-03]")
    st.warning("**WICHTIG:** Gleichmäßig atmen! Keine Preßatmung! [cite: 2025-12-20]")
    # Backup-Info Wandsitz etc. in der Zusammenfassung [cite: 2026-02-03]
    st.write("* **Blutdruck:** Senkung durch Sprossen und Rote Bete [cite: 2025-12-20].")
    st.write("* **Mund:** Keine Mundspülungen mit Chlorhexidin [cite: 2025-12-20].")
    st.write("* **Zähne:** Erst Zeit nach dem Essen vergehen lassen [cite: 2025-12-20].")

with st.expander("✈️ Reisen & Ernährung"):
    st.write("* **Ticket:** Österreich Ticket vorhanden [cite: 2026-01-25].")
    st.write("* **Snacks:** Nüsse für unterwegs [cite: 2026-02-03].")
