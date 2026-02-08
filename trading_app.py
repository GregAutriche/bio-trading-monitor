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

# --- 2. MARKT-CHECK (EURO/USD, DAX, NASDAQ) ---
st.subheader("💹 Markt-Check")

def get_price(symbol):
    try:
        ticker = yf.Ticker(symbol)
        # Wir holen den letzten verfügbaren Schlusskurs (auch am Wochenende)
        data = ticker.history(period="1d")
        if not data.empty:
            return round(data['Close'].iloc[-1], 4)
        return "Keine Daten"
    except:
        return "Fehler"

c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Euro/USD", get_price("EURUSD=X"))
with c2:
    st.metric("DAX", get_price("^GDAXI"))
with c3:
    st.metric("Nasdaq", get_price("^IXIC"))

st.divider()

# --- 3. BIO-CHECK (DEINE SICHERHEIT) ---
st.subheader("🧘 Bio-Check & Backup")
# Hier fügen wir deine wichtigen Erinnerungen ein
st.error("⚠️ WANDSITZ: Atmen! Pressatmung vermeiden (Blutdruckschutz)! [cite: 2025-12-20]")
with st.expander("🛡️ Deine gespeicherten Infos"):
    st.write("🌱 **Ernährung**: Sprossen & Rote Bete [cite: 2025-12-20]")
    st.write("🥜 **Reisen**: Nüsse als Snack & Österreich Ticket [cite: 2026-02-03, 2026-01-25]")
    st.write("🚫 **Warnung**: Keine Chlorhexidin-Mundspülungen [cite: 2025-12-20]")
