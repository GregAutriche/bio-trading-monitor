import streamlit as st
from datetime import datetime

# --- 1. SETUP & SESSION STATE ---
st.set_page_config(page_title="Monitor für dich", layout="wide")

# Feste Startzeit (bleibt beim Refresh gleich)
if 'start_zeit' not in st.session_state:
    st.session_state.start_zeit = datetime.now().strftime('%d.%m.%Y %H:%M:%S')

# Wandsitz-Speicher [cite: 2026-02-03]
if 'w_zeit' not in st.session_state: st.session_state.w_zeit = 30
if 'h_count' not in st.session_state: st.session_state.h_count = 0
if 'serie' not in st.session_state: st.session_state.serie = 0

def click_wandsitz():
    st.session_state.h_count += 1
    if st.session_state.h_count == 1:
        st.session_state.serie += 1
    if st.session_state.serie >= 7:
        st.session_state.w_zeit += 10
        st.session_state.serie = 0

# --- 2. HEADER ---
st.title("🖥️ Monitor für dich")
st.write(f"🚀 **Programm gestartet am:** {st.session_state.start_zeit}") #
st.write(f"🕒 **Letztes Daten-Update:** {datetime.now().strftime('%H:%M:%S')} (Sonntag: Markt geschlossen)")

st.divider()

# --- 3. BÖRSEN-WETTER (DEFAULT MODUS) ---
# Saubere Anzeige der Möglichkeiten ohne unnötige Begriffe
st.subheader("🌦️ Börsen-Wetter: ATR & RSI [no data]")
w1, w2, w3 = st.columns(3)

with w1:
    st.info("🔴 **Extrem Tief**\n\nWindstill / Frost (< 10%)") # [cite: 2026-02-07]
with w2:
    st.info("🟢 **Normalbereich**\n\nHeiter bis Wolkig (10% - 90%)") # [cite: 2026-02-07]
with w3:
    st.info("🟣 **Extrem Hoch**\n\nSturm / Hitze (> 90%)") # [cite: 2026-02-07]

st.divider()

# --- 4. MARKT-CHECK & CHINA-EXPOSURE ---
st.subheader("📈 Markt-Check & China-Exposure [no data]")
l, m, r = st.columns(3)
with l: st.info("🔴 **Extrem Tief** (< 10%)") #
with m: st.info("🟢 **Normalbereich** (10% - 90%)")
with r: st.info("🟣 **Extrem Hoch** (> 90%)")

st.divider()

# --- 5. BIO-CHECK LEISTE ---
st.subheader("🧘 Dein Bio-Check")
c1, c2, c3 = st.columns([2, 1, 1])

with c1:
    # Wandsitz-Status
    label = f"Wandsitz: {st.session_state.w_zeit} Sek. Erledigt"
    if st.session_state.h_count > 0:
        st.success(f"✅ {label} | Heute: {st.session_state.h_count}x")
    else:
        st.button(label, on_click=click_wandsitz)
    
    # Wichtigste Warnung [cite: 2025-12-20]
    st.error("⚠️ **Atmen! Keine Preßatmung!**")
    st.caption(f"Serie: {st.session_state.serie}/7 Tage bis zur Steigerung.")

with c2:
    st.write("🌱 **Sprossen / Rote Bete**") # [cite: 2025-12-20]
    st.write("🎫 **Österreich Ticket**") # [cite: 2026-01-25]

with c3:
    st.write("🥜 **Nüsse einplanen**") # [cite: 2026-02-03]
    st.write("🚫 **Kein Chlorhexidin**") # [cite: 2025-12-20]
