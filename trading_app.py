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
        if data.empty or len(data) < periods: return None
        
        # Sicherstellen, dass wir nur die 'Close' Spalte als Series haben
        close = data['Close']
        if isinstance(close, pd.DataFrame):
            close = close.iloc[:, 0]

        delta = close.diff()
        up = delta.clip(lower=0)
        down = -1 * delta.clip(upper=0)
        
        ema_up = up.ewm(com=periods-1, adjust=False).mean()
        ema_down = down.ewm(com=periods-1, adjust=False).mean()
        
        rs = ema_up / ema_down
        rsi = 100 - (100 / (1 + rs))
        
        final_val = rsi.iloc[-1]
        return float(final_val) if not pd.isna(final_val) else None
    except:
        return None

def get_market_data():
    try:
        data = yf.download(["EURUSD=X", "^GDAXI", "^IXIC"], period="1d", interval="1m", progress=False)
        def get_last(ticker):
            try:
                val = data['Close'][ticker].dropna()
                return val.iloc[-1] if not val.empty else None
            except: return None
            
        return get_last("EURUSD=X"), get_last("^GDAXI"), get_last("^IXIC")
    except:
        return None, None, None

# --- 4. MARKT-CHECK ---
st.subheader("📈 Markt-Check: Euro/USD | DAX | Nasdaq")
val_eurusd, val_dax, val_nasdaq = get_market_data()
m1, m2, m3 = st.columns(3)

def display_metric(label, val, is_index=False):
    if val is None or pd.isna(val):
        st.write(f"*{label}*")
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

# --- 5. BÖRSEN-WETTER ---
st.subheader("🌦️ Börsen-Wetter (Live RSI Sortierung)")

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
        continue
    if rsi_val < 10:
        eiszeit.append((t, rsi_val))
    elif rsi_val > 90:
        sturm.append((t, rsi_val))
    else:
        sonnig.append((t, rsi_val))

with w1:
    st.info("🔴 Eiszeit / Frost (RSI < 10%)")
    if not eiszeit: st.markdown(no_data_html, unsafe_allow_html=True)
    for t, v in eiszeit: st.write(f"*{t}*: {v:.2f}%")

with w2:
    st.info("🟢 Sonnig / Heiter (10% - 90%)")
    if not sonnig: st.markdown(no_data_html, unsafe_allow_html=True)
    for t, v in sonnig: st.write(f"{t}: {v:.2f}%")

with w3:
    st.info("🟣 Sturm / Gewitter (RSI > 90%)")
    if not sturm: st.markdown(no_data_html, unsafe_allow_html=True)
    for t, v in sturm: st.write(f"⚠️ *{t}*: {v:.2f}%")

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

time.sleep(60)
st.rerun()
