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
def hole_live_daten(info):
    try:
        t = yf.Ticker(info["symbol"])
        df = t.history(period="1d")
        if not df.empty and df.index[-1].date() == datetime.now().date():
            return df['Close'].iloc[-1], df.index[-1].strftime('%d.%m. %H:%M'), True
        return info["default"], info["datum"], False # Nutze Default-Datum wenn nicht live
    except:
        return info["default"], info["datum"], False

# --- 3. HEADER & METRIKEN ---
st.title("📊 Dein Trading- & Bio-Monitor")
cols = st.columns(len(meine_ticker))
ist_irgendwas_live = False

for i, (name, info) in enumerate(meine_ticker.items()):
    preis, zeit, live = hole_live_daten(info)
    if live: ist_irgendwas_live = True
    
    format_str = "{:.4f}" if "USD" in name else "{:,.2f}"
    cols[i].metric(label=name, value=format_str.format(preis))
    
    # Status-Anzeige: Datum BLEIBT, [no data] kommt dazu
    status_label = ":green[[data]]" if live else ":red[[no data]]"
    cols[i].write(f"{zeit} {status_label}")

st.divider()

# --- 4. MARKT-CHECK & BEWERTUNGSSKALA ---
# Status für die Überschriften
global_status = ":green[[data]]" if ist_irgendwas_live else ":red[[no data]]"

st.subheader(f"📈 Markt-Check & China-Exposure Logik {global_status}")
wert = st.number_input("Aktueller Analyse-Wert (%)", value=5, step=1)

st.write(f"### Bewertungsskala: {global_status}")
l, m, r = st.columns(3)

# EINHEITLICHE LOGIK FÜR ALLE DREI BEREICHE
# LINKS: EXTREM TIEF
with l:
    if wert < 10: # Deine Regel: < 10%
        st.error("🔴 **EXTREM TIEF**\n\nStatus: AKTIV")
    else:
        st.write("🔴 **Extrem Tief**")
        st.info("Möglichkeit: < 10%")

# MITTE: NORMALBEREICH
with m:
    if 10 <= wert <= 90: # Deine Regel: 10% - 90%
        st.success("🟢 **Normalbereich**\n\nStatus: AKTIV")
    else:
        st.write("🟢 **Normalbereich**")
        st.info("Möglichkeit: 10% - 90%")

# RECHTS: EXTREM HOCH
with r:
    if wert > 90: # Deine Regel: > 90%
        st.error("🔴 **EXTREM HOCH**\n\nStatus: AKTIV")
    else:
        st.write("🟣 **Extrem Hoch**")
        st.info("Möglichkeit: > 90%")

st.divider()

# --- 5. BIO-BACKUP (WANDSITZ) ---
with st.expander("🧘 Gesundheit & Wandsitz-Routine"):
    st.write("### Routine: **WANDSITZ**")
    st.info("⏱️ Ziel: **05 bis 08 Minuten**")
    st.warning("**WICHTIG:** Gleichmäßig atmen! Keine Preßatmung (Valsalva-Manöver)!")
    st.write("* **Mundhygiene:** Keine Mundspülungen mit Chlorhexidin.")
    st.write("* **Zähne:** Nicht direkt nach dem Essen putzen.")
    st.write("* **Ernährung:** Fokus auf Sprossen und Rote Bete.")
