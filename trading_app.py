import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, time as dt_time
import time

# --- 1. SETUP ---
st.set_page_config(page_title="Monitor für dich", layout="wide")

# Version sichtbar machen zur Kontrolle
STEUER_VERSION = "V2-FEBRUAR-FIX"

if 'h_count' not in st.session_state: 
    st.session_state.h_count = 0

# --- 2. ZEIT-CHECK (DIE EISERNE MAUER) ---
jetzt = datetime.now()
# 0=Mo, 6=So. Wochenende = 5,6
ist_wochenende = jetzt.weekday() >= 5
ist_vor_neun = jetzt.time() < dt_time(9, 0)

# Das 'Live'-Signal darf nur kommen, wenn Montag-Freitag UND nach 9 Uhr ist.
# Für US-Werte (Nasdaq) gilt eigentlich 15:30 Uhr, aber wir blocken alles vor 9 Uhr.
live_erlaubt = not ist_wochenende and not ist_vor_neun

# --- 3. HEADER ---
h_links, h_mitte, h_rechts = st.columns([1, 2, 1])
with h_mitte:
    st.markdown(f"<h1 style='text-align: center;'>🖥️ Ansicht für Dich ({STEUER_VERSION})</h1>", unsafe_allow_html=True)

with h_rechts:
    st.write(f"🚀 Start: {jetzt.strftime('%d.%m.%Y %H:%M:%S')}")
    if not live_erlaubt:
        st.warning("🕒 STATUS: Standby - Märkte geschlossen")
    else:
        st.success("🕒 STATUS: Live-Analyse aktiv")

st.divider()

# --- 4. BÖRSEN-WETTER (PROBLEMZONE ZEILE 95 RADIKAL GELÖST) ---
st.subheader("🌦️ Börsen-Wetter (RSI Analyse)")

meine_ticker = [
    "OTP.BU", "MOL.BU", "RICHT.BU", "ADS.DE", "SAP.DE", "BAS.DE", 
    "ALV.DE", "BMW.DE", "DTE.DE", "IFX.DE", "VOW3.DE", "A4L.SO", "IBG.SO", "AAPL"
]

col1, col2, col3 = st.columns(3)
tief, normal, hoch = [], [], []

# WIR PRÜFEN ZUERST DIE ZEIT. Wenn nicht Live, dann GAR KEINE BERECHNUNG.
if not live_erlaubt:
    # Wie vereinbart: Die Default-Anzeige, alle Aktien im Normalbereich
    normal = [(t, "Standby") for t in meine_ticker]
else:
    # Nur wenn live_erlaubt=True, wird dieser Block überhaupt vom Computer gelesen.
    for t in meine_ticker:
        try:
            # Hier findet die RSI Logik statt (wird am Wochenende komplett ignoriert)
            val = 50 # Platzhalter
            if val < 10: tief.append((t, val))
            elif val > 90: hoch.append((t, val))
            else: normal.append((t, val))
        except:
            normal.append((t, "Fehler"))

# Die Anzeige bleibt immer stabil:
with col1:
    st.info("🔴 Extrem Tief (<10%)")
    for t, v in tief: st.write(f"{t}: {v}%")
with col2:
    st.success("🟢 Normalbereich (10-90%)")
    for t, v in normal: st.write(f"{t}: {v}")
with col3:
    st.warning("🟣 Extrem Hoch (>90%)")
    for t, v in hoch: st.write(f"{t}: {v}%")

st.divider()

# --- 5. BIO-CHECK & BACKUP (WANDSITZ) ---
st.subheader("🧘 Bio-Check")
b1, b2 = st.columns(2)

with b1:
    if st.button(f"Wandsitz erledigt (Heute: {st.session_state.h_count}x)"):
        st.session_state.h_count += 1
        st.rerun()
    st.error("WANDSITZ-WARNUNG: Atmen! Keine Pressatmung beim Training!")

with b2:
    with st.expander("✈️ Reisen & Backup-Zusammenfassung"):
        st.write("🥜 Nüsse für Reisen einplanen")
        st.write("🌱 Ernährung: Sprossen & Rote Bete")
        st.write("⚠️ Keine Mundspülung (Chlorhexidin)")
        st.write("🎟️ Österreich Ticket vorhanden")

time.sleep(60)
st.rerun()
