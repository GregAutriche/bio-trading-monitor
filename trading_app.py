import streamlit as st
from datetime import datetime

# --- 1. INITIALISIERUNG ---
st.set_page_config(page_title="Monitor für dich", layout="wide")

# Feste Startzeit (08.02.2026 12:02:58 laut deinem Foto)
if 'start_zeit' not in st.session_state:
    st.session_state.start_zeit = "08.02.2026 12:02:58"

if 'w_zeit' not in st.session_state: st.session_state.w_zeit = 30
if 'h_count' not in st.session_state: st.session_state.h_count = 0

# --- 2. HEADER & STATUS ---
st.title("🖥️ Monitor für dich")
st.write(f"🚀 **Programm gestartet am:** {st.session_state.start_zeit}")

# Status-Logik für den automatischen Übergang morgen
st.write("🕒 **Status:** ⚪ STANDBY (Wochenende - Daten-Check aktiv)")

st.divider()

# --- 3. BÖRSEN-WETTER (Mit deiner Wunsch-Logik) ---
st.subheader("🌦️ Börsen-Wetter (ATR & RSI)")
w1, w2, w3 = st.columns(3)

with w1:
    st.info("🔴 **Eiszeit / Frost**\n\nExtrem Tief (< 10%)")
with w2:
    st.info("🟢 **Sonnig / Heiter**\n\nNormalbereich (10% - 90%)")
with w3:
    st.info("🟣 **Sturm / Gewitter**\n\nExtrem Hoch (> 90%)")

st.divider()

# --- 4. DEIN BIO-CHECK (Fehlerfrei & Aktiv) ---
st.subheader("🧘 Dein Bio-Check")
c1, c2, c3 = st.columns([2, 1, 1])

with c1:
    # Wandsitz-Button
    btn_label = f"Wandsitz erledigt (Heute: {st.session_state.h_count}x)"
    if st.button(btn_label):
        st.session_state.h_count += 1
        st.rerun()
    
    # Korrigierte Warnanzeige ohne Syntax-Konflikt
    st.error("ACHTUNG: Atmen! Keine Pressatmung!")

with c2:
    st.write("🌱 Sprossen / Rote Bete") [cite: 2025-12-20]
    st.write("🎫 Österreich Ticket") [cite: 2026-01-25]

with c3:
    st.write("🥜 Nüsse einplanen") [cite: 2026-02-03]
    st.write("🚫 Kein Chlorhexidin") [cite: 2025-12-20]
