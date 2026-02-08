import streamlit as st
import yfinance as yf
from datetime import datetime

# --- 1. START-ZEILE ---
jetzt = datetime.now()
tage = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
heute_name = tage[jetzt.weekday()]

# Anzeige: Start: Wochentag, Jahr Monat Tag Uhrzeit
st.markdown(f"## Start: {heute_name}, {jetzt.strftime('%Y %m %d %H:%M:%S')}")
st.divider()

# --- 2. MARKT-CHECK ---
st.subheader("💹 Markt-Check: Euro/USD | DAX | Nasdaq")

def get_data(symbol):
    try:
        t = yf.Ticker(symbol)
        d = t.history(period="1d")
        return round(d['Close'].iloc[-1], 4) if not d.empty else "N/A"
    except: return "Error"

m1, m2, m3 = st.columns(3)
with m1: st.metric("Euro/USD", get_data("EURUSD=X"))
with m2: st.metric("DAX", get_data("^GDAXI"))
with m3: st.metric("Nasdaq", get_data("^IXIC"))

st.divider()

# --- 3. DIE 14 AKTIEN (7x EUROPA & 7x USA) ---
st.subheader("🇪🇺 7x Europa & 🇺🇸 7x USA")

europa = ["OTP.BU", "MOL.BU", "ADS.DE", "SAP.DE", "ASML.AS", "MC.PA", "SIE.DE"]
usa = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA"]

c_eu, c_us = st.columns(2)
with c_eu:
    for t in europa: st.write(f"🇪🇺 {t}: {get_data(t)}")
with c_us:
    for t in usa: st.write(f"🇺🇸 {t}: {get_data(t)}")

st.divider()

# --- 4. BIO-CHECK & BACKUP ---
st.subheader("🧘 Bio-Check & Sicherheit")
st.error("⚠️ WANDSITZ: Atmen! Pressatmung vermeiden!")

with st.expander("🛡️ Backup-Informationen"):
    st.write("🌱 **Blutdruck**: Sprossen & Rote Bete nutzen [cite: 2025-12-20]")
    st.write("🥜 **Reisen**: Nüsse als Snack & Österreich Ticket [cite: 2026-02-03, 2026-01-25]")
    st.write("🚫 **Warnung**: Keine Mundspülung (Chlorhexidin) [cite: 2025-12-20]")
