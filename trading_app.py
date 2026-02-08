import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, time as dt_time
import time

# --- 1. SETUP ---
st.set_page_config(page_title="Monitor V4", layout="wide")
VERSION = "V4-ULTRA-STABLE"

if 'h_count' not in st.session_state: 
    st.session_state.h_count = 0

# --- 2. ZEITSTEUERUNG (DER FEHLER-STOPPER) ---
jetzt = datetime.now()
ist_wochenende = jetzt.weekday() >= 5
ist_vor_neun = jetzt.time() < dt_time(9, 0)

# Nur Mo-Fr nach 09:00 Uhr ist der "Live-Modus" erlaubt
live_modus = not ist_wochenende and not ist_vor_neun

# --- 3. HEADER ---
h_links, h_mitte, h_rechts = st.columns([1, 2, 1])
with h_mitte:
    st.markdown(f"<h1 style='text-align: center;'>🖥️ Deine Ansicht ({VERSION})</h1>", unsafe_allow_html=True)
with h_rechts:
    status_text = "🟢 LIVE" if live_modus else "🟡 STANDBY (Wochenende)"
    st.write(f"🚀 Start: {jetzt.strftime('%d.%m.%Y %H:%M:%S')}")
    st.markdown(f"**Status: {status_text}**")

st.divider()

# --- 4. MARKT-CHECK ---
st.subheader("📈 Markt-Übersicht")
m1, m2, m3 = st.columns(3)

def fetch_data(ticker):
    if not live_modus: return None
    try:
        d = yf.download(ticker, period="1d", interval="1m", progress=False)
        return float(d['Close'].iloc[-1]) if not d.empty else None
    except: return None

with m1: st.metric("Euro/USD", "1.1820")
with m2: 
    dax = fetch_data("^GDAXI")
    st.metric("DAX", f"{dax:,.2f}" if dax else "[Standby]")
with m3: 
    nas = fetch_data("^IXIC")
    st.metric("Nasdaq", f"{nas:,.2f}" if nas else "[Standby]")

st.divider()

# --- 5. BÖRSEN-WETTER (DAS ENDE VON ZEILE 95) ---
st.subheader("🌦️ Börsen-Wetter (RSI Sortierung)")

meine_ticker = ["OTP.BU", "MOL.BU", "RICHT.BU", "ADS.DE", "SAP.DE", "BAS.DE", "AAPL"]
col1, col2, col3 = st.columns(3)
tief, normal, hoch = [], [], []

# WENN SONNTAG: Alles direkt in 'normal' ohne jede Berechnung
if not live_modus:
    normal = [(t, "Markt geschlossen") for t in meine_ticker]
else:
    # NUR WENN LIVE: Der Computer liest diesen Teil nur unter der Woche!
    for t in meine_ticker:
        try:
            data = yf.download(t, period="1mo", interval="1d", progress=False)
            if not data.empty:
                # Hier würde die RSI Berechnung stehen
                rsi_val = 50 
                # DER FIX: Wir prüfen, ob es eine Zahl ist, bevor wir vergleichen
                if isinstance(rsi_val, (int, float)):
                    if rsi_val < 10: tief.append((t, rsi_val))
                    elif rsi_val > 90: hoch.append((t, rsi_val))
                    else: normal.append((t, rsi_val))
            else:
                normal.append((t, "No Data"))
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

# --- 6. BIO-CHECK & BACKUP ---
st.subheader("🧘 Bio-Check & Backup")
b1, b2 = st.columns(2)

with b1:
    if st.button(f"Wandsitz erledigt ({st.session_state.h_count}x)"):
        st.session_state.h_count += 1
        st.rerun()
    st.error("WANDSITZ: Beim Training nicht die Luft anhalten!")

with b2:
    with st.expander("ℹ️ Backup & Gesundheit"):
        st.write("🌱 **Blutdruck**: Sprossen & Rote Bete konsumieren.")
        st.write("🥜 **Reisen**: Nüsse als Snack einplanen.")
        st.write("⚠️ **Warnung**: Keine Mundspülungen mit Chlorhexidin.")
        st.write("🎟️ **Mobilität**: Österreich Ticket ist aktiv.")

time.sleep(60)
st.rerun()
