import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, time as dt_time
import time

# --- 1. SETUP & VERSION ---
st.set_page_config(page_title="Monitor für dich", layout="wide")
# Versionshinweis zur Kontrolle auf dem Bildschirm
V_ID = "VER-FIX-95-STAB"

if 'h_count' not in st.session_state: 
    st.session_state.h_count = 0

# --- 2. ZEITSTEUERUNG (EUROPA & USA) ---
jetzt = datetime.now()
# 0=Mo, 6=So. Wochenende ist Samstag(5) und Sonntag(6)
ist_wochenende = jetzt.weekday() >= 5
ist_vor_neun = jetzt.time() < dt_time(9, 0)

# Nur wenn Montag-Freitag UND nach 9 Uhr, wird die Berechnung freigeschaltet
live_berechnung_erlaubt = not ist_wochenende and not ist_vor_neun

# --- 3. HEADER ---
h_links, h_mitte, h_rechts = st.columns([1, 2, 1])
with h_mitte:
    st.markdown(f"<h1 style='text-align: center;'>🖥️ Ansicht für Dich ({V_ID})</h1>", unsafe_allow_html=True)

with h_rechts:
    st.write(f"🚀 Start: {jetzt.strftime('%d.%m.%Y %H:%M:%S')}")
    if not live_berechnung_erlaubt:
        st.warning("🕒 STATUS: Standby (Märkte geschlossen)")
    else:
        st.success("🕒 STATUS: Analyse aktiv")

st.divider()

# --- 4. BÖRSEN-WETTER (DIE LÖSUNG) ---
st.subheader("🌦️ Börsen-Wetter")

meine_ticker = ["OTP.BU", "MOL.BU", "RICHT.BU", "ADS.DE", "SAP.DE", "BAS.DE", "AAPL"]
col1, col2, col3 = st.columns(3)

# Listen vorbereiten
tief, normal, hoch = [], [], []

# WENN NICHT LIVE: Direkt alle in den Normalbereich schieben (Kein RSI-Vergleich!)
if not live_berechnung_erlaubt:
    normal = [(t, "Standby") for t in meine_ticker]
else:
    # Nur hier wird gerechnet. Falls Daten fehlen (z.B. US-Werte vor 15:30), 
    # fangen wir das mit 'try' ab.
    for t in meine_ticker:
        try:
            # Hier findet die eigentliche RSI-Logik statt
            # Falls data leer ist, wird hier abgebrochen und zum 'except' gesprungen
            data = yf.download(t, period="1mo", interval="1d", progress=False)
            if data.empty:
                normal.append((t, "No Data"))
                continue
            
            # (Beispielhafte RSI-Zuweisung zur Veranschaulichung)
            rsi_aktuell = 50 
            
            if rsi_aktuell < 10: tief.append((t, rsi_aktuell))
            elif rsi_aktuell > 90: hoch.append((t, rsi_aktuell))
            else: normal.append((t, rsi_aktuell))
        except:
            normal.append((t, "Wartezeit"))

# Anzeige der Spalten
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

# --- 5. BIO-CHECK (WANDSITZ) ---
st.subheader("🧘 Bio-Check")
b1, b2 = st.columns(2)
with b1:
    if st.button(f"Wandsitz erledigt ({st.session_state.h_count}x)"):
        st.session_state.h_count += 1
        st.rerun()
    st.error("HINWEIS: Atmen nicht vergessen! Keine Pressatmung halten!")

with b2:
    with st.expander("✈️ Reisen & Backup"):
        st.write("🥜 Nüsse für unterwegs (Reisen)")
        st.write("🌱 Blutdruck: Sprossen & Rote Bete")
        st.write("⚠️ Keine Mundspülung (Chlorhexidin)")

time.sleep(60)
st.rerun()
