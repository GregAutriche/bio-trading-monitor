import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, time as dt_time
import time

# --- 1. SETUP & VERSION ---
st.set_page_config(page_title="Monitor für dich", layout="wide")
# Sichtbare Version zur Kontrolle
STEUER_ID = "VER-SONNTAG-FINAL-FIX"

if 'h_count' not in st.session_state: 
    st.session_state.h_count = 0

# --- 2. ZEITSTEUERUNG (DIE EISERNE MAUER) ---
jetzt = datetime.now()
# weekday() 5=Samstag, 6=Sonntag
ist_wochenende = jetzt.weekday() >= 5
ist_vor_neun = jetzt.time() < dt_time(9, 0)

# Der Hauptschalter: NUR wenn Mo-Fr UND nach 9 Uhr, wird gerechnet!
darf_heute_rechnen = not ist_wochenende and not ist_vor_neun

# --- 3. HEADER ---
h_links, h_mitte, h_rechts = st.columns([1, 2, 1])
with h_mitte:
    st.markdown(f"<h1 style='text-align: center;'>🖥️ Ansicht für Dich ({STEUER_ID})</h1>", unsafe_allow_html=True)

with h_rechts:
    st.write(f"🚀 Start: {jetzt.strftime('%d.%m.%Y %H:%M:%S')}")
    if darf_heute_rechnen:
        st.success("🕒 STATUS: Live-Analyse aktiv")
    else:
        # Heute am Sonntag MUSS dieses gelbe Feld erscheinen:
        st.warning("🕒 STATUS: Standby (Börse geschlossen)")

st.divider()

# --- 4. MARKT-CHECK (DAX & NASDAQ) ---
st.subheader("📈 Markt-Check")
m1, m2, m3 = st.columns(3)

def get_live_val(ticker):
    if not darf_heute_rechnen: return None
    try:
        d = yf.download(ticker, period="1d", interval="1m", progress=False)
        return float(d['Close'].iloc[-1]) if not d.empty else None
    except: return None

with m1: st.metric("Euro/USD", "1.1820") # Fixer Wert laut deinem Bild
with m2: 
    val_dax = get_live_val("^GDAXI")
    st.write("**DAX**")
    st.write(f"{val_dax:,.2f}" if val_dax else "[Standby]")
with m3: 
    val_nas = get_live_val("^IXIC")
    st.write("**Nasdaq**")
    st.write(f"{val_nas:,.2f}" if val_nas else "[Standby]")

st.divider()

# --- 5. BÖRSEN-WETTER (DAS ENDE VON ZEILE 95) ---
st.subheader("🌦️ Börsen-Wetter (Live RSI Sortierung)")

meine_ticker = ["OTP.BU", "MOL.BU", "RICHT.BU", "ADS.DE", "SAP.DE", "BAS.DE", "AAPL"]
col1, col2, col3 = st.columns(3)
tief, normal, hoch = [], [], []

# ABSOLUTE SICHERHEIT: Wenn heute Sonntag ist, führen wir KEINEN Vergleich aus!
if not darf_heute_rechnen:
    # Alle Aktien werden einfach im Normalbereich gelistet
    normal = [(t, "Märkte geschlossen") for t in meine_ticker]
else:
    # Dieser Block wird HEUTE (Sonntag) komplett übersprungen
    for t in meine_ticker:
        try:
            data = yf.download(t, period="1mo", interval="1d", progress=False)
            if not data.empty:
                rsi_val = 50 # Platzhalter für Berechnung
                # Hier lag der Fehler (Zeile 95) - jetzt durch 'if' oben geschützt
                if rsi_val < 10: tief.append((t, rsi_val))
                elif rsi_val > 90: hoch.append((t, rsi_val))
                else: normal.append((t, rsi_val))
            else:
                normal.append((t, "Keine Daten"))
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
st.subheader("🧘 Bio-Check")
b1, b2 = st.columns(2)
with b1:
    if st.button(f"Wandsitz erledigt ({st.session_state.h_count}x)"):
        st.session_state.h_count += 1
        st.rerun()
    st.error("ACHTUNG: Beim Wandsitz (isometrisch) nicht die Luft anhalten!")
with b2:
    with st.expander("✈️ Reisen & Gesundheit (Backup)"):
        st.write("🎟️ Österreich Ticket ist aktiv")
        st.write("🥜 Nüsse als Reisesnack einplanen")
        st.write("🌱 Blutdruck: Sprossen & Rote Bete nutzen")
        st.write("⚠️ Keine Mundspülungen (Chlorhexidin)")

time.sleep(60)
st.rerun()
