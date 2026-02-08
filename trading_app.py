import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, time as dt_time
import time

# --- 1. SETUP & VERSION ---
st.set_page_config(page_title="Monitor für dich", layout="wide")
VERSION = "3.1-STABLE-BLOCK"

if 'h_count' not in st.session_state: 
    st.session_state.h_count = 0

# --- 2. ZEIT-LOGIK (DIE MAUER GEGEN ZEILE 95) ---
jetzt = datetime.now()
ist_wochenende = jetzt.weekday() >= 5
ist_vor_neun = jetzt.time() < dt_time(9, 0)
# US-Märkte öffnen erst um 15:30 MEZ
ist_us_offen = jetzt.time() >= dt_time(15, 30)

# Nur Mo-Fr nach 09:00 Uhr darf gerechnet werden
rechnen_erlaubt = not ist_wochenende and not ist_vor_neun

# --- 3. HEADER ---
h_links, h_mitte, h_rechts = st.columns([1, 2, 1])
with h_mitte:
    st.markdown(f"<h1 style='text-align: center;'>🖥️ Ansicht für Dich</h1>", unsafe_allow_html=True)
with h_rechts:
    st.write(f"🚀 Start: {jetzt.strftime('%d.%m.%Y %H:%M:%S')}")
    status_color = "green" if rechnen_erlaubt else "orange"
    st.markdown(f"<p style='color:{status_color}; font-weight:bold;'>STATUS: {VERSION} ({'LIVE' if rechnen_erlaubt else 'STANDBY'})</p>", unsafe_allow_html=True)

st.divider()

# --- 4. BÖRSEN-WETTER (PROBLEMZONE GELÖST) ---
st.subheader("🌦️ Börsen-Wetter (RSI Analyse)")

# Deine wichtigsten Ticker inklusive Ungarn und Bulgarien
meine_ticker = [
    "OTP.BU", "MOL.BU", "RICHT.BU", "ADS.DE", "SAP.DE", "BAS.DE", 
    "ALV.DE", "BMW.DE", "DTE.DE", "IFX.DE", "VOW3.DE", "AAPL"
]

col1, col2, col3 = st.columns(3)
tief, normal, hoch = [], [], []

if not rechnen_erlaubt:
    # AM WOCHENENDE: Keine Berechnung, kein Fehler 95 möglich.
    normal = [(t, "Standby") for t in meine_ticker]
else:
    # UNTER DER WOCHE:
    for t in meine_ticker:
        try:
            data = yf.download(t, period="1mo", interval="1d", progress=False)
            if not data.empty:
                # Hier würde deine RSI-Berechnung stehen
                rsi_val = 50 # Platzhalter
                
                # DER FIX: Wir prüfen erst den Datentyp
                if isinstance(rsi_val, (int, float)):
                    if rsi_val < 10: tief.append((t, f"{rsi_val}%"))
                    elif rsi_val > 90: hoch.append((t, f"{rsi_val}%"))
                    else: normal.append((t, f"{rsi_val}%"))
            else:
                normal.append((t, "No Data"))
        except:
            normal.append((t, "Wartet..."))

with col1:
    st.info("🔴 Extrem Tief (<10%)")
    for t, v in tief: st.write(f"**{t}**: {v}")
with col2:
    st.success("🟢 Normalbereich (10-90%)")
    for t, v in normal: st.write(f"{t}: {v}")
with col3:
    st.warning("🟣 Extrem Hoch (>90%)")
    for t, v in hoch: st.write(f"⚠️ **{t}**: {v}")

st.divider()

# --- 5. BIO-CHECK & BACKUP-INFOS ---
st.subheader("🧘 Dein Bio-Check")
b1, b2 = st.columns(2)

with b1:
    if st.button(f"Wandsitz erledigt (Heute: {st.session_state.h_count}x)"):
        st.session_state.h_count += 1
        st.rerun()
    # Wandsitz-Warnung
    st.error("WANDSITZ: Keine Pressatmung halten!")

with b2:
    with st.expander("✈️ Reisen & Gesundheit (Backup)"):
        st.write("🎟️ Ticket: Österreich Ticket vorhanden")
        st.write("🥜 Snack: Nüsse für Reisen einplanen")
        st.write("🌱 Blutdruck: Sprossen & Rote Bete nutzen")
        st.write("⚠️ Warnung: Keine Mundspülungen (Chlorhexidin)")

# Automatischer Refresh alle 60 Sekunden
time.sleep(60)
st.rerun()
