import streamlit as st
from datetime import datetime

# --- SETUP ---
if 'w_zeit' not in st.session_state: st.session_state.w_zeit = 30
if 'h_count' not in st.session_state: st.session_state.h_count = 0

st.title("🖥️ Monitor für dich")

# --- 1. DAS BÖRSEN-WETTER (Volatilität & Momentum) ---
st.subheader("🌦️ Börsen-Wetter: Die Volksmusik (ATR & RSI) [no data]")
w1, w2, w3 = st.columns(3)

with w1:
    # Rote Box: Extremes Wetter (z.B. hohe Volatilität oder tiefer RSI)
    st.info("🔴 **Extrem Tief**")
    st.write("Wetter: Windstill / Frost")
    st.caption("< 10%")

with w2:
    # Grüne Box: Normales Wetter
    st.info("🟢 **Normalbereich**")
    st.write("Wetter: Heiter bis Wolkig")
    st.caption("10% - 90%")

with w3:
    # Violette Box: Extremes Wetter (z.B. Überhitzt)
    st.info("🟣 **Extrem Hoch**")
    st.write("Wetter: Hitze / Sturm")
    st.caption("> 90% [cite: 2026-02-07]")

st.divider()

# --- 2. MARKT-CHECK & CHINA-EXPOSURE ---
st.subheader("📈 Markt-Check & China-Exposure [no data]")
l, m, r = st.columns(3)
with l: st.info("🔴 Extrem Tief (< 10%)") [cite: 2026-02-07]
with m: st.info("🟢 Normalbereich (10% - 90%)") [cite: 2026-02-07]
with r: st.info("🟣 Extrem Hoch (> 90%)") [cite: 2026-02-07]

st.divider()

# --- 3. BIO-CHECK LEISTE (Wandsitz & Gesundheit) ---
# Hier sind deine wichtigen Backup-Infos integriert
c1, c2, c3 = st.columns([2, 1, 1])
with c1:
    label = f"Wandsitz: {st.session_state.w_zeit} Sek. Erledigt"
    if st.session_state.h_count > 0:
        st.success(f"✅ {label} | Heute: {st.session_state.h_count}x")
    else:
        if st.button(label): 
            st.session_state.h_count += 1
            st.rerun()
    st.error("⚠️ **Atmen! Keine Preßatmung!** [cite: 2025-12-20]")

with c2:
    st.write("🌱 Sprossen / Rote Bete [cite: 2025-12-20]")
    st.write("🎫 Ö-Ticket dabei [cite: 2026-01-25]")

with c3:
    st.write("🥜 Nüsse einplanen [cite: 2026-02-03]")
    st.write("🚫 Kein Chlorhexidin [cite: 2025-12-20]")

