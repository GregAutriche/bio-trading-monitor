import streamlit as st
from datetime import datetime
# 1. Zeitdaten ermitteln
jetzt = datetime.now()
tage = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
wochentag = tage[jetzt.weekday()]

# 2. Die von dir gewünschte Zeile beim Start schreiben
# Format: Start: Wochentag, Jahr Monat Tag Uhrzeit
st.markdown(f"### Start: {wochentag}, {jetzt.strftime('%Y %m %d %H:%M:%S')}")


import streamlit as st
from datetime import datetime
import yfinance as yf
import time

# 2. Die von dir gewünschte Zeile beim Start schreiben
# Format: Start: Wochentag, Jahr Monat Tag Uhrzeit
st.markdown(f"### Start: {wochentag}, {jetzt.strftime('%Y %m %d %H:%M:%S')}")

st.divider()

# --- SETUP ---
st.set_page_config(page_title="Monitor", layout="wide")

# --- 1. WOCHENTAG-CHECK (DAS ERGEBNIS) ---
jetzt = datetime.now()
tage = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
heute_name = tage[jetzt.weekday()]
ist_wochenende = jetzt.weekday() >= 5

# Diese Zeile schreibt den Tag FETT nach ganz oben
st.markdown(f"# Heute ist {heute_name}")
st.write(f"Datum: {jetzt.strftime('%d.%m.%Y')}")

if ist_wochenende:
    st.warning("🕒 STATUS: Wochenende - Börsenanalyse pausiert.")
else:
    st.success("🕒 STATUS: Live-Analyse aktiv.")

st.divider()

# --- 2. DIE FEHLER-SPERRE ---
if ist_wochenende:
    st.info("Sonntags-Modus: Keine Kursdaten-Abfrage, um Fehler zu vermeiden.")
    st.write("Morgen ab 09:00 Uhr geht es hier automatisch weiter.")
else:
    # Nur hier darf der Code für die Kurse stehen
    st.write("Kursanalyse läuft...")

st.divider()

# --- 3. DEIN BIO-CHECK (WIE VEREINBART) ---
st.subheader("🧘 Bio-Check & Sicherheit")
c1, c2 = st.columns(2)
with c1:
    st.error("⚠️ WANDSITZ: Atmen! Keine Pressatmung halten! [cite: 2025-12-20]")
    st.write("🌱 Blutdruck: Sprossen & Rote Bete nutzen [cite: 2025-12-20]")
with c2:
    with st.expander("🛡️ Backup-Infos"):
        st.write("🎟️ Österreich Ticket aktiv [cite: 2026-01-25]")
        st.write("🥜 Snack: Nüsse für Reisen [cite: 2026-02-03]")
        st.write("⚠️ Keine Mundspülung (Chlorhexidin) [cite: 2025-12-20]")

time.sleep(60)
st.rerun()




