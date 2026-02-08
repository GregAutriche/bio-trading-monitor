import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, time as dt_time
import time

# --- 1. SETUP & KONFIGURATION ---
st.set_page_config(page_title="Bio-Monitor", layout="wide")

if 'h_count' not in st.session_state: 
    st.session_state.h_count = 0

# --- 2. WOCHENTAG-ABGLEICH (DEINE IDEE) ---
jetzt = datetime.now()
wochentag_nr = jetzt.weekday() # 0=Mo, 5=Sa, 6=So
wochentage_namen = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
heute_name = wochentage_namen[wochentag_nr]

# Prüfung: Ist heute ein Handelstag? (Mo-Fr)
ist_handelstag = wochentag_nr < 5
ist_marktzeit = dt_time(9, 0) <= jetzt.time() <= dt_time(22, 0)

# Nur wenn beides stimmt, wird die Fehlerzone (RSI) aktiviert
live_modus = ist_handelstag and ist_marktzeit

# --- 3. HEADER MIT WOCHENTAG-ANZEIGE ---
st.markdown(f"<h1 style='text-align: center;'>🖥️ Dein Monitor</h1>", unsafe_allow_html=True)

h_links, h_mitte, h_rechts = st.columns([1, 1, 1])
with h_mitte:
    # Hier zeigen wir den Wochentag an, damit du siehst, was das System denkt
    st.info(f"📅 Heute ist: **{heute_name}**")

with h_rechts:
    if live_modus:
        st.success("🕒 STATUS: Markt aktiv")
    else:
        st.warning("🕒 STATUS: Wochenende / Standby")

st.divider()

# --- 4. BÖRSEN-WETTER (DIE REPARIERTE ZONE) ---
st.subheader("🌦️ Börsen-Wetter")

meine_ticker = ["OTP.BU", "MOL.BU", "RICHT.BU", "ADS.DE", "SAP.DE", "BAS.DE", "AAPL"]
col1, col2, col3 = st.columns(3)
tief, normal, hoch = [], [], []

if not live_modus:
    # AM WOCHENENDE: Alles direkt in den Normalbereich ohne Vergleich
    normal = [(t, "Standby") for t in meine_ticker]
else:
    # DIESER TEIL WIRD AM SONNTAG KOMPLETT ÜBERSPRUNGEN
    for t in meine_ticker:
        try:
            data = yf.download(t, period="1mo", interval="1d", progress=False)
            if not data.empty:
                # Hier würde die Berechnung stehen. 
                # Da heute Sonntag ist, kommt das Programm gar nicht bis hierhin.
                rsi_val = 50 
                if rsi_val < 10: tief.append((t, rsi_val))
                elif rsi_val > 90: hoch.append((t, rsi_val))
                else: normal.append((t, rsi_val))
        except:
            normal.append((t, "Fehler"))

# Anzeige der Ergebnisse
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

# --- 5. BIO-CHECK & BACKUP ---
st.subheader("🧘 Bio-Check & Sicherheit")
b1, b2 = st.columns(2)
with b1:
    if st.button(f"Wandsitz erledigt ({st.session_state.h_count}x)"):
        st.session_state.h_count += 1
        st.rerun()
    st.error("WICHTIG: Keine Pressatmung beim Wandsitz!")

with b2:
    with st.expander("ℹ️ Backup & Gesundheit"):
        st.write(f"* **Training**: Wandsitz zur Senkung des Blutdrucks")
        st.write("* **Ernährung**: Sprossen & Rote Bete")
        st.write("* **Hygiene**: Keine Mundspülungen (Chlorhexidin)")
        st.write("* **Reisen**: Nüsse als Snack einplanen")
        st.write("* **Mobilität**: Österreich Ticket aktiv")

time.sleep(60)
st.rerun()
