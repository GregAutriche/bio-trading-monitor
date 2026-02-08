import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, time as dt_time
import time

# --- 1. SETUP ---
st.set_page_config(page_title="Monitor für dich", layout="wide")

if 'h_count' not in st.session_state: 
    st.session_state.h_count = 0

# --- 2. HANDELSZEITEN-CHECK ---
def ist_handelszeit():
    jetzt = datetime.now()
    if jetzt.weekday() > 4: # Wochenende
        return False
    if jetzt.time() < dt_time(9, 0): # Vor 9 Uhr
        return False
    return True

# --- 3. HEADER ---
h_links, h_mitte, h_rechts = st.columns([1, 2, 1])

with h_mitte:
    st.markdown("<h1 style='text-align: center;'>🖥️ Ansicht für Dich</h1>", unsafe_allow_html=True)

with h_rechts:
    jetzt_str = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    st.write(f"🚀 Start: {jetzt_str}")
    status_text = "Aktiv" if ist_handelszeit() else "Börse geschlossen (Start Mo-Fr 09:00)"
    st.info(f"🕒 STATUS: {status_text}")

st.divider()

# --- 4. DATENABFRAGE & RSI LOGIK ---
def calculate_rsi(ticker_symbol, periods=14):
    if not ist_handelszeit():
        return None
    try:
        df = yf.download(ticker_symbol, period="1mo", interval="1d", progress=False)
        if df is None or df.empty or len(df) <= periods:
            return None
        close = df['Close']
        if isinstance(close, pd.DataFrame):
            close = close.iloc[:, 0]
        close = close.dropna()
        delta = close.diff()
        up = delta.clip(lower=0)
        down = -1 * delta.clip(upper=0)
        ema_up = up.ewm(com=periods-1, adjust=False).mean()
        ema_down = down.ewm(com=periods-1, adjust=False).mean()
        rs = ema_up / ema_down
        rsi_series = 100 - (100 / (1 + rs))
        val = rsi_series.iloc[-1]
        return float(val) if not pd.isna(val) else None
    except:
        return None

def get_market_data():
    if not ist_handelszeit():
        return None, None, None
    try:
        data = yf.download(["EURUSD=X", "^GDAXI", "^IXIC"], period="1d", interval="1m", progress=False)
        def pick_last(ticker):
            try:
                s = data['Close'][ticker].dropna()
                return float(s.iloc[-1]) if not s.empty else None
            except: return None
        return pick_last("EURUSD=X"), pick_last("^GDAXI"), pick_last("^IXIC")
    except:
        return None, None, None

# --- 5. MARKT-CHECK ---
st.subheader("📈 Markt-Check: Euro/USD | DAX | Nasdaq")
val_eurusd, val_dax, val_nasdaq = get_market_data()
m1, m2, m3 = st.columns(3)

def display_metric(label, val, is_index=False):
    if val is None or pd.isna(val):
        st.write(f"**{label}**")
        st.markdown(f"<span style='color:red; font-weight:bold;'>[No Data]</span>", unsafe_allow_html=True)
    else:
        if is_index:
            # 2 Nachkommastellen bei Indizes
            formatted = f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        else:
            # 4 Nachkommastellen bei Währung
            formatted = f"{val:.4f}"
        st.metric(label, formatted)

with m1: display_metric("Euro/USD", val_eurusd)
with m2: display_metric("DAX", val_dax, is_index=True)
with m3: display_metric("Nasdaq", val_nasdaq, is_index=True)

st.divider()

# --- 6. BÖRSEN-WETTER (10/90 Logik) ---
st.subheader("🌦️ Börsen-Wetter (RSI Analyse)")

meine_ticker = [
    "OTP.BU", "MOL.BU", "RICHT.BU", "ADS.DE", "SAP.DE", "BAS.DE", 
    "ALV.DE", "BMW.DE", "DTE.DE", "IFX.DE", "VOW3.DE", "A4L.SO", "IBG.SO", "AAPL"
]

w1, w2, w3 = st.columns(3)
no_data_red = "<span style='color:red; font-weight:bold;'>[No Data]</span>"

extrem_tief, normalbereich, extrem_hoch = [], [], []

if ist_handelszeit():
    for t in meine_ticker:
        r = calculate_rsi(t)
        if r is None: continue
        # Logik gemäß Vorgabe
        if r < 10: extrem_tief.append((t, r))
        elif r > 90: extrem_hoch.append((t, r))
        else: normalbereich.append((t, r))

with w1:
    st.info("🔴 Extrem Tief (RSI < 10%)")
    if not extrem_tief: st.markdown(no_data_red, unsafe_allow_html=True)
    for t, v in extrem_tief: st.write(f"**{t}**: {v:.2f}%")

with w2:
    st.success("🟢 Normalbereich (10% - 90%)")
    if not normalbereich: st.markdown(no_data_red, unsafe_allow_html=True)
    for t, v in normalbereich: st.write(f"{t}: {v:.2f}%")

with w3:
    st.warning("🟣 Extrem Hoch (RSI > 90%)")
    if not extrem_hoch: st.markdown(no_data_red, unsafe_allow_html=True)
    for t, v in extrem_hoch: st.write(f"⚠️ **{t}**: {v:.2f}%")

st.divider()

# --- 7. BIO-CHECK ---
st.subheader("🧘 Dein Bio-Check")
b1, b2 = st.columns([1, 1])

with b1:
    if st.button(f"Wandsitz erledigt (Heute: {st.session_state.h_count}x)"):
        st.session_state.h_count += 1
        st.rerun()
    # Warnung Wandsitz
    st.error("ACHTUNG: Atmen! Keine Pressatmung während des isometrischen Trainings!")

with b2:
    with st.expander("✈️ Reisen & Gesundheit"):
        # Backup-Informationen
        st.write("🥜 Nüsse einplanen (Snack für Reisen)")
        st.write("🌱 Sprossen / Rote Bete (Blutdrucksenkung)")
        st.write("⚠️ Keine Mundspülungen (Chlorhexidin) / Keine Phosphate")

time.sleep(60)
st.rerun()
