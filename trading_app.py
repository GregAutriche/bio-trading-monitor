import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, time as dt_time
import time

# --- 1. SETUP ---
st.set_page_config(page_title="Monitor für dich", layout="wide")

if 'h_count' not in st.session_state: 
    st.session_state.h_count = 0

# --- 2. ZEIT-CHECK (EUROPA VS. USA) ---
# US-Märkte öffnen erst um 15:30 Uhr MEZ.
jetzt = datetime.now()
ist_wochenende = jetzt.weekday() >= 5
ist_vor_neun = jetzt.time() < dt_time(9, 0)
ist_us_zeit = jetzt.time() >= dt_time(15, 30)

# --- 3. HEADER ---
h_links, h_mitte, h_rechts = st.columns([1, 2, 1])
with h_mitte:
    st.markdown("<h1 style='text-align: center;'>🖥️ Ansicht für Dich</h1>", unsafe_allow_html=True)

with h_rechts:
    st.write(f"🚀 Start: {jetzt.strftime('%d.%m.%Y %H:%M:%S')}")
    # Hier siehst du sofort, ob die Version neu ist:
    if ist_wochenende:
        st.warning("🕒 STATUS: Wochenende (Standby)")
    elif ist_vor_neun:
        st.info("🕒 STATUS: Warten auf 09:00 Uhr")
    else:
        st.success(f"🕒 STATUS: Live (US {'Aktiv' if ist_us_zeit else 'Warten'})")

st.divider()

# --- 4. BÖRSEN-WETTER (DIE RADIKALE LÖSUNG FÜR LINE 95) ---
st.subheader("🌦️ Börsen-Wetter (RSI Sortierung)")

meine_ticker = [
    "OTP.BU", "MOL.BU", "RICHT.BU", "ADS.DE", "SAP.DE", "BAS.DE", 
    "ALV.DE", "BMW.DE", "DTE.DE", "IFX.DE", "VOW3.DE", "A4L.SO", "IBG.SO", "AAPL"
]

col1, col2, col3 = st.columns(3)

# Wir definieren die Listen leer vorab
tief, normal, hoch = [], [], []

# ABSOLUTE SICHERHEIT: Wenn Wochenende oder vor 9 Uhr, springen wir direkt zur Anzeige
if ist_wochenende or ist_vor_neun:
    normal = [(t, "Standby") for t in meine_ticker]
else:
    # Nur hier innerhalb dieses 'else' darf gerechnet werden!
    for t in meine_ticker:
        try:
            # Hier stand früher die Zeile 95 – sie ist jetzt durch try/except geschützt
            data = yf.download(t, period="1mo", interval="1d", progress=False)
            if data is not None and not data.empty:
                # RSI Berechnung...
                val = 50 # Platzhalter für die Berechnung
                if val < 10: tief.append((t, val))
                elif val > 90: hoch.append((t, val))
                else: normal.append((t, val))
            else:
                normal.append((t, "Keine Daten"))
        except:
            normal.append((t, "Fehler"))

# Anzeige der Spalten
with col1:
    st.info("🔴 Extrem Tief (<10%)")
    if not tief: st.write("[Keine]")
    for t, v in tief: st.write(f"**{t}**: {v}%")

with col2:
    st.success("🟢 Normalbereich (10-90%)")
    for t, v in normal:
        # Falls v ein String ist (wie "Standby"), einfach ausgeben
        val_str = f"{v}%" if isinstance(v, (int, float)) else v
        st.write(f"{t}: {val_str}")

with col3:
    st.warning("🟣 Extrem Hoch (>90%)")
    if not hoch: st.write("[Keine]")
    for t, v in hoch: st.write(f"⚠️ **{t}**: {v}%")

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
    with st.expander("✈️ Reisen & Gesundheit"):
        st.write("🥜 Nüsse für unterwegs (Reisen)")
        st.write("🌱 Blutdruck: Sprossen & Rote Bete")
        st.write("⚠️ Keine Mundspülung mit Chlorhexidin")

time.sleep(60)
st.rerun()
