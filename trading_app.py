import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime
import time

# --- SICHERHEITS-CHECK START ---
jetzt = datetime.now()
tage = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
heute_name = tage[jetzt.weekday()]
ist_wochenende = jetzt.weekday() >= 5

# DAS HIER ERZWINGT DIE ANZEIGE
st.set_page_config(page_title="Monitor", layout="wide")
st.title(f"📍 System-Check: Heute ist {heute_name}")

if ist_wochenende:
    st.warning("⚠️ WOCHENENDE: Die Zeile 95 wird heute blockiert.")
else:
    st.success("✅ MARKT OFFEN: Analyse aktiv.")

st.divider()

# --- MARKT-CHECK ---
st.subheader("📊 Markt-Check")
if ist_wochenende:
    st.write("DAX & Nasdaq: [Pause bis Montag 09:00]")
else:
    # Hier nur an Werktagen rechnen
    pass 

st.divider()

# --- DEIN BIO-CHECK (IMMUTABLE) ---
st.subheader("🧘 Bio-Check & Backup")
col1, col2 = st.columns(2)

with col1:
    st.error("WANDSITZ: Atmen! Keine Pressatmung halten!")
    st.write("🌱 Blutdruck: Sprossen & Rote Bete nutzen")

with col2:
    with st.expander("ℹ️ Deine Reise-Infos"):
        st.write("🎟️ Österreich Ticket ist aktiv")
        st.write("🥜 Snack: Nüsse für unterwegs")
        st.write("⚠️ Keine Mundspülung mit Chlorhexidin!")

# Automatischer Refresh
time.sleep(60)
st.rerun()
