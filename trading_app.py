import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime
import time

# --- 1. SETUP ---
st.set_page_config(page_title="Monitor für dich", layout="wide")

if 'h_count' not in st.session_state: 
    st.session_state.h_count = 0

# --- 2. HEADER ---
h_links, h_mitte, h_rechts = st.columns([1, 2, 1])

with h_mitte:
    st.markdown("<h1 style='text-align: center;'>🖥️ Ansicht für Dich 🖥️</h1>", unsafe_allow_html=True)

with h_rechts:
    jetzt = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    st.write(f"🚀 Start: {jetzt}")
    st.info("🕒 STATUS: Aktiv / Live-Formatierung")

st.divider()

# --- 3. MARKT-CHECK (FORMAT: 4 Stellen Währung / 2 Stellen Indizes) ---
st.subheader("📈 Markt-Check: Euro/USD | DAX | Nasdaq")
m1, m2, m3 = st.columns(3)

# Beispielwerte für die Anzeige
val_eurusd = 1.0850
val_dax = 16950.45
val_nasdaq = 17800.12

with m1: 
    # Währung: 4 Nachkommastellen
    st.metric("Euro/USD", f"{val_eurusd:.4f}")
with m2: 
    # DAX: 2 Nachkommastellen + Tausendertrenner (Deutsch)
    st.metric("DAX", f"{val_dax:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
with m3: 
    # Nasdaq: 2 Nachkommastellen + Tausendertrenner (Deutsch)
    st.metric("Nasdaq", f"{val_nasdaq:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

st.divider()

# --- 4. BÖRSEN-WETTER (10/90 Logik) ---
st.subheader("🌦️ Börsen-Wetter 🌦️ (RSI & ADR Analyse)")

# Hier pflegst du deine 14 Titel ein
meine_titel = [] 

w1, w2, w3 = st.columns(3)

with w1:
    st.info("🔴 Eiszeit / Frost (RSI < 10%)")
    for t in meine_titel:
        if t["rsi"] < 10:
            st.write(f"{t['name']} ({t['ticker']}): {t['rsi']}%")
    
with w2:
    st.info("🟢 Sonnig / Heiter (10% - 90%)")
    for t in meine_titel:
        if 10 <= t["rsi"] <= 90:
            st.write(f"{t['name']}: {t['rsi']}%")
    
with w3:
    st.info("🟣 Sturm / Gewitter (RSI > 90%)")
    for t in meine_titel:
        if t["rsi"] > 90:
            st.write(f"{t['name']}: {t['rsi']}%")

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
        st.write("🥜 Nüsse einplanen (Snack für das Österreich-Ticket)")
        st.write("🌱 Sprossen / Rote Bete")
        st.write("⚠️ Keine Mundspülung (Chlorhexidin) / Keine Phosphate")

# --- 6. AUTO-REFRESH ---
time.sleep(60)
st.rerun()
