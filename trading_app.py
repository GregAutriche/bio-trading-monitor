import streamlit as st
import yfinance as yf
from datetime import datetime

# --- 1. KONFIGURATION & TICKER ---
st.set_page_config(page_title="Trading & Bio Monitor", layout="wide")

meine_ticker = {
    "EUR/USD": {"symbol": "EURUSD=X", "default": 1.1778},
    "DAX Index": {"symbol": "^GDAXI", "default": 24721.46},
    "NASDAQ 100": {"symbol": "^IXIC", "default": 23031.21}
}

# --- 2. ZENTRALE DATEN-ABFRAGE (DIE ENTSCHEIDUNG) ---
def check_daten_status():
    # Wir prüfen beispielhaft am DAX, ob heute gehandelt wird
    try:
        test_ticker = yf.Ticker("^GDAXI")
        df = test_ticker.history(period="1d")
        if not df.empty:
            # Check, ob der Zeitstempel von heute ist
            ist_heute = df.index[-1].date() == datetime.now().date()
            return ist_heute
        return False
    except:
        return False

# Die wichtigste Variable für das gesamte Programm
ist_live = check_daten_status()
status_label = ":green[[data]]" if ist_live else ":red[[no data]]"

# --- 3. DASHBOARD HEADER ---
st.title("📊 Dein Trading- & Bio-Monitor")

cols = st.columns(len(meine_ticker))
for i, (name, info) in enumerate(meine_ticker.items()):
    # Falls nicht live, nimm den Default-Wert aus deinem Screenshot
    if not ist_live:
        preis = info["default"]
        zeit_info = "06.02. 00:00"
    else:
        # Hier käme der Live-Abruf (vereinfacht für die Struktur)
        t = yf.Ticker(info["symbol"])
        preis = t.history(period="1d")['Close'].iloc[-1]
        zeit_info = datetime.now().strftime('%d.%m. %H:%M')

    format_str = "{:.4f}" if "USD" in name else "{:,.2f}"
    cols[i].metric(label=name, value=format_str.format(preis))
    cols[i].write(f"Status: {status_label}")

st.divider()

# --- 4. MARKT-CHECK & BEWERTUNGSSKALA ---
st.subheader(f"📈 Markt-Check & China-Exposure Logik {status_label}")
wert = st.number_input("Aktueller Analyse-Wert (%)", value=5, step=1)

st.write(f"### Bewertungsskala: {status_label}")
l, m, r = st.columns(3)

# Logik für alle 3 Bereiche (Punkt + Möglichkeit im inaktiven Zustand)
# LINKS: EXTREM TIEF
with l:
    if wert < 10: # Regel: < 10% [cite: 2026-02-07]
        st.error("🔴 **EXTREM TIEF**\n\nStatus: AKTIV")
    else:
        st.write("🔴 **Extrem Tief**")
        st.info("Möglichkeit: < 10%")

# MITTE: NORMALBEREICH
with m:
    if 10 <= wert <= 90: # Regel: 10% - 90% [cite: 2026-02-07]
        st.success("🟢 **Normalbereich**\n\nStatus: AKTIV")
    else:
        st.write("🟢 **Normalbereich**")
        st.info("Möglichkeit: 10% - 90%")

# RECHTS: EXTREM HOCH
with r:
    if wert > 90: # Regel: > 90% [cite: 2026-02-07]
        st.error("🔴 **EXTREM HOCH**\n\nStatus: AKTIV")
    else:
        st.write("🟣 **Extrem Hoch**")
        st.info("Möglichkeit: > 90%")

st.divider()

# --- 5. BIO-BACKUP & ROUTINEN ---
with st.expander("🧘 Gesundheit & Wandsitz-Routine"):
    st.write("### Routine: **WANDSITZ**")
    st.info("⏱️ Ziel: **05 bis 08 Minuten** [cite: 2026-02-03]")
    st.warning("**Sicherheitsregel:** Gleichmäßig atmen! Keine Preßatmung! [cite: 2025-12-20]")
    st.write("* Keine Mundspülungen mit Chlorhexidin [cite: 2025-12-20]")
    st.write("* Nicht direkt nach dem Essen Zähne putzen [cite: 2025-12-20]")

with st.expander("✈️ Reisen & Ernährung"):
    st.write(f"* **Ticket:** Österreich-Ticket vorhanden [cite: 2026-01-25]")
    st.write("* **Snacks:** Nüsse einplanen [cite: 2026-02-03]")
    st.write("* **Ernährung:** Sprossen & Rote Bete zur Blutdrucksenkung [cite: 2025-12-20]")
    st.write("* **Vorsicht:** Phosphate in Fertiggerichten meiden [cite: 2025-12-20]")

# --- 6. 7-TAGE ÜBERSICHT ---
with st.expander("📅 Letzte 7 Tage Übersicht"):
    st.table({
        "Datum": ["02.02.", "03.02.", "04.02.", "05.02.", "06.02.", "07.02.", "08.02."],
        "Wandsitz (Min)": [6, 5, 7, 6, 8, 5, "-"],
        "Analyse-Wert (%)": [15, 12, 8, 45, 92, 5, wert],
        "Status": ["Normal", "Normal", "Tief", "Normal", "Hoch", "Tief", "Check"]
    })
