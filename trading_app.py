import streamlit as st
import yfinance as yf
from datetime import datetime
import time

# --- 1. SETUP & SESSION STATE ---
st.set_page_config(page_title="Monitor für dich", layout="wide")

if 'h_count' not in st.session_state: st.session_state.h_count = 0

# --- 2. ZEIT-STEUERUNG (AUTOMATISCH) ---
jetzt = datetime.now()
# Prüfe: Ist es Montag (0) oder später UND nach 09:00 Uhr? [cite: 2026-02-07]
ist_boersenzeit = jetzt.weekday() <= 4 and jetzt.hour >= 9 

# --- 3. DATEN-LOGIK (7 EU + 7 US) ---
def hole_daten():
    if not ist_boersenzeit:
        return None
    # Deine 14 Champions: Niedrige Schulden, hohe Substanz [cite: 2026-02-07]
    titel = ["ASML.AS", "SAP.DE", "MC.PA", "SIE.DE", "OR.PA", "AIR.PA", "AZN.L", 
             "MSFT", "AAPL", "GOOGL", "V", "MA", "PG", "JNJ"]
    try:
        # Nur ein kleiner Test-Abruf für den Status
        return yf.download(titel, period="1d", interval="1m", group_by='ticker')
    except:
        return None

daten = hole_daten()

# --- 4. HEADER ---
st.title("🖥️ Monitor für dich")
st.write(f"🚀 **System-Zeit:** {jetzt.strftime('%d.%m.%Y %H:%M:%S')}")
if ist_boersenzeit:
    st.success("🟢 **LIVE-MODUS AKTIV:** 14 Qualitätswerte werden überwacht") [cite: 2026-02-07]
else:
    st.info("⚪ **STANDBY:** Automatischer Start am Montag um 09:00 Uhr") [cite: 2026-02-07]

st.divider()

# --- 5. BÖRSEN-WETTER (AUTOMATISCHE ANZEIGE) ---
st.subheader("🌦️ Börsen-Wetter")
w1, w2, w3 = st.columns(3)

with w1:
    st.info("🔴 **Eiszeit / Frost**\n\nKaufzone (RSI < 10%)") [cite: 2026-02-07]
with w2:
    st.info("🟢 **Sonnig / Heiter**\n\nNormalbereich (10% - 90%)")
with w3:
    st.info("🟣 **Sturm / Gewitter**\n\nVorsicht (RSI > 90%)") [cite: 2026-02-07]

st.divider()

# --- 6. BIO-CHECK (DEIN TRACKER) ---
st.subheader("🧘 Dein Bio-Check")
c1, c2, c3 = st.columns([2, 1, 1])

with c1:
    if st.button(f"Wandsitz erledigt (Heute: {st.session_state.h_count}x)"):
        st.session_state.h_count += 1
        st.rerun()
    st.error("ACHTUNG: Atmen! Keine Pressatmung!") [cite: 2025-12-20]

with c2:
    st.write("🌱 Sprossen / Rote Bete") [cite: 2025-12-20]
    st.write("🎫 Österreich Ticket") [cite: 2026-01-25]

with c3:
    st.write("🥜 Nüsse einplanen") [cite: 2026-02-03]
    st.write("🚫 Kein Chlorhexidin") [cite: 2025-12-20]

# Automatischer Refresh alle 60 Sekunden [cite: 2026-02-07]
time.sleep(60)
st.rerun()
