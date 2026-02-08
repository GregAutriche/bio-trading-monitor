import streamlit as st

# --- SPEICHER ---
if 'w_zeit' not in st.session_state: st.session_state.w_zeit = 30
if 'h_count' not in st.session_state: st.session_state.h_count = 0

st.title("🖥️ Monitor für dich")

# --- 1. BÖRSEN-WETTER (DIE VOLKSMUSIK) ---
# Wir zeigen hier die Möglichkeiten im gleichen Box-Design wie unten [cite: 2026-02-07]
st.subheader("🌦️ Börsen-Wetter: ATR & RSI [no data]")
w1, w2, w3 = st.columns(3)

with w1:
    st.info("🔴 **Extrem Tief**\n\nWindstill / Frost (< 10%)")
with w2:
    st.info("🟢 **Normalbereich**\n\nHeiter bis Wolkig (10% - 90%)")
with w3:
    st.info("🟣 **Extrem Hoch**\n\nSturm / Hitze (> 90%)")

st.divider()

# --- 2. MARKT-CHECK & CHINA-EXPOSURE ---
st.subheader("📈 Markt-Check & China-Exposure [no data]")
l, m, r = st.columns(3)
with l: st.info("🔴 **Extrem Tief** (< 10%)")
with m: st.info("🟢 **Normalbereich** (10% - 90%)")
with r: st.info("🟣 **Extrem Hoch** (> 90%)")

st.divider()

# --- 3. BIO-CHECK LEISTE (Wandsitz & Gesundheit) ---
c1, c2, c3 = st.columns([2, 1, 1])

with c1:
    # Der Wandsitz-Button wechselt bei Klick auf Grün [cite: 2026-02-03, 2026-02-07]
    label = f"Wandsitz: {st.session_state.w_zeit} Sek. Erledigt"
    if st.session_state.h_count > 0:
        st.success(f"✅ {label} | Heute: {st.session_state.h_count}x")
    else:
        if st.button(label): 
            st.session_state.h_count += 1
            st.rerun()
    # Wichtigster Schutzfaktor [cite: 2025-12-20]
    st.error("⚠️ **WICHTIG:** Atmen! Keine Preßatmung!")

with c2:
    st.write("🌱 Sprossen / Rote Bete [cite: 2025-12-20]")
    st.write("🎫 Österreich Ticket [cite: 2026-01-25]")

with c3:
    st.write("🥜 Nüsse einplanen [cite: 2026-02-03]")
    st.write("🚫 Kein Chlorhexidin [cite: 2025-12-20]")
