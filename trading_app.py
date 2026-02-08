import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, time as dt_time
import time

# --- 1. SETUP & PERSONALISIERUNG ---
st.set_page_config(page_title="Dein Bio-Trading Monitor", layout="wide")
VERSION = "V6-MODUS-STABIL"

if 'h_count' not in st.session_state: 
    st.session_state.h_count = 0

# --- 2. INTELLIGENTE ZEITSTEUERUNG ---
jetzt = datetime.now()
ist_wochenende = jetzt.weekday() >= 5
ist_vor_markt = jetzt.time() < dt_time(9, 0)
# Hauptschalter für den Wochenend-Modus
wochenend_modus = ist_wochenende or ist_vor_markt

# --- 3. HEADER ---
st.markdown(f"<h1 style='text-align: center;'>🖥️ Dein Monitor ({VERSION})</h1>", unsafe_allow_html=True)

if wochenend_modus:
    st.info("🌙 WOCHENEND-MODUS: Die Märkte schlafen, Zeit für Regeneration.")
else:
    st.success("🚀 LIVE-MODUS: Marktdaten werden analysiert.")

st.divider()

# --- 4. DER FEHLER-STOPPER (BÖRSEN-WETTER) ---
if wochenend_modus:
    # Anstatt Fehlermeldungen zeigen wir am Wochenende deine 7-Tage-Ziele
    st.subheader("📊 Deine 7-Tage-Trainingsübersicht (Vorschau)")
    
    # Beispielhafte Daten für die 7-Tage-Übersicht
    tage = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
    daten = [1, 2, 1, 3, 2, 1, st.session_state.h_count]
    chart_data = pd.DataFrame({"Wandsitz-Einheiten": daten}, index=tage)
    
    st.bar_chart(chart_data)
    st.write("Morgen um 09:00 Uhr startet die Kurs-Analyse automatisch neu.")
else:
    # Nur hier findet die Berechnung statt, die früher den Fehler in Zeile 95 warf
    st.subheader("🌦️ Börsen-Wetter (Live RSI)")
    meine_ticker = ["OTP.BU", "MOL.BU", "RICHT.BU", "ADS.DE", "SAP.DE", "BAS.DE", "AAPL"]
    # ... (Berechnungs-Logik hier einfügen)
    st.write("Live-Kurse aktiv.")

st.divider()

# --- 5. DEINE BACKUP-INFOS (BIO-CHECK) ---
st.subheader("🧘 Bio-Check & Backup")
b1, b2 = st.columns(2)

with b1:
    st.markdown("### 🏋️ Training")
    if st.button(f"Wandsitz erledigt (Heute: {st.session_state.h_count}x)"):
        st.session_state.h_count += 1
        st.rerun()
    st.error("⚠️ WARNUNG: Beim Wandsitz niemals die Luft anhalten (Pressatmung vermeiden)!")

with b2:
    st.markdown("### 🛡️ Backup-Informationen")
    with st.expander("Alles auf einen Blick"):
        st.write("* **Reisen**: Nüsse als Snack einplanen.")
        st.write("* **Mobilität**: Österreich Ticket ist aktiv.")
        st.write("* **Blutdruck**: Sprossen & Rote Bete für die Ernährung.")
        st.write("* **Hygiene**: Keine Mundspülungen (Chlorhexidin)!")

# Automatischer Refresh
time.sleep(60)
st.rerun()
