import streamlit as st
import yfinance as yf
from datetime import datetime
import time

# --- 1. SETUP ---
st.set_page_config(page_title="Monitor für dich", layout="wide")

if 'h_count' not in st.session_state: 
    st.session_state.h_count = 0

# --- 2. AUTO-PILOT LOGIK ---
jetzt = datetime.now()
ist_boersenzeit = jetzt.weekday() <= 4 and jetzt.hour >= 9 # [cite: 2026-02-07]

# --- 3. HEADER-BEREICH (ZENTRIERT & RECHTSBÜNDIG) ---
# Wir erstellen 3 Spalten: Links (leer), Mitte (Titel), Rechts (Status)
head_l, head_m, head_r = st.columns([1, 2, 1])

with head_m:
    # Der Haupttitel exakt in der Mitte
    st.markdown("<h1 style='text-align: center;'>🖥️ Ansicht für Dich 🖥️</h1>", unsafe_allow_html=True)

with head_r:
    # Programm-Infos rechtsbündig untereinander
    st.write("🚀 **Start:** 08.02.2026 12:02:58")
    if ist_boersenzeit:
        st.success("🟢 LIVE-MODUS") # [cite: 2026-02-07]
    else:
        st.info("🕒 STANDBY") # [cite: 2026-02-07]

st.divider()

# --- 4. BÖRSEN-WETTER (7 EU + 7 US) ---
st.subheader("🌦️ Börsen-Wetter")
w1, w2, w3 = st.columns(3)

with w1:
    st.info("🔴 **Eiszeit / Frost**\n\nKaufzone (RSI < 10%)")
with w2:
    st.info("🟢 **Sonnig / Heiter**\n\nNormalbereich (10%-90%)")
with w3:
    st.info("🟣 **Sturm / Gewitter**\n\nVorsicht (RSI > 90%)")

st.divider()

# --- 5. MARKT-CHECK (EURO/USD, DAX, NASDAQ) ---
st.subheader("📈 Markt-Check")
l, m, r = st.columns(3)
with l: st.metric("Euro/USD", "Aktiv ab 09:00") [cite: 2026-02-07]
with m: st.metric("DAX", "Aktiv ab 09:00") [cite: 2026-02-07]
with r: st.metric("Nasdaq", "Aktiv ab 15:30") [cite: 2026-02-07]

st.divider()

# --- 6. BIO-CHECK ---
st.subheader("🧘 Dein Bio-Check")
c1, c2 = st.columns([1, 1])
with c1:
    if st.button(f"Wandsitz erledigt (Heute: {st.session_state.h_count}x)"):
        st.session_state.h_count += 1
        st.rerun()
with c2:
    st.error("ACHTUNG: Atmen! Keine Pressatmung!")

with st.expander("✈️ Check: Reisen"):
    st.write("🥜 **Nüsse einplanen**") [cite: 2026-02-03]
    st.write("🌱 **Sprossen / Rote Bete**") [cite: 2025-12-20]
    st.write("🎫 **Österreich Ticket**") [cite: 2026-01-25]

# --- 7. AUTOMATIK-REFRESH ---
time.sleep(60)
st.rerun()
