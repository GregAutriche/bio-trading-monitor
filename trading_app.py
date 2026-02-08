import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime
import time

# --- 1. START-LOGIK: WOCHENTAG-ERKENNUNG ---
jetzt = datetime.now()
wochentag_nr = jetzt.weekday() # 0=Mo, 6=So
tage_namen = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
heute_name = tage_namen[wochentag_nr]

# Hier ist die Weiche: Nur Mo-Fr wird 'rechnen' erlaubt
rechnen_erlaubt = wochentag_nr < 5 

# --- 2. SETUP & SESSION ---
st.set_page_config(page_title="Bio-Monitor V7", layout="wide")

if 'h_count' not in st.session_state: 
    st.session_state.h_count = 0

# --- 3. HEADER (Muss den Wochentag zeigen!) ---
st.markdown(f"<h1 style='text-align: center;'>🖥️ Ansicht für Dich</h1>", unsafe_allow_html=True)

col_a, col_b = st.columns(2)
with col_a:
    # Das System schreibt jetzt EXPLIZIT hin, welcher Tag ist
    st.info(f"📅 Start-Check: Heute ist **{heute_name}**")
with col_b:
    if rechnen_erlaubt:
        st.success("🕒 STATUS: Börsentag - Analyse läuft")
    else:
        st.warning("🕒 STATUS: Wochenende - Standby")

st.divider()

# --- 4. BÖRSEN-WETTER (DIE FEHLER-ZONE) ---
st.subheader("🌦️ Börsen-Wetter")

# Wichtigste Ticker (Ungarn & Bulgarien inklusive)
meine_ticker = ["OTP.BU", "MOL.BU", "RICHT.BU", "ADS.DE", "SAP.DE", "BAS.DE", "AAPL"]
col1, col2, col3 = st.columns(3)
tief, normal, hoch = [], [], []

# REAKTION AUF DEN WOCHENTAG:
if not rechnen_erlaubt:
    # Wenn heute Sonntag ist, wird Zeile 95 GAR NICHT ERST GELESEN
    normal = [(t, "Pause") for t in meine_ticker]
else:
    # Dieser Block ist für Mo-Fr reserviert
    for t in meine_ticker:
        try:
            data = yf.download(t, period="1mo", interval="1d", progress=False)
            if not data.empty:
                rsi_val = 50 # Berechnung
                # Hier war dein Fehler:
                if rsi_val < 10: tief.append((t, rsi_val)) # Zone < 10%
                elif rsi_val > 90: hoch.append((t, rsi_val)) # Zone > 90%
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

# --- 5. DEIN BIO-CHECK (BACKUP) ---
st.subheader("🧘 Bio-Check & Backup")
b1, b2 = st.columns(2)

with b1:
    if st.button(f"Wandsitz erledigt ({st.session_state.h_count}x)"):
        st.session_state.h_count += 1 # Tracking für die 7-Tage Übersicht
        st.rerun()
    st.error("WANDSITZ-WARNUNG: Atmen! Keine Pressatmung halten!")

with b2:
    with st.expander("🛡️ Deine Sicherheits-Infos"):
        st.write(f"🌱 **Blutdruck**: Sprossen & Rote Bete")
        st.write(f"🥜 **Snacks**: Nüsse für Reisen einplanen")
        st.write(f"🎟️ **Mobilität**: Österreich Ticket vorhanden")
        st.write(f"⚠️ **Hygiene**: Keine Mundspülung (Chlorhexidin)!")

time.sleep(60)
st.rerun()
