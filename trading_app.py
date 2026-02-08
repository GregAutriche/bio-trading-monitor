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
    st.info("🕒 STATUS: Live-Analyse aktiv")

st.divider()

# --- 3. DATENABFRAGE & RSI LOGIK ---
def calculate_rsi(ticker_symbol, periods=14):
    try:
        data = yf.download(ticker_symbol, period="1mo", interval="1d", progress=False)
        if data.empty: return None
        
        close_delta = data['Close'].diff()
        up = close_delta.clip(lower=0)
        down = -1 * close_delta.clip(upper=0)
        
        ma_up = up.rolling(window=periods).mean()
        ma_down = down.rolling(window=periods).mean()
        
        rsi = ma_up / ma_down
        rsi = 100 - (100 / (1 + rsi))
        return rsi.iloc[-1]
    except:
        return None

def get_market_data():
    try:
        data = yf.download(["EURUSD=X", "^GDAXI", "^IXIC"], period="1d", interval="1m", progress=False)
        eur_usd = data['Close']['EURUSD=X'].iloc[-1] if not data['Close']['EURUSD=X'].empty else None
        dax = data['Close']['^GDAXI'].iloc[-1] if not data['Close']['^GDAXI'].empty else None
        nasdaq = data['Close']['^IXIC'].iloc[-1] if not data['Close']['^IXIC'].empty else None
        return eur_usd, dax, nasdaq
    except:
        return None, None, None

# --- 4. MARKT-CHECK ---
st.subheader("📈 Markt-Check: Euro/USD | DAX | Nasdaq")
val_eurusd, val_dax, val_nasdaq = get_market_data()
m1, m2, m3 = st.columns(3)

def display_metric(label, val, is_index=False):
    if val is None or pd.isna(val):
        st.write(f"**{label}**")
        st.markdown(f"<span style='color:red; font-weight:bold;'>[No Data]</span>", unsafe_allow_html=True)
    else:
        if is_index:
            formatted = f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        else:
            formatted = f"{val:.4f}"
        st.metric(label, formatted)

with m1: display_metric("Euro/USD", val_eurusd)
with m2: display_metric("DAX", val_dax, is_index=True)
with m3: display_metric("Nasdaq", val_nasdaq, is_index=True)

st.divider()

# --- 5. BÖRSEN-WETTER (AUTOMATISCH) ---
st.subheader("🌦️ Börsen-Wetter (Live RSI Sortierung)")

# Hier deine 14 Ticker einpflegen (Beispiel-Liste zum Befüllen)
meine_ticker = [
    "OTP.BU", "MOL.BU", "RICHT.BU", "ADS.DE", "SAP.DE", "BAS.DE", 
    "ALV.DE", "BMW.DE", "DTE.DE", "IFX.DE", "VOW3.DE", "A4L.SO", "IBG.SO", "AAPL"
]

w1, w2, w3 = st.columns(3)
no_data_html = "<span style='color:red; font-weight:bold;'>[No Data]</span>"

eiszeit, sonnig, sturm = [], [], []

for t in meine_ticker:
    rsi_val = calculate_rsi(t)
    if rsi_val is None:
        continue # Wird unten als No Data angezeigt, wenn Listen leer bleiben
    elif rsi_val < 10:
        eiszeit.append((t, rsi_val))
    elif rsi_val > 90:
        sturm.append((t, rsi_val))
    else:
        sonnig.append((t, rsi_val))

with w1:
    st.error("🔴 Eiszeit / Frost (RSI < 10%)")
    if not eiszeit: st.markdown(no_data_html, unsafe_allow_html=True)
    for t, v in eiszeit: st.write(f"**{t}**: {v:.2f}%")

with w2:
    st.success("🟢 Sonnig / Heiter (10% - 90%)")
    if not sonnig: st.markdown(no_data_html, unsafe_allow_html=True)
    for t, v in sonnig: st.write(f"{t}: {v:.2f}%")

with w3:
    st.warning("🟣 Sturm / Gewitter (RSI > 90%)")
    if not sturm: st.markdown(no_data_html, unsafe_allow_html=True)
    for t, v in sturm: st.write(f"⚠️ **{t}**: {v:.2f}%")

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
