import streamlit as st
from datetime import datetime

# --- 1. INITIALISIERUNG ---
st.set_page_config(page_title="Monitor für dich", layout="wide")

# Feste Startzeit (08.02.2026 12:02:58 laut deinem Foto)
if 'start_zeit' not in st.session_state:
    st.session_state.start_zeit = "08.02.2026 12:02:58"

if 'h_count' not in st.session_state: st.session_state.h_count = 0

# --- 2. HEADER & STATUS ---
st.title("🖥️ Monitor für dich")
st.write(f"🚀 **Programm gestartet am:** {st.session_state.start_zeit}")
st.write("🕒 **Status:** ⚪ STANDBY (Wochenende)")

st.divider()

# --- 3. BÖRSEN-WETTER (Sonnig/Sturm Logik) ---
st.subheader("🌦️ Börsen-Wetter (ATR & RSI)")
w1, w2, w3 = st.columns(3)

with w1:
    st.info("🔴 **Eiszeit / Frost**\n\nExtrem Tief (< 10%)")
with w2:
    st.info("🟢 **Sonnig / Heiter**\n\nNormalbereich (10% - 90%)")
with w3:
    st.info("🟣 **Sturm / Gewitter**\n\nExtrem Hoch (> 90%)")

st.divider()

# --- 4. MARKT-CHECK & CHINA-EXPOSURE ---
st.subheader("📈 Markt-Check & China-Exposure [no data]")
l, m, r = st.columns(3)
with l: st.info("🔴 Extrem Tief (< 10%)")
with m: st.info("🟢 Normalbereich (10% - 90%)")
with r: st.info("🟣 Extrem Hoch (> 90%)")

st.divider()

# --- 5. DEIN BIO-CHECK ---
st.subheader("🧘 Dein Bio-Check")
c1, c2, c3 = st.columns([2, 1, 1])

with c1:
    if st.button(f"Wandsitz erledigt (Heute: {st.session_state.h_count}x)"):
        st.session_state.h_count += 1
        st.rerun()
    # Vereinfachte Fehlermeldung für maximale Stabilität
    st.error("ACHTUNG: Atmen! Keine Pressatmung!")

with c2:
    st.write("🌱 Sprossen / Rote Bete")
    st.write("🎫 Österreich Ticket")

with c3:
    st.write("🥜 Nüsse einplanen")
    st.write("🚫 Kein Chlorhexidin")
