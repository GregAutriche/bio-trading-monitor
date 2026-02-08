import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# --- 1. KONFIGURATION & SESSION STATE (Speicher für Zähler & Zeit) ---
st.set_page_config(page_title="Monitor für dich", layout="wide")

if 'wandsitz_zeit' not in st.session_state:
    st.session_state.wandsitz_zeit = 30  # Startwert Sekunden [cite: 2026-02-03]
if 'heute_zaehler' not in st.session_state:
    st.session_state.heute_zaehler = 0
if 'serie_tage' not in st.session_state:
    st.session_state.serie_tage = 0
if 'letztes_datum' not in st.session_state:
    st.session_state.letztes_datum = datetime.now().date()

# --- 2. LOGIK FÜR SERIE & RESET ---
heute = datetime.now().date()
if heute > st.session_state.letztes_datum:
    if st.session_state.heute_zaehler == 0:
        st.session_state.serie_tage = 0  # Reset Serie bei verpasstem Tag [cite: 2026-02-03]
    st.session_state.heute_zaehler = 0
    st.session_state.letztes_datum = heute

def wandsitz_erledigt():
    st.session_state.heute_zaehler += 1
    if st.session_state.heute_zaehler == 1:
        st.session_state.serie_tage += 1
    # Automatische Steigerung nach 7 Tagen [cite: 2026-02-03]
    if st.session_state.serie_tage >= 7:
        st.session_state.wandsitz_zeit += 10
        st.session_state.serie_tage = 0

# --- 3. HEADER & MÄRKTE ---
st.title("🖥️ Monitor für dich")
st.write(f"**Letztes Update:** {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")

m_cols = st.columns(3)
ticker_daten = {
    "EUR/USD": "^GDAXI", # Nur als Beispiel für Spalten
    "DAX Index": "^GDAXI",
    "NASDAQ 100": "^IXIC"
}

for i, (name, sym) in enumerate(ticker_daten.items()):
    with m_cols[i]:
        st.metric(label=name, value="Lade...")
        st.caption("☁️ ATR: N/A | 🌡️ RSI: N/A")
        st.write("06.02. 00:00 :red[[no data]]") # [cite: 2026-02-07]

st.divider()

# --- 4. BEWERTUNGSSKALA (Neutral-Logik) ---
st.subheader("📈 Markt-Check & China-Exposure [no data]")
wert = st.number_input("Aktueller Analyse-Wert (%)", value=5)

l, m, r = st.columns(3)
with l: st.info("🔴 **Extrem Tief**\n\n< 10%")
with m: st.info("🟢 **Normalbereich**\n\n10% - 90%")
with r: st.info("🟣 **Extrem Hoch**\n\n> 90%")

st.divider()

# --- 5. DIE BIO-CHECK-LEISTE (UNTEN) ---
# Button Farbe: Grün wenn erledigt, sonst Grau [cite: 2026-02-03, 2026-02-07]
button_label = f"Wandsitz: {st.session_state.wandsitz_zeit} Sek. Erledigt"
if st.session_state.heute_zaehler > 0:
    st.success(f"✅ {button_label} | Heute: {st.session_state.heute_zaehler}x")
else:
    st.button(button_label, on_click=wandsitz_erledigt)

bio_col1, bio_col2, bio_col3 = st.columns([2, 1, 1])

with bio_col1:
    st.error("⚠️ **WICHTIG:** Gleichmäßig atmen! Keine Preßatmung! [cite: 2025-12-20]")
    st.write(f"Serie: **{st.session_state.serie_tage}/7 Tage** bis zur Steigerung.")

with bio_col2:
    st.write("🌱 **Sprossen / Rote Bete** [cite: 2025-12-20]")
    st.write("🎫 **Österreich Ticket** [cite: 2026-01-25]")

with bio_col3:
    st.write("🥜 **Nüsse einplanen** [cite: 2026-02-03]")
    st.write("🚫 **Kein Chlorhexidin** [cite: 2025-12-20]")
