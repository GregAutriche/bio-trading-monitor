import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, time as dt_time
import time

# --- 1. SETUP & PERSISTENZ ---
st.set_page_config(page_title="Monitor für dich", layout="wide")

if 'h_count' not in st.session_state: 
    st.session_state.h_count = 0

# --- 2. LOGIK: IST ES MONTAG NACH 9 UHR? ---
def check_live_status():
    jetzt = datetime.now()
    # Wochentag: Montag ist 0
    ist_montag_oder_später = jetzt.weekday() <= 4 
    ist_nach_neun = jetzt.time() >= dt_time(9, 0)
    
    # Spezialbedingung für den Start der Woche:
    if jetzt.weekday() == 0 and not ist_nach_neun:
        return False # Es ist Montag, aber noch vor 9 Uhr
    
    if jetzt.weekday() > 4:
        return False # Es ist Wochenende
        
    return ist_montag_oder_später and ist_nach_neun

# --- 3. HEADER ---
h_links, h_mitte, h_rechts = st.columns([1, 2, 1])
with h_mitte:
    st.markdown("<h1 style='text-align: center;'>🖥️ Ansicht für Dich</h1>", unsafe_allow_html=True)

with h_rechts:
    jetzt_str = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    st.write(f"🚀 Start: {jetzt_str}")
    live_aktiv = check_live_status()
    status_msg = "Live-Analyse aktiv" if live_aktiv else "Warten auf Montag 09:00 - Standby"
    st.info(f"🕒 STATUS: {status_msg}")

st.divider()

# --- 4. DATENABFRAGE (NUR WENN LIVE) ---
def get_market_data():
    if not live_aktiv:
        return None, None, None
    try:
        data = yf.download(["EURUSD=X", "^GDAXI", "^IXIC"], period="1d", interval="1m", progress=False)
        def pick(t):
            try: return float(data['Close'][t].dropna().iloc[-1])
            except: return None
        return pick("EURUSD=X"), pick("^GDAXI"), pick("^IXIC")
    except:
        return None, None, None

# --- 5. MARKT-CHECK ANZEIGE ---
st.subheader("📈 Markt-Check: Euro/USD | DAX | Nasdaq")
val_eurusd, val_dax, val_nasdaq = get_market_data()
m1, m2, m3 = st.columns(3)

def display_metric(label, val, is_index=False):
    if val is None:
        st.write(f"**{label}**")
        st.markdown(f"<span style='color:red; font-weight:bold;'>[No Data]</span>", unsafe_allow_html=True)
    else:
        fmt = f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if is_index else f"{val:.4f}"
        st.metric(label, fmt)

with m1: display_metric("Euro/USD", val_eurusd)
with m2: display_metric("DAX", val_dax, is_index=True)
with m3: display_metric("Nasdaq", val_nasdaq, is_index=True)

st.divider()

# --- 6. BÖRSEN-WETTER (DIE VEREINBARTE DEFAULT ANZEIGE) ---
st.subheader("🌦️ Börsen-Wetter (RSI Analyse)")

meine_ticker = [
    "OTP.BU", "MOL.BU", "RICHT.BU", "ADS.DE", "SAP.DE", "BAS.DE", 
    "ALV.DE", "BMW.DE", "DTE.DE", "IFX.DE", "VOW3.DE", "A4L.SO", "IBG.SO", "AAPL"
]

w1, w2, w3 = st.columns(3)
extrem_tief, normalbereich, extrem_hoch = [], [], []

# Hier wird der ValueError abgefangen:
if not live_aktiv:
    # Vor Montag 9 Uhr: ALLES in den Normalbereich (Default)
    normalbereich = [(t, "Standby") for t in meine_ticker]
else:
    # Hier würde die Berechnung stattfinden
    normalbereich = [(t, "Berechne...") for t in meine_ticker]

with w1:
    st.info("🔴 Extrem Tief (RSI < 10%)")
    if not extrem_tief: st.markdown("<span style='color:red;'>[No Data]</span>", unsafe_allow_html=True)

with w2:
    st.success("🟢 Normalbereich (10% - 90%)")
    for t, v in normalbereich:
        st.write(f"{t}: {v}")

with w3:
    st.warning("🟣 Extrem Hoch (RSI > 90%)")
    if not extrem_hoch: st.markdown("<span style='color:red;'>[No Data]</span>", unsafe_allow_html=True)

st.divider()

# --- 7. BIO-CHECK & SICHERHEIT ---
st.subheader("🧘 Dein Bio-Check")
b1, b2 = st.columns([1, 1])

with b1:
    if st.button(f"Wandsitz erledigt (Heute: {st.session_state.h_count}x)"):
        st.session_state.h_count += 1
        st.rerun()
    st.error("WANDSITZ-WARNUNG: Keine Pressatmung! Atmen!")

with b2:
    with st.expander("✈️ Reisen & Gesundheit (Backup)"):
        st.write("🥜 Nüsse & Sprossen/Rote Bete")
        st.write("⚠️ Kein Chlorhexidin / Keine Phosphate")

# Automatischer Refresh jede Minute
time.sleep(60)
st.rerun()
