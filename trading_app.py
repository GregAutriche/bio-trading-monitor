import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime
import time

# --- 1. SETUP ---
st.set_page_config(page_title="Monitor für dich", layout="wide")

if 'h_count' not in st.session_state: 
    st.session_state.h_count = 0

# --- 2. HEADER (Titel Mitte / Status Rechts) ---
h_links, h_mitte, h_rechts = st.columns([1, 2, 1])

with h_mitte:
    st.markdown("<h1 style='text-align: center;'>🖥️ Ansicht für Dich</h1>", unsafe_allow_html=True)

with h_rechts:
    st.write("🚀 **Start:** 08.02.2026 12:02:58")
    st.info("🕒 STATUS: Standby / Bereit für Live-Daten")

st.divider()

# --- 3. MARKT-CHECK (EURO/USD, DAX, NASDAQ) ---
st.subheader("📈 Markt-Check: Euro/USD | DAX | Nasdaq")
m1, m2, m3 = st.columns(3)
with m1: st.metric("Euro/USD", "1.0850", "+0.002")
with m2: st.metric("DAX", "16.950", "+0.5%")
with m3: st.metric("Nasdaq", "17.800", "+0.8%")

st.divider()

# --- 4. BÖRSEN-WETTER (RSI & ADR LOGIK) ---
st.subheader("🌦️ Börsen-Wetter (RSI & ADR Analyse)")
# Hier fließen deine 14 Titel ein
w1, w2, w3 = st.columns(3)

with w1:
    st.info("🔴 **Eiszeit / Frost** (RSI < 10%)")
    st.write("**Titel im Kaufbereich:**")
    # Hier erscheinen die Titel mit ihrem ADR-Wert
    
with w2:
    st.info("🟢 **Sonnig / Heiter** (10% - 90%)")
    st.write("**Titel im Normalbereich:**")
    
with w3:
    st.info("🟣 **Sturm / Gewitter** (RSI > 90%)")
    st.write("**Titel Überhitzt:**")

st.divider()

# --- 5. BIO-CHECK ---
st.subheader("🧘 Dein Bio-Check")
b1, b2 = st.columns([1, 1])

with b1:
    if st.button(f"Wandsitz erledigt (Heute: {st.session_state.h_count}x)"):
        st.session_state.h_count += 1
        st.rerun()
    st.error("ACHTUNG: Atmen! Keine Pressatmung!")

with b2:
    with st.expander("✈️ Check: Reisen"):
        st.write("🥜 **Nüsse einplanen**")
        st.write("🌱 **Sprossen / Rote Bete**")

# --- 6. AUTO-REFRESH ---
time.sleep(60)
st.rerun()
