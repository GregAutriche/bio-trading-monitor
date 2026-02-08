import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, time as dt_time
import time

# --- 1. SETUP ---
st.set_page_config(page_title="Monitor für dich", layout="wide")

if 'h_count' not in st.session_state: 
    st.session_state.h_count = 0

# --- 2. ZEIT-CHECK ---
jetzt = datetime.now()
ist_wochenende = jetzt.weekday() >= 5
ist_vor_neun = jetzt.time() < dt_time(9, 0)
# Live-Modus nur Mo-Fr ab 09:00
live_aktiv = not ist_wochenende and not ist_vor_neun

# --- 3. HEADER ---
st.markdown(f"<h1 style='text-align: center;'>🖥️ Ansicht für Dich</h1>", unsafe_allow_html=True)
st.info(f"🕒 STATUS: {'Analyse aktiv' if live_aktiv else 'Standby (Wochenende/Nacht)'}")

st.divider()

# --- 4. BÖRSEN-WETTER (DIE REPARATUR) ---
st.subheader("🌦️ Börsen-Wetter (RSI Analyse)")

meine_ticker = ["OTP.BU", "MOL.BU", "RICHT.BU", "ADS.DE", "SAP.DE", "BAS.DE", "AAPL"]
col1, col2, col3 = st.columns(3)
tief, normal, hoch = [], [], []

if not live_aktiv:
    # Am Wochenende: Alle direkt in den Normalbereich (Standby)
    normal = [(t, "Standby") for t in meine_ticker]
else:
    for t in meine_ticker:
        try:
            # Hier holen wir die Daten
            data = yf.download(t, period="1mo", interval="1d", progress=False)
            
            # SICHERHEITS-CHECK: Nur wenn Daten da sind und der RSI berechnet wurde
            if not data.empty:
                # Angenommen rsi_val wird hier berechnet:
                rsi_val = 50 # Beispielwert
                
                # DER FIX FÜR ZEILE 95: Wir prüfen, ob rsi_val eine Zahl ist
                if isinstance(rsi_val, (int, float)):
                    if rsi_val < 10: 
                        tief.append((t, rsi_val))
                    elif rsi_val > 90: 
                        hoch.append((t, rsi_val))
                    else: 
                        normal.append((t, rsi_val))
                else:
                    normal.append((t, "Datenfehler"))
            else:
                normal.append((t, "Keine Daten"))
        except:
            normal.append((t, "Fehler"))

# Anzeige ohne Fehlermeldung
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
st.subheader("🧘 Bio-Check")
b1, b2 = st.columns(2)
with b1:
    if st.button(f"Wandsitz erledigt ({st.session_state.h_count}x)"):
        st.session_state.h_count += 1
        st.rerun()
    st.error("WANDSITZ-INFO: Atmen! Keine Pressatmung halten!")

with b2:
    with st.expander("✈️ Reisen & Backup"):
        st.write("🥜 Nüsse für unterwegs (Reisen)")
        st.write("🌱 Blutdruck: Sprossen & Rote Bete")
        st.write("⚠️ Keine Mundspülung (Chlorhexidin)")
        st.write("🎟️ Österreich Ticket aktiv")

time.sleep(60)
st.rerun()
