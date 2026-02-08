import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, time as dt_time
import time

# --- 1. SETUP ---
st.set_page_config(page_title="Monitor für dich", layout="wide")

if 'h_count' not in st.session_state: 
    st.session_state.h_count = 0

# --- 2. DIE MONTAGS-REGEL (TÜRSTEHER) ---
def ist_startzeit_vorbei():
    jetzt = datetime.now()
    # Nur Montag(0) bis Freitag(4)
    if jetzt.weekday() >= 5: 
        return False
    # Erst ab 09:00 Uhr
    if jetzt.time() < dt_time(9, 0):
        return False
    return True

live_erlaubt = ist_startzeit_vorbei()

# --- 3. HEADER ---
h_links, h_mitte, h_rechts = st.columns([1, 2, 1])
with h_mitte:
    st.markdown("<h1 style='text-align: center;'>🖥️ Ansicht für Dich</h1>", unsafe_allow_html=True)

with h_rechts:
    st.write(f"🚀 Start: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
    # Hier prüfst du die Version:
    status_msg = "Live-Analyse aktiv" if live_erlaubt else "Warten auf Montag 09:00"
    st.info(f"🕒 STATUS: {status_msg}")

st.divider()

# --- 4. BÖRSEN-WETTER (DIE DEFAULT ANZEIGE OHNE ZEILE 95 FEHLER) ---
st.subheader("🌦️ Börsen-Wetter (RSI Analyse)")

meine_ticker = [
    "OTP.BU", "MOL.BU", "RICHT.BU", "ADS.DE", "SAP.DE", "BAS.DE", 
    "ALV.DE", "BMW.DE", "DTE.DE", "IFX.DE", "VOW3.DE", "A4L.SO", "IBG.SO", "AAPL"
]

w1, w2, w3 = st.columns(3)

# Wir lassen die fehlerhafte Logik heute (Sonntag) komplett weg:
if not live_erlaubt:
    with w1:
        st.info("🔴 Extrem Tief (RSI < 10%)")
        st.markdown("<span style='color:red;'>[No Data]</span>", unsafe_allow_html=True)
    with w2:
        st.success("🟢 Normalbereich (10% - 90%)") #
        for t in meine_ticker:
            st.write(f"{t}: Standby") # Alle bekannt als Default
    with w3:
        st.warning("🟣 Extrem Hoch (RSI > 90%)") #
        st.markdown("<span style='color:red;'>[No Data]</span>", unsafe_allow_html=True)
else:
    # Erst hier würde der Code mit Zeile 95 stehen
    st.write("Berechne Live-Daten...")

st.divider()

# --- 5. BIO-CHECK (WANDSITZ & REISEN) ---
st.subheader("🧘 Dein Bio-Check")
b1, b2 = st.columns(2)

with b1:
    if st.button(f"Wandsitz erledigt (Heute: {st.session_state.h_count}x)"): #
        st.session_state.h_count += 1
        st.rerun()
    st.error("WANDSITZ-WARNUNG: Atmen! Keine Pressatmung halten!")

with b2:
    with st.expander("✈️ Reisen & Gesundheit"):
        st.write("🥜 Nüsse einplanen")
        st.write("🌱 Sprossen / Rote Bete für Blutdruck")
        st.write("⚠️ Keine Mundspülung (Chlorhexidin)")

time.sleep(60)
st.rerun()
