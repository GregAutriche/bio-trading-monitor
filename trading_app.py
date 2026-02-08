import streamlit as st
from datetime import datetime

# --- SETUP ---
if 'w_zeit' not in st.session_state: st.session_state.w_zeit = 30
if 'h_count' not in st.session_state: st.session_state.h_count = 0
if 'serie' not in st.session_state: st.session_state.serie = 0

st.title("🖥️ Monitor für dich")

# --- 1. VOLKSMUSIK OBEN (Default-Boxen wie gewünscht) ---
st.subheader("📊 Markt-Analyse: ATR & RSI [no data]")
v1, v2, v3 = st.columns(3)

with v1:
    st.info("🔴 **Extrem Tief**\n\n< 10%") # [cite: 2026-02-07]
with v2:
    st.info("🟢 **Normalbereich**\n\n10% - 90%") # [cite: 2026-02-07]
with v3:
    st.info("🟣 **Extrem Hoch**\n\n> 90%") # [cite: 2026-02-07]

st.divider()

# --- 2. MARKT-CHECK MITTE (Deine bekannte Skala) ---
st.subheader("📈 Markt-Check & China-Exposure [no data]")
l, m, r = st.columns(3)
with l: st.info("🔴 **Extrem Tief** (< 10%)")
with m: st.info("🟢 **Normalbereich** (10% - 90%)")
with r: st.info("🟣 **Extrem Hoch** (> 90%)")

st.divider()

# --- 3. BIO-CHECK LEISTE UNTEN ---
c1, c2, c3 = st.columns([2, 1, 1])
with c1:
    label = f"Wandsitz: {st.session_state.w_zeit} Sek. Erledigt"
    if st.session_state.h_count > 0:
        st.success(f"✅ {label} | Heute: {st.session_state.h_count}x")
    else:
        if st.button(label): 
            st.session_state.h_count += 1
            st.rerun()
    st.error("⚠️ **Atmen! Keine Preßatmung!**") # [cite: 2025-12-20]

with c2:
    st.write("🌱 Sprossen / Rote Bete") # [cite: 2025-12-20]
    st.write("🎫 Ö-Ticket") # [cite: 2026-01-25]

with c3:
    st.write("🥜 Nüsse einplanen") # [cite: 2026-02-03]
    st.write("🚫 Kein Chlorhexidin") # [cite: 2025-12-20]
