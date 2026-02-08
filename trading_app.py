import streamlit as st
import yfinance as yf
from datetime import datetime

# --- 1. KONFIGURATION & TICKER ---
st.set_page_config(page_title="Trading & Bio Monitor", layout="wide")

# Deine Default-Werte aus den Screenshots integriert
meine_ticker = {
    "EUR/USD": {"symbol": "EURUSD=X", "default": 1.1778},
    "DAX Index": {"symbol": "^GDAXI", "default": 24721.46},
    "NASDAQ 100": {"symbol": "^IXIC", "default": 23031.21}
}

# --- 2. PRIORITÄTS-CHECK: GIBT ES AKTUELLE DATEN? ---
def check_live_status():
    try:
        # Wir prüfen am DAX, ob heute bereits Daten generiert wurden
        test = yf.Ticker("^GDAXI")
        df = test.history(period="1d")
        if not df.empty:
            # Nur wenn das Datum von heute ist, gilt es als [data]
            return df.index[-1].date() == datetime.now().date()
        return False
    except:
        return False

# Die zentrale Entscheidung für das gesamte Dashboard
ist_live = check_live_status()
status_label = ":green[[data]]" if ist_live else ":red[[no data]]"

# --- 3. HEADER & METRIKEN ---
st.title("📊 Dein Trading- & Bio-Monitor")

cols = st.columns(len(meine_ticker))
for i, (name, info) in enumerate(meine_ticker.items()):
    if ist_live:
        t = yf.Ticker(info["symbol"])
        preis = t.history(period="1d")['Close'].iloc[-1]
        zeit_info = datetime.now().strftime('%d.%m. %H:%M')
    else:
        # Wenn keine Daten, nimm die festen Default-Werte
        preis = info["default"]
        zeit_info = "Markt geschlossen"

    format_str = "{:.4f}" if "USD" in name else "{:,.2f}"
    cols[i].metric(label=name, value=format_str.format(preis))
    cols[i].write(f"Status: {status_label}")

st.divider()

# --- 4. MARKT-CHECK & BEWERTUNGSSKALA ---
# Hier wird die Priorität [no data] nun konsequent für beide Überschriften genutzt
st.subheader(f"📈 Markt-Check & China-Exposure Logik {status_label}")
wert = st.number_input("Aktueller Analyse-Wert (%)", value=5, step=1)

st.write(f"### Bewertungsskala: {status_label}")
l, m, r = st.columns(3)

# Logik für alle 3 Bereiche: Wenn inaktiv -> Punkt + Möglichkeit
# LINKS: EXTREM TIEF
with l:
    if wert < 10:
        st.error("🔴 **EXTREM TIEF**\n\nStatus: AKTIV")
    else:
        st.write("🔴 **Extrem Tief**")
        st.info("Möglichkeit: < 10%")

# MITTE: NORMALBEREICH
with m:
    if 10 <= wert <= 90:
        st.success("🟢 **Normalbereich**\n\nStatus: AKTIV")
    else:
        st.write("🟢 **Normalbereich**")
        st.info("Möglichkeit: 10% - 90%")

# RECHTS: EXTREM HOCH
with r:
    if wert > 90:
        st.error("🔴 **EXTREM HOCH**\n\nStatus: AKTIV")
    else:
        st.write("🟣 **Extrem Hoch**")
        st.info("Möglichkeit: > 90%")

st.divider()

# --- 5. BIO-BACKUP (WANDSITZ & GESUNDHEIT) ---
with st.expander("🧘 Gesundheit & Wandsitz-Routine"):
    st.write("### Routine: **WANDSITZ**")
    st.info("⏱️ Ziel: **05 bis 08 Minuten** [cite: 2026-02-03]")
    st.warning("**WICHTIG:** Gleichmäßig atmen! Keine Preßatmung (Valsalva-Manöver)! [cite: 2025-12-20]")
    st.write("* **Mundhygiene:** Keine Mundspülungen mit Chlorhexidin verwenden [cite: 2025-12-20].")
    st.write("* **Timing:** Nicht unmittelbar nach dem Essen Zähne putzen [cite: 2025-12-20].")

with st.expander("✈️ Reisen & Ernährung"):
    st.write(f"* **Ticket:** Österreich-Ticket vorhanden [cite: 2026-01-25].")
    st.write("* **Snacks:** Nüsse für die Reise einplanen [cite: 2026-02-03].")
    st.write("* **Blutdruck:** Fokus auf Sprossen und Rote Bete [cite: 2025-12-20].")
    st.write("* **Vorsicht:** Phosphate in Fertiggerichten und Grapefruit meiden [cite: 2025-12-20].")
