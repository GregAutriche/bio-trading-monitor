import streamlit as st
import yfinance as yf
from datetime import datetime

# --- 1. SETUP ---
st.set_page_config(page_title="Monitor für dich", layout="wide")

if 'start_zeit' not in st.session_state:
    st.session_state.start_zeit = datetime.now().strftime('%d.%m.%Y %H:%M:%S')

# --- 2. AUTOMATISCHER DATEN-CHECK ---
def hole_wetter_daten():
    # Hier würde morgen der Abruf für DAX/RSI stehen [cite: 2026-02-07]
    # Wenn Markt geschlossen (Sonntag), geben wir None zurück
    return None 

wetter_status = hole_wetter_daten()

# --- 3. HEADER ---
st.title("🖥️ Monitor für dich")
st.write(f"🚀 **Programm gestartet am:** {st.session_state.start_zeit}")
st.write(f"🕒 **Status:** {'🟢 LIVE' if wetter_status else '⚪ STANDBY (Wochenende)'}")

st.divider()

# --- 4. BÖRSEN-WETTER (Mit sonnig/stürmisch Logik) ---
st.subheader("🌦️ Börsen-Wetter (ATR & RSI)")
w1, w2, w3 = st.columns(3)

with w1:
    # Frost-Logik bei < 10% [cite: 2026-02-07]
    st.info("🔴 **Eiszeit / Frost**\n\nExtrem Tief (< 10%)")
with w2:
    # Sonnig-Logik im Normalbereich [cite: 2026-02-07]
    st.info("🟢 **Sonnig / Heiter**\n\nNormalbereich (10% - 90%)")
with w3:
    # Sturm-Logik bei > 90% [cite: 2026-02-07]
    st.info("🟣 **Sturm / Gewitter**\n\nExtrem Hoch (> 90%)")

st.divider()

# --- 5. BIO-CHECK LEISTE (AUFGERÄUMT) ---
# Wandsitz-Tracker und Gesundheit ohne störende Quellen im Text [cite: 2026-02-07]
st.subheader("🧘 Dein Bio-Check")
c1, c2, c3 = st.columns([2, 1, 1])

with c1:
    if st.button(f"Wandsitz erledigt (Heute: {st.session_state.get('h_count', 0)}x)"):
        # Logik für Training [cite: 2026-02-03]
        pass
    st.error("⚠️ **Atmen! Keine Preßatmung!**", help="Wichtig zur Blutdruck-Vermeidung [cite: 2025-12-20]")

with c2:
    st.write("🌱 Sprossen / Rote Bete", help="Blutdrucksenkende Ernährung [cite: 2025-12-20]")
    st.write("🎫 Österreich Ticket", help="Gültig für alle Öffis [cite: 2026-01-25]")

with c3:
    st.write("🥜 Nüsse einplanen", help="Gesunde Fette für unterwegs [cite: 2026-02-03]")
    st.write("🚫 Kein Chlorhexidin", help="Vermeide Mundspülungen mit diesem Stoff [cite: 2025-12-20]")
