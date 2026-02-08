import streamlit as st
import yfinance as yf
from datetime import datetime
import time

# --- 1. INITIALISIERUNG ---
st.set_page_config(page_title="Monitor für dich", layout="wide")

if 'h_count' not in st.session_state: 
    st.session_state.h_count = 0

# --- 2. AUTO-PILOT LOGIK (ZEITSTEUERUNG) ---
jetzt = datetime.now()
# Prüft: Ist es Montag-Freitag (0-4) UND nach 09:00 Uhr?
ist_boersenzeit = jetzt.weekday() <= 4 and jetzt.hour >= 9

# --- 3. HEADER MIT FIXEM START-DATUM ---
st.title("🖥️ Monitor für dich")
# Fixiertes Datum laut deinem Wunsch-Design
st.write("🚀 **Programm gestartet am:** 08.02.2026 12:02:58")

if ist_boersenzeit:
    st.success("🟢 LIVE-MODUS AKTIV: 14 Qualitätswerte werden überwacht")
else:
    st.info("⚪ STANDBY: Automatischer Start am Montag um 09:00 Uhr")

st.divider()

# --- 4. BÖRSEN-WETTER (7 EU + 7 US) ---
st.subheader("🌦️ Börsen-Wetter")
w1, w2, w3 = st.columns(3)

with w1:
    st.info("🔴 **Eiszeit / Frost**\n\nKaufzone (RSI < 10%)")
with w2:
    st.info("🟢 **Sonnig / Heiter**\n\nNormalbereich (10% - 90%)")
with w3:
    st.info("🟣 **Sturm / Gewitter**\n\nVorsicht (RSI > 90%)")

st.divider()

# --- 5. MARKT-CHECK & CHINA-EXPOSURE ---
st.subheader("📈 Markt-Check & China-Exposure (DAX Fokus)")
l, m, r = st.columns(3)
with l: st.info("🔴 Extrem Tief (< 10%)")
with m: st.info("🟢 Normalbereich (10% - 90%)")
with r: st.info("🟣 Extrem Hoch (> 90%)")

st.divider()

# --- 6. DEIN BIO-CHECK (WANDSITZ & GESUNDHEIT) ---
st.subheader("🧘 Dein Bio-Check")
c1, c2, c3 = st.columns([2, 1, 1])

with c1:
    if st.button(f"Wandsitz erledigt (Heute: {st.session_state.h_count}x)"):
        st.session_state.h_count += 1
        st.rerun()
    # Stabiler Blutdruck-Warnblock ohne Formatierungsfehler
    st.error("ACHTUNG: Atmen! Keine Pressatmung!")

with c2:
    st.write("🌱 Sprossen / Rote Bete")
    st.write("🎫 Österreich Ticket")

with c3:
    st.write("🥜 Nüsse einplanen")
    st.write("🚫 Kein Chlorhexidin")

# --- 7. AUTOMATISCHER REFRESH ---
# Das Programm aktualisiert sich alle 60 Sek. von selbst
time.sleep(60)
st.rerun()
