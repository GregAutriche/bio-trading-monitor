import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, time as dt_time
import time

# --- 1. SETUP ---
st.set_page_config(page_title="Monitor für dich", layout="wide")

if 'h_count' not in st.session_state: 
    st.session_state.h_count = 0

# --- 2. DIE ZEIT-PRÜFUNG (DER TÜRSTEHER) ---
jetzt = datetime.now()
# 0=Mo, 4=Fr, 5=Sa, 6=So
ist_werktag = jetzt.weekday() <= 4
ist_nach_neun = jetzt.time() >= dt_time(9, 0)

# Nur wenn Montag-Freitag UND nach 9 Uhr, wird 'live_aktiv' True
live_aktiv = ist_werktag and ist_nach_neun

# --- 3. HEADER ---
h_links, h_mitte, h_rechts = st.columns([1, 2, 1])
with h_mitte:
    st.markdown("<h1 style='text-align: center;'>🖥️ Ansicht für Dich</h1>", unsafe_allow_html=True)

with h_rechts:
    st.write(f"🚀 Start: {jetzt.strftime('%d.%m.%Y %H:%M:%S')}")
    # HIER merkst du die neue Version:
    status_msg = "Live-Analyse aktiv" if live_aktiv else "Warten auf Montag 09:00"
    st.info(f"🕒 STATUS: {status_msg}")

st.divider()

# --- 4. MARKT-CHECK ---
st.subheader("📈 Markt-Check: Euro/USD | DAX | Nasdaq")
m1, m2, m3 = st.columns(3)

val_eurusd, val_dax, val_nasdaq = None, None, None

# Markt-Daten nur holen, wenn live_aktiv ist
if live_aktiv:
    try:
        data = yf.download(["EURUSD=X", "^GDAXI", "^IXIC"], period="1d", interval="1m", progress=False)
        if not data.empty:
            val_eurusd = data['Close']['EURUSD=X'].iloc[-1] if 'EURUSD=X' in data['Close'] else None
            val_dax = data['Close']['^GDAXI'].iloc[-1] if '^GDAXI' in data['Close'] else None
            val_nasdaq = data['Close']['^IXIC'].iloc[-1] if '^IXIC' in data['Close'] else None
    except: pass

def display_metric(label, val, is_index=False):
    if val is None or pd.isna(val):
        st.write(f"**{label}**")
        st.markdown(f"<span style='color:red; font-weight:bold;'>[No Data]</span>", unsafe_allow_html=True)
    else:
        fmt = f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if is_index else f"{val:.4f}"
        st.metric(label, fmt)

with m1: display_metric("Euro/USD", val_eurusd)
with m2: display_metric("DAX", val_dax, is_index=True)
with m3: display_metric("Nasdaq", val_nasdaq, is_index=True)

st.divider()

# --- 5. BÖRSEN-WETTER (DIE DEFAULT ANZEIGE) ---
st.subheader("🌦️ Börsen-Wetter (RSI Analyse)")

meine_ticker = [
    "OTP.BU", "MOL.BU", "RICHT.BU", "ADS.DE", "SAP.DE", "BAS.DE", 
    "ALV.DE", "BMW.DE", "DTE.DE", "IFX.DE", "VOW3.DE", "A4L.SO", "IBG.SO", "AAPL"
]

w1, w2, w3 = st.columns(3)

# WENN NICHT MONTAG 9 UHR -> SOFORT DEFAULT
if not live_aktiv:
    with w1:
        st.info("🔴 Extrem Tief (RSI < 10%)")
        st.markdown("<span style='color:red;'>[No Data]</span>", unsafe_allow_html=True)
    with w2:
        st.success("🟢 Normalbereich (10% - 90%)")
        # HIER merkst du die neue Version: Alle Ticker stehen auf Standby
        for t in meine_ticker:
            st.write(f"{t}: Standby")
    with w3:
        st.warning("🟣 Extrem Hoch (RSI > 90%)")
        st.markdown("<span style='color:red;'>[No Data]</span>", unsafe_allow_html=True)
else:
    # Dieser Teil wird heute (Sonntag) komplett ignoriert und nicht ausgeführt
    st.write("Live-Modus: Berechne RSI...")

st.divider()

# --- 6. BIO-CHECK (Fakten & Infos) ---
st.subheader("🧘 Dein Bio-Check")
b1, b2 = st.columns(2)

with b1:
    if st.button(f"Wandsitz erledigt (Heute: {st.session_state.h_count}x)"):
        st.session_state.h_count += 1
        st.rerun()
    st.error("WANDSITZ-INFO: Atmen! Keine Pressatmung halten!")

with b2:
    with st.expander("✈️ Reisen & Backup-Infos"):
        st.write("🥜 Nüsse für Reisen einplanen")
        st.write("🌱 Sprossen / Rote Bete für Blutdruck")
        st.write("⚠️ Keine Mundspülung / Keine Phosphate")

time.sleep(60)
st.rerun()
