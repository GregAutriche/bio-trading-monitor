import streamlit as st
import yfinance as yf
from datetime import datetime

# --- 1. START-ZEILE (DEIN HAUPTWUNSCH) ---
jetzt = datetime.now()
tage = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
heute_name = tage[jetzt.weekday()]

# Format: Start: Wochentag, Jahr Monat Tag Uhrzeit
st.markdown(f"## Start: {heute_name}, {jetzt.strftime('%Y %m %d %H:%M:%S')}")
st.divider()

# --- 2. MARKT-ÜBERSICHT (INDEX-DATEN) ---
st.subheader("💹 Markt-Check: Euro/USD | DAX | Nasdaq")

def get_live_data(symbol):
    try:
        ticker = yf.Ticker(symbol)
        # Holt den letzten verfügbaren Kurs, um Abstürze am Wochenende zu vermeiden
        data = ticker.history(period="1d")
        if not data.empty:
            return round(data['Close'].iloc[-1], 2)
        return "N/A"
    except:
        return "Error"

m1, m2, m3 = st.columns(3)
with m1: st.metric("Euro/USD", get_live_data("EURUSD=X"))
with m2: st.metric("DAX", get_live_data("^GDAXI"))
with m3: st.metric("Nasdaq", get_live_data("^IXIC"))

st.divider()

# --- 3. DIE 14 AKTIEN (7x EUROPA inkl. HU/BG & 7x USA) ---
st.subheader("🇪🇺 7x Europa & 🇺🇸 7x USA")

# Europa Liste (Beispielhaft inklusive deiner ungarischen/bulgarischen Favoriten)
europa = ["OTP.BU", "MOL.BU", "ADS.DE", "SAP.DE", "ASML.AS", "MC.PA", "SIE.DE"] [cite: 2026-02-07]
usa = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA"]

col_eu, col_us = st.columns(2)

with col_eu:
    st.markdown("**Europa Portfolio**")
    for t in europa:
        st.write(f"{t}: {get_live_data(t)}")

with col_us:
    st.markdown("**USA Portfolio**")
    for t in usa:
        st.write(f"{t}: {get_live_data(t)}")

st.divider()

# --- 4. BIO-CHECK & BACKUP (ZUSAMMENFASSUNG) ---
st.subheader("🧘 Bio-Check & Sicherheit")
st.error("⚠️ WANDSITZ: Atmen! Pressatmung vermeiden (Blutdruckschutz)! [cite: 2025-12-20]")

with st.expander("🛡️ Deine gespeicherten Backup-Infos"):
    st.write("🌱 **Ernährung**: Sprossen & Rote Bete zur Blutdrucksenkung [cite: 2025-12-20]")
    st.write("🥜 **Reisen**: Nüsse als Snack & Österreich Ticket aktiv [cite: 2026-02-03, 2026-01-25]")
    st.write("🚫 **Hygiene**: Keine Mundspülungen mit Chlorhexidin [cite: 2025-12-20]")
