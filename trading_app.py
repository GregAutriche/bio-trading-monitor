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
            return df['Close'].iloc[-1], df.index[-1].strftime('%d.%m. %H:%M'), False
        return info["default"], "06.02. 00:00", True
    except:
        return info["default"], "Fehler", True

# --- 3. HEADER ---
st.title("📊 Dein Trading- & Bio-Monitor")
cols = st.columns(len(meine_ticker))
for i, (name, info) in enumerate(meine_ticker.items()):
    preis, zeit, is_def = hole_daten(info)
    format_str = "{:.4f}" if "USD" in name else "{:,.2f}"
    cols[i].metric(label=name, value=format_str.format(preis))
    if is_def:
        cols[i].write(f":green[Default ({zeit})]") # Anzeige, dass Default aktiv ist
    else:
        cols[i].write(f"Live: {zeit}")

st.divider()

# --- 4. MARKT-CHECK LOGIK (PASSIV VS. AKTIV) ---
st.subheader("📈 Markt-Check & China-Exposure Logik")
wert = st.number_input("Aktueller Analyse-Wert (%)", value=5, step=1)

st.write("### Bewertungs-Skala:")
l, m, r = st.columns(3)

# LINKS: EXTREM TIEF
with l:
    if wert < 10:
        st.error("🔴 **EXTREM TIEF**\n\nStatus: AKTIV")
    else:
        st.info("⚪ Extrem Tief (Möglichkeit: < 10%)")

# MITTE: NORMALBEREICH (DEIN WUNSCH)
with m:
    if 10 <= wert <= 90:
        # AKTIV-Zustand: Volles Grün
        st.success("🟢 **NORMALBEREICH**\n\nStatus: AKTIV")
    else:
        # PASSIV-Zustand: Zeigt in Grün, was möglich ist
        st.write(":green[🟢 **Normalbereich** (Möglichkeit: 10% - 90%)]")
        st.info("Aktuell: Inaktiv")

# RECHTS: EXTREM HOCH
with r:
    if wert > 90:
        st.error("🔴 **EXTREM HOCH**\n\nStatus: AKTIV")
    else:
        st.info("⚪ Extrem Hoch (Möglichkeit: > 90%)")

st.divider()

# --- 5. BIO-BACKUP ---
with st.expander("🧘 Gesundheit & Wandsitz-Routine"):
    st.write("### Routine: **WANDSITZ**")
    st.info("⏱️ Ziel: 05 bis 08 Minuten [cite: 2026-02-03]")
    st.warning("**Wichtig:** Gleichmäßig atmen! Keine Preßatmung! [cite: 2025-12-20]")
