import streamlit as st
from datetime import datetime

# --- 1. SETUP & SESSION STATE ---
st.set_page_config(page_title="Monitor für dich", layout="wide")

if 'start_zeit' not in st.session_state:
    st.session_state.start_zeit = "08.02.2026 12:02:58" #

if 'h_count' not in st.session_state: st.session_state.h_count = 0

# --- 2. DEINE QUALITÄTS-LISTE (7 EU + 7 US) ---
# Diese Werte erfüllen deine Kriterien: niedrige Schulden, hohe Substanz [cite: 2026-02-07]
eu_titel = ["ASML.AS", "SAP.DE", "MC.PA", "SIE.DE", "OR.PA", "AIR.PA", "AZN.L"]
us_titel = ["MSFT", "AAPL", "GOOGL", "V", "MA", "PG", "JNJ"]

# --- 3. HEADER & STATUS ---
st.title("🖥️ Monitor für dich")
st.write(f"🚀 **Programm gestartet am:** {st.session_state.start_zeit}")
st.write("🕒 **Status:** ⚪ STANDBY (Wochenende - 14 Qualitätswerte geladen)")

st.divider()

# --- 4. BÖRSEN-WETTER (7 EU + 7 US ANALYSE) ---
st.subheader("🌦️ Börsen-Wetter: 14 Qualitäts-Champions")
w1, w2, w3 = st.columns(3)

with w1:
    st.info("🔴 **Eiszeit / Frost**\n\nKaufzone (< 10%)")
with w2:
    st.info("🟢 **Sonnig / Heiter**\n\nNormalbereich (10% - 90%)")
with w3:
    st.info("🟣 **Sturm / Gewitter**\n\nÜberhitzt (> 90%)")

st.divider()

# --- 5. MARKT-CHECK & CHINA-EXPOSURE ---
st.subheader("📈 Markt-Check & China-Exposure (DAX Fokus)") [cite: 2026-02-07]
l, m, r = st.columns(3)
with l: st.info("🔴 Extrem Tief (< 10%)")
with m: st.info("🟢 Normalbereich (10% - 90%)")
with r: st.info("🟣 Extrem Hoch (> 90%)")

st.divider()

# --- 6. BIO-CHECK LEISTE (STABIL & SICHER) ---
st.subheader("🧘 Dein Bio-Check")
c1, c2, c3 = st.columns([2, 1, 1])

with c1:
    if st.button(f"Wandsitz erledigt (Heute: {st.session_state.h_count}x)"):
        st.session_state.h_count += 1
        st.rerun()
    # Wichtigste Blutdruck-Regel [cite: 2025-12-20]
    st.error("ACHTUNG: Atmen! Keine Pressatmung!")

with c2:
    st.write("🌱 Sprossen / Rote Bete") [cite: 2025-12-20]
    st.write("🎫 Österreich Ticket") [cite: 2026-01-25]

with c3:
    st.write("🥜 Nüsse einplanen") [cite: 2026-02-03]
    st.write("🚫 Kein Chlorhexidin") [cite: 2025-12-20]
