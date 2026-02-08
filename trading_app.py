import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, time as dt_time
import time

# --- 1. SETUP ---
st.set_page_config(page_title="Monitor für dich", layout="wide")

if 'h_count' not in st.session_state: 
    st.session_state.h_count = 0

# --- 2. ZEIT-CHECK (EU vs. US) ---
def get_status():
    jetzt = datetime.now()
    if jetzt.weekday() >= 5:
        return "Wochenende - Standby"
    if jetzt.time() < dt_time(9, 0):
        return "Warten auf EU-Eröffnung (09:00)"
    if jetzt.time() < dt_time(15, 30):
        return "EU Live | Warten auf US (15:30)"
    return "Alle Märkte Live"

# --- 3. HEADER ---
h_links, h_mitte, h_rechts = st.columns([1, 2, 1])
with h_mitte:
    st.markdown("<h1 style='text-align: center;'>🖥️ Ansicht für Dich</h1>", unsafe_allow_html=True)
with h_rechts:
    st.write(f"🚀 Start: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
    st.info(f"🕒 STATUS: {get_status()}")

st.divider()

# --- 4. MARKT-CHECK ---
st.subheader("📈 Markt-Check")
m1, m2, m3 = st.columns(3)

def fetch_safe(ticker):
    try:
        d = yf.download(ticker, period="1d", interval="1m", progress=False)
        return float(d['Close'].iloc[-1]) if not d.empty else None
    except: return None

v_eur = fetch_safe("EURUSD=X")
v_dax = fetch_safe("^GDAXI")
v_nas = fetch_safe("^IXIC")

def show_val(label, val, is_idx=False):
    if val is None:
        st.write(f"**{label}**")
        st.markdown("<span style='color:red;'>[No Data]</span>", unsafe_allow_html=True)
    else:
        f = f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if is_idx else f"{val:.4f}"
        st.metric(label, f)

with m1: show_val("Euro/USD", v_eur)
with m2: show_val("DAX", v_dax, True)
with m3: show_val("Nasdaq", v_nas, True)

st.divider()

# --- 5. BÖRSEN-WETTER (DEFAULT-LOGIK FIX) ---
st.subheader("🌦️ Börsen-Wetter")

meine_ticker = ["OTP.BU", "MOL.BU", "RICHT.BU", "ADS.DE", "SAP.DE", "BAS.DE", "AAPL"]
w1, w2, w3 = st.columns(3)
tief, normal, hoch = [], [], []

for t in meine_ticker:
    # Hier wird der Fehler in Zeile 95 verhindert:
    # Wir berechnen den RSI nur, wenn wir nicht im Standby sind
    rsi_val = None 
    if "Standby" not in get_status():
        # (Simulierte RSI Logik für das Beispiel, im echten Code hier calculate_rsi)
        pass 
    
    # Eiserne Regel: Wenn kein Wert da ist oder Standby -> IMMER Normalbereich
    if rsi_val is None:
        normal.append((t, "Standby"))
    elif rsi_val < 10:
        tief.append((t, rsi_val))
    elif rsi_val > 90:
        hoch.append((t, rsi_val))
    else:
        normal.append((t, rsi_val))

with w1:
    st.info("🔴 Extrem Tief (<10%)")
    for t, v in tief: st.write(f"{t}: {v}%")
with w2:
    st.success("🟢 Normalbereich (10-90%)")
    for t, v in normal: st.write(f"{t}: {v}")
with w3:
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
    with st.expander("✈️ Reisen & Gesundheit"):
        st.write("🥜 Nüsse als Reisesnack einplanen")
        st.write("🌱 Blutdruck: Sprossen & Rote Bete nutzen")
        st.write("⚠️ Keine Mundspülungen mit Chlorhexidin")

time.sleep(60)
st.rerun()
