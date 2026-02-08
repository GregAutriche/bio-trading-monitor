import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime
import time

# --- 1. SETUP ---
st.set_page_config(page_title="Monitor für dich", layout="wide")

if 'h_count' not in st.session_state: 
    st.session_state.h_count = 0

# --- 2. HEADER ---
h_links, h_mitte, h_rechts = st.columns([1, 2, 1])

with h_mitte:
    st.markdown("<h1 style='text-align: center;'>🖥️ Ansicht für Dich</h1>", unsafe_allow_html=True)

with h_rechts:
    jetzt = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    st.write(f"🚀 Start: {jetzt}")
    st.info("🕒 STATUS: Live-Abfrage aktiv")

st.divider()

# --- 3. DATENABFRAGE LOGIK ---
def get_live_data():
    try:
        # Abfrage der Ticker
        # Euro/USD (EURUSD=X), DAX (^GDAXI), Nasdaq (^IXIC)
        data = yf.download(["EURUSD=X", "^GDAXI", "^IXIC"], period="1d", interval="1m", progress=False)
        
        eur_usd = data['Close']['EURUSD=X'].iloc[-1] if not data['Close']['EURUSD=X'].empty else None
        dax = data['Close']['^GDAXI'].iloc[-1] if not data['Close']['^GDAXI'].empty else None
        nasdaq = data['Close']['^IXIC'].iloc[-1] if not data['Close']['^IXIC'].empty else None
        
        return eur_usd, dax, nasdaq
    except:
        return None, None, None

val_eurusd, val_dax, val_nasdaq = get_live_data()

# --- 4. MARKT-CHECK ANZEIGE ---
st.subheader("📈 Markt-Check: Euro/USD | DAX | Nasdaq")
m1, m2, m3 = st.columns(3)

def display_metric(label, val, is_index=False):
    if val is None or pd.isna(val):
        st.write(f"**{label}**")
        st.markdown(f"<span style='color:red; font-weight:bold;'>[No Data]</span>", unsafe_allow_html=True)
    else:
        if is_index:
            # Index: 2 Stellen + Tausendertrenner
            formatted = f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        else:
            # Währung: 4 Stellen
            formatted = f"{val:.4f}"
        st.metric(label, formatted)

with m1: 
    display_metric("Euro/USD", val_eurusd)
with m2: 
    display_metric("DAX", val_dax, is_index=True)
with m3: 
    display_metric("Nasdaq", val_nasdaq, is_index=True)

st.divider()

# --- 5. BÖRSEN-WETTER ---
st.subheader("🌦️ Börsen-Wetter (RSI & ADR Analyse)")
# Hier deine 14 Titel einpflegen
meine_titel = [] 

w1, w2, w3 = st.columns(3)
no_data_html = "<span style='color:red; font-weight:bold;'>[No Data]</span>"

with w1:
    st.info("🔴 Eiszeit / Frost (RSI < 10%)")
    if not meine_titel: st.markdown(no_data_html, unsafe_allow_html=True)
    for t in meine_titel:
        if t.get("rsi") is not None and t["rsi"] < 10:
            st.write(f"{t['name']} ({t['ticker']}): {t['rsi']}%")
    
with w2:
    st.info("🟢 Sonnig / Heiter (10% - 90%)")
    if not meine_titel: st.markdown(no_data_html, unsafe_allow_html=True)
    for t in meine_titel:
        if t.get("rsi") is not None and 10 <= t["rsi"] <= 90:
            st.write(f"{t['name']}: {t['rsi']}%")
    
with w3:
    st.info("🟣 Sturm / Gewitter (RSI > 90%)")
    if not meine_titel: st.markdown(no_data_html, unsafe_allow_html=True)
    for t in meine_titel:
        if t.get("rsi") is not None and t["rsi"] > 90:
            st.write(f"{t['name']}: {t['rsi']}%")

st.divider()

# --- 6. BIO-CHECK ---
st.subheader("🧘 Dein Bio-Check")
b1, b2 = st.columns([1, 1])

with b1:
    if st.button(f"Wandsitz erledigt (Heute: {st.session_state.h_count}x)"):
        st.session_state.h_count += 1
        st.rerun()
    st.error("ACHTUNG: Atmen! Keine Pressatmung!")

with b2:
    with st.expander("✈️ Check: Reisen"):
        st.write("🥜 Nüsse einplanen")
        st.write("🌱 Sprossen / Rote Bete")
        st.write("⚠️ Keine Mundspülung (Chlorhexidin) / Keine Phosphate")

# --- 7. AUTO-REFRESH ---
time.sleep(60)
st.rerun()
