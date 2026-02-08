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
    # Nur Montag (0) bis Freitag (4)
    if jetzt.weekday() > 4:
        return False
    # Erst ab 09:00 Uhr morgens
    if jetzt.time() < dt_time(9, 0):
        return False
    return True

# --- 3. HEADER ---
h_links, h_mitte, h_rechts = st.columns([1, 2, 1])

with h_mitte:
    st.markdown("<h1 style='text-align: center;'>🖥️ Ansicht für Dich</h1>", unsafe_allow_html=True)

with h_rechts:
    jetzt_str = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    st.write(f"🚀 Start: {jetzt_str}")
    if ist_handelszeit():
        st.info("🕒 STATUS: Live-Analyse aktiv")
    else:
        st.warning("🕒 STATUS: Börse geschlossen (Start Mo-Fr 09:00)")

st.divider()

# --- 4. DATENABFRAGE & RSI LOGIK (ROBUST) ---
def calculate_rsi(ticker_symbol, periods=14):
    if not ist_handelszeit():
        return None
    try:
        data = yf.download(ticker_symbol, period="1mo", interval="1d", progress=False)
        if data.empty or len(data) < periods: return None
        
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
        
        val = rsi.iloc[-1]
        return float(val) if not pd.isna(val) else None
    except:
        return None

def get_market_data():
    if not ist_handelszeit():
        return None, None, None
    try:
        # Abfrage für Euro/USD, DAX und Nasdaq
        data = yf.download(["EURUSD=X", "^GDAXI", "^IXIC"], period="1d", interval="1m", progress=False)
        
        def pick_last(ticker):
            try:
                # Sicherstellen, dass wir einen Einzelwert ziehen
                series = data['Close'][ticker].dropna()
                return float(series.iloc[-1]) if not series.empty else None
            except: return None
            
        return pick_last("EURUSD=X"), pick_last("^GDAXI"), pick_last("^IXIC")
    except:
        return None, None, None

# --- 5. MARKT-CHECK ANZEIGE ---
st.subheader("📈 Markt-Check: Euro/USD | DAX | Nasdaq")
val_eurusd, val_dax, val_nasdaq = get_market_data()
m1, m2, m3 = st.columns(3)

def display_metric(label, val, is_index=False):
    if val is None or pd.isna(val):
        st.write(f"*{label}*")
        st.markdown(f"<span style='color:red; font-weight:bold;'>[No Data]</span>", unsafe_allow_html=True)
    else:
        if is_index:
            # Index: 2 Stellen + Tausendertrenner
            formatted = f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        else:
            # Währung: 4 Stellen
            formatted = f"{val:.4f}"
        st.metric(label, formatted)

with m1: display_metric("Euro/USD", val_eurusd)
with m2: display_metric("DAX", val_dax, is_index=True)
with m3: display_metric("Nasdaq", val_nasdaq, is_index=True)

st.divider()

# --- 6. BÖRSEN-WETTER (RSI SORTIERUNG) ---
st.subheader("🌦️ Börsen-Wetter (Live RSI Sortierung)")

# Deine 14 Ticker
meine_ticker = [
    "OTP.BU", "MOL.BU", "RICHT.BU", "ADS.DE", "SAP.DE", "BAS.DE", 
    "AL
