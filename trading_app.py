import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime
import time

# --- 1. SETUP ---
st.set_page_config(page_title="Monitor für dich", layout="wide")

# Session State für Wandsitz-Zähler
if 'h_count' not in st.session_state: 
    st.session_state.h_count = 0

# --- 2. HEADER ---
h_links, h_mitte, h_rechts = st.columns([1, 2, 1])

with h_mitte:
    st.markdown("<h1 style='text-align: center;'>🖥️ Ansicht für Dich</h1>", unsafe_allow_html=True)

with h_rechts:
    jetzt = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    st.write(f"🚀 Start: {jetzt}")
    st.info("🕒 STATUS: Live-Modus")

st.divider()

# --- 3. MARKT-CHECK (Einheitliche Formatierung) ---
st.subheader("📈 Markt-Check: Euro/USD | DAX | Nasdaq")
m1, m2, m3 = st.columns(3)

# Beispielwerte (Formatierung: Forex 4 Stellen, Indizes Tausendertrenner)
# In der finalen Version werden diese via yf.Ticker(...).history abgerufen
eur_usd_val = 1.0850
dax_val = 16950.00
nasdaq_val = 17800.00

with m1: 
    st.metric("Euro/USD", f"{eur_usd_val:.4f}")
with m2: 
    st.metric("DAX", f"{dax_val:,.0f}".replace(",", "."))
with m3: 
    st.metric("Nasdaq", f"{nasdaq_val:,.0f}".replace(",", "."))

st.divider()

# --- 4. BÖRSEN-WETTER (10% / 90% Logik) ---
st.subheader("🌦️ Börsen-Wetter (RSI & ADR Analyse)")

# Deine 14 Titel mit den Suffixen für Ungarn (.BU) und Bulgarien (.SO)
# Hier als Platzhalter mit fiktiven RSI/Kurs-Werten zur Demonstration der Logik
titel_liste = [
    {"name": "OTP Bank", "ticker": "OTP.BU", "wert": 8},   # Eiszeit
    {"name": "MOL", "ticker": "MOL.BU", "wert": 45},      # Normal
    {"name": "Richter", "ticker": "RICHT.BU", "wert": 92},# Sturm
    {"name": "SAP", "ticker": "SAP.DE", "wert": 50},
    # ... weitere Titel bis 14 ergänzen
]

w1, w2, w3 = st.columns(3)

with w1:
    st.error("🔴 Eiszeit / Frost (RSI < 10%)")
    for t in titel_liste:
        if t["wert"] < 10:
            st.write(f"**{t['name']}** ({t['ticker']}): {t['wert']}%")
    
with w2:
    st.success("🟢 Sonnig / Heiter (10% - 90%)")
    for t in titel_liste:
        if 10 <= t["wert"] <= 90:
            st.write(f"{t['name']}: {t['wert']}%")
    
with w3:
    st.warning("🟣 Sturm / Gewitter (RSI > 90%)")
    for t in titel_liste:
        if t["wert"] > 90:
            st.write(f"⚠️ **{t['name']}**: {t['wert']}%")

st.divider()

# --- 5. BIO-CHECK ---
st.subheader("🧘 Dein Bio-Check")
b1, b2 = st.columns([1, 1])

with b1:
    if st.button(f"Wandsitz erledigt (Heute: {st.session_state.h_count}x)"):
        st.session_state.h_count += 1
        st.rerun()
    st.error("⚠️ WARNUNG: Atmen! Keine Pressatmung beim Wandsitz!")

with b2:
    with st.expander("✈️ Check: Reisen (Österreich-Ticket)"):
        st.write("🥜 Snack: Nüsse eingepackt?")
        st.write("🌱 Bio: Sprossen & Rote Bete heute verzehrt?")
        st.write("🚫 Verzicht: Kein Chlorhexidin / Keine Phosphate.")

# --- 6. AUTO-REFRESH ---
time.sleep(60)
st.rerun()
