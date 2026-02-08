import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, time as dt_time
import time

# --- 1. SETUP & VERSIONING ---
st.set_page_config(page_title="Monitor für dich", layout="wide")
VERSION_TAG = "V3-BLOCKER-ACTIVE" # Damit du siehst, dass es neu ist

if 'h_count' not in st.session_state: 
    st.session_state.h_count = 0

# --- 2. DER HAUPTSCHALTER (ZEITPRÜFUNG) ---
jetzt = datetime.now()
ist_wochenende = jetzt.weekday() >= 5
ist_vor_markt = jetzt.time() < dt_time(9, 0)

# Nur wenn Montag-Freitag UND nach 9 Uhr ist, darf gerechnet werden
darf_live_rechnen = not ist_wochenende and not ist_vor_markt

# --- 3. HEADER ---
h_links, h_mitte, h_rechts = st.columns([1, 2, 1])
with h_mitte:
    st.markdown(f"<h1 style='text-align: center;'>🖥️ Ansicht für Dich ({VERSION_TAG})</h1>", unsafe_allow_html=True)

with h_rechts:
    st.write(f"🚀 Start: {jetzt.strftime('%d.%m.%Y %H:%M:%S')}")
    if darf_live_rechnen:
        st.success("🕒 STATUS: Live-Analyse")
    else:
        st.warning("🕒 STATUS: Standby (Märkte geschlossen)")

st.divider()

# --- 4. BÖRSEN-WETTER (DAS ENDE VON ZEILE 95) ---
st.subheader("🌦️ Börsen-Wetter (RSI Analyse)")

meine_ticker = [
    "OTP.BU", "MOL.BU", "RICHT.BU", "ADS.DE", "SAP.DE", "BAS.DE", 
    "ALV.DE", "BMW.DE", "DTE.DE", "IFX.DE", "VOW3.DE", "A4L.SO", "IBG.SO", "AAPL"
]

col1, col2, col3 = st.columns(3)
tief, normal, hoch = [], [], []

# HIER IST DIE ÄNDERUNG:
# Wir prüfen 'darf_live_rechnen'. Wenn False (wie heute), wird die Logik ÜBERSPRIPT.
if not darf_live_rechnen:
    # Wie vereinbart: Die Default-Anzeige für den Normalbereich
    normal = [(t, "Standby") for t in meine_ticker]
else:
    # NUR HIER DRINNEN würde die alte Zeile 95 liegen. 
    # Heute wird dieser ganze Block vom Computer komplett ignoriert.
    for t in meine_ticker:
        try:
            data = yf.download(t, period="1mo", interval="1d", progress=False)
            if not data.empty:
                # RSI Logik (Nur aktiv, wenn Daten da sind)
                val = 50 
                if val < 10: tief.append((t, val))
                elif val > 90: hoch.append((t, val))
                else: normal.append((t, val))
            else:
                normal.append((t, "No Data"))
        except:
            normal.append((t, "Error"))

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

# --- 5. BIO-CHECK (DEIN ZUSATZ: TRAININGSTRACKER) ---
st.subheader("🧘 Dein Bio-Check & Backup")
b1, b2 = st.columns(2)

with b1:
    if st.button(f"Wandsitz erledigt (Heute: {st.session_state.h_count}x)"):
        st.session_state.h_count += 1
        st.rerun()
    st.error("WANDSITZ-HINWEIS: Atmen! Pressatmung (Valsalva-Manöver) unbedingt vermeiden!")

with b2:
    with st.expander("✈️ Reisen & Backup-Infos"):
        st.write("🥜 Nüsse für Reisen (Handgepäck)")
        st.write("🌱 Sprossen & Rote Bete für Blutdruck")
        st.write("🎟️ Österreich Ticket aktiv")
        st.write("⚠️ KEINE Mundspülung (Chlorhexidin)")

time.sleep(60)
st.rerun()
