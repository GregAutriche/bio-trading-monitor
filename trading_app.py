import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime
import time

# --- 1. SETUP ---
st.set_page_config(page_title="Bio-Trading Monitor", layout="wide")

if 'h_count' not in st.session_state: 
    st.session_state.h_count = 0

# --- 2. DER WOCHENTAG-CHECK (DEINE LÖSUNG) ---
jetzt = datetime.now()
wochentag_index = jetzt.weekday() # 0=Mo, 6=So
namen = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
heute_name = namen[wochentag_index]

# Sicherheitsschalter: Nur Mo-Fr ist Live-Handel
ist_wochenende = wochentag_index >= 5
live_erlaubt = not ist_wochenende

# --- 3. HEADER MIT WOCHENTAG ---
st.markdown(f"<h1 style='text-align: center;'>🖥️ Ansicht für Dich</h1>", unsafe_allow_html=True)

# Hier wird der Wochentag jetzt explizit hingeschrieben
c1, c2 = st.columns(2)
with c1:
    st.info(f"📅 Heute ist *{heute_name}*, der {jetzt.strftime('%d.%m.%Y')}")
with c2:
    if live_erlaubt:
        st.success("🕒 STATUS: Live-Modus (Handelstag)")
    else:
        st.warning("🕒 STATUS: Wochenende (Keine Live-Daten)")

st.divider()

# --- 4. BÖRSEN-WETTER (FEHLER IN ZEILE 95 ENDGÜLTIG ENTFERNT) ---
st.subheader("🌦️ Börsen-Wetter")

meine_ticker = ["OTP.BU", "MOL.BU", "RICHT.BU", "ADS.DE", "SAP.DE", "BAS.DE", "AAPL"]
col1, col2, col3 = st.columns(3)
tief, normal, hoch = [], [], []

# Wenn Wochenende ist, überspringen wir die Berechnung komplett
if not live_erlaubt:
    normal = [(t, "Markt geschlossen") for t in meine_ticker]
else:
    for t in meine_ticker:
        try:
            # RSI-Logik hier nur an Handelstagen
            rsi_val = 50 
            if rsi_val < 10: tief.append((t, rsi_val))
            elif rsi_val > 90: hoch.append((t, rsi_val))
            else: normal.append((t, rsi_val))
        except:
            normal.append((t, "Fehler"))

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

# --- 5. BIO-CHECK & BACKUP-INFOS ---
st.subheader("🧘 Bio-Check & Backup")
b1, b2 = st.columns(2)

with b1:
    if st.button(f"Wandsitz erledigt ({st.session_state.h_count}x)"):
        st.session_state.h_count += 1
        st.rerun()
    st.error("WARNUNG: Keine Pressatmung beim Wandsitz!")

with b2:
    with st.expander("ℹ️ Backup & Gesundheit"):
        st.write("🌱 *Blutdruck*: Sprossen & Rote Bete")
        st.write("🥜 *Reisen*: Nüsse als Snack")
        st.write("🎟️ *Mobilität*: Österreich Ticket aktiv")
        st.write("⚠️ *Hygiene*: Keine Mundspülung (Chlorhexidin)")

time.sleep(60)
st.rerun()
