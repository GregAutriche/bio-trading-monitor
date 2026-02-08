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
    cols[i].write(f"{zeit} :red[[no data]]" if not live else f"{zeit} :green[[data]]")

st.divider()

# --- 4. MARKT-CHECK & BEWERTUNGSSKALA ---
status_label = ":red[[no data]]" if not ist_live else ":green[[data]]"
st.subheader(f"📈 Markt-Check & China-Exposure Logik {status_label}")

wert = st.number_input("Aktueller Analyse-Wert (%)", value=5, step=1)
st.write(f"### Bewertungsskala: {status_label}")

l, m, r = st.columns(3)

# LOGIK: WENN NO DATA -> ALLES NEUTRAL (WIE NORMALBEREICH)
# WENN DATA -> DEINE REGELN (10/90) AKTIVIEREN [cite: 2026-02-07]

with l:
    # Nur aktiv rot, wenn Daten da sind UND der Wert passt
    if ist_live and wert < 10:
        st.error("🔴 **EXTREM TIEF**\n\nStatus: AKTIV")
    else:
        st.write("⚪ **Extrem Tief**")
        st.info("Möglichkeit: < 10%")

with m:
    if ist_live and 10 <= wert <= 90:
        st.success("🟢 **Normalbereich**\n\nStatus: AKTIV")
    else:
        st.write("🟢 **Normalbereich**")
        st.info("Möglichkeit: 10% - 90%")

with r:
    if ist_live and wert > 90:
        st.error("🔴 **EXTREM HOCH**\n\nStatus: AKTIV")
    else:
        st.write("⚪ **Extrem Hoch**")
        st.info("Möglichkeit: > 90%")

st.divider()

# --- 5. ZUSAMMENFASSUNG & BACKUP-INFO ---
with st.expander("🧘 Gesundheit & Wandsitz-Routine"):
    st.write("### Routine: **WANDSITZ**")
    st.info("⏱️ Ziel: **05 bis 08 Minuten** [cite: 2026-02-03]")
    st.warning("**WICHTIG:** Gleichmäßig atmen! Keine Preßatmung (Valsalva)! [cite: 2025-12-20]")
    st.write("* **Blutdruck:** Senkung durch Sprossen und Rote Bete [cite: 2025-12-20].")
    st.write("* **Warnung:** Keine Mundspülungen mit Chlorhexidin [cite: 2025-12-20].")
    st.write("* **Timing:** Zähneputzen nicht direkt nach dem Essen [cite: 2025-12-20].")

with st.expander("✈️ Reisen & Ernährung"):
    st.write("* **Ticket:** Österreich Ticket vorhanden [cite: 2026-01-25].")
    st.write("* **Snacks:** Nüsse für die Reise einplanen [cite: 2026-02-03].")
    st.write("* **Vorsicht:** Phosphate und Grapefruit-Wechselwirkungen beachten [cite: 2025-12-20].")
