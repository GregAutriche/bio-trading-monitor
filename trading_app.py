import streamlit as st
import yfinance as yf
from datetime import datetime
import time

# --- SETUP ---
st.set_page_config(page_title="Monitor für dich", layout="wide")

if 'h_count' not in st.session_state: 
    st.session_state.h_count = 0

# Zeit-Logik für Montag 09:00 Uhr
jetzt = datetime.now()
ist_boersenzeit = jetzt.weekday() <= 4 and jetzt.hour >= 9

# --- HEADER (Titel Mitte, Status Rechts) ---
h_links, h_mitte, h_rechts = st.columns([1, 2, 1])

with h_mitte:
    st.markdown("<h1 style='text-align: center;'>🖥️ Ansicht für Dich</h1>", unsafe_allow_html=True)

with h_rechts:
    st.write("🚀 **Start:** 08.02.2026 12:02:58")
    if ist_boersenzeit:
        st.success("🟢 LIVE-MODUS")
    else:
        st.info("🕒 STANDBY")

st.divider()

# --- 1. MARKT-CHECK & LIVE-INDIZES (Jetzt oben) ---
st.subheader("📈 Markt-Check & Live-Indizes")
m1, m2, m3 = st.columns(3)
with m1: st.metric("Euro/USD", "Aktiv ab 09:00")
with m2: st.metric("DAX", "Aktiv ab 09:00")
with m3: st.metric("Nasdaq", "Aktiv ab 15:30")

st.divider()

# --- 2. BÖRSEN-WETTER (Darunter) ---
st.subheader("🌦️ Börsen-Wetter")
w1, w2, w3 = st.columns(3)

with w1:
    st.info("🔴 **Eiszeit / Frost**\n\nKaufzone (RSI < 10%)")
with w2:
    st.info("🟢 **Sonnig / Heiter**\n\nNormalbereich (10%-90%)")
with w3:
    st.info("🟣 **Sturm / Gewitter**\n\nVorsicht (RSI > 90%)")

st.divider()

# --- 3. BIO-CHECK ---
st.subheader("🧘 Dein Bio-Check")
b1, b2 = st.columns([1, 1])

with b1:
    if st.button(f"Wandsitz erledigt (Heute: {st.session_state.h_count}x)"):
        st.session_state.h_count += 1
        st.rerun()
    # WICHTIG: Die Warnung ohne Quellcode-Zitate im String, um Fehler zu vermeiden
    st.error("ACHTUNG: Atmen! Keine Pressatmung!")

with b2:
    with st.expander("✈️ Check: Reisen"):
        st.write("🥜 **Nüsse einplanen**")
        st.write("🌱 **Sprossen / Rote Bete**")

# Automatischer Refresh jede Minute
time.sleep(60)
st.rerun()
