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
    # Sonntag (6) oder Samstag (5) -> Keine Live-Analyse
    if jetzt.weekday() >= 5:
        return False
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
    # Statusanzeige basierend auf Handelszeit
    if ist_handelszeit():
        st.info("🕒 STATUS: Live-Analyse aktiv")
    else:
        st.warning("🕒 STATUS: Markt geschlossen - Default Anzeige")

st.divider()

# --- 4. DATENABFRAGE ---
def get_market_data():
    if not ist_handelszeit():
        return None, None, None
    try:
        # Nur am Wochenende/Nachts können Ticker wie ^GDAXI leer sein
        data = yf.download(["EURUSD=X", "^GDAXI", "^IXIC"], period="1d", interval="1m", progress=False)
        if data.empty: return None, None, None
        
        def pick(ticker):
            try:
                s = data['Close'][ticker].dropna()
                return float(s.iloc[-1]) if not s.empty else None
            except: return None
        return pick("EURUSD=X"), pick("^GDAXI"), pick("^IXIC")
    except:
        return None, None, None

# --- 5. MARKT-CHECK ANZEIGE ---
st.subheader("📈 Markt-Check: Euro/USD | DAX | Nasdaq")
val_eurusd, val_dax, val_nasdaq = get_market_data()
m1, m2, m3 = st.columns(3)

def display_metric(label, val, is_index=False):
    # Wenn Wert None ist oder wir außerhalb der Handelszeit sind -> Rot [No Data]
    if val is None or pd.isna(val):
        st.write(f"**{label}**")
        st.markdown(f"<span style='color:red; font-weight:bold;'>[No Data]</span>", unsafe_allow_html=True)
    else:
        fmt = f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if is_index else f"{val:.4f}"
        st.metric(label, fmt)

with m1: display_metric("Euro/USD", val_eurusd)
with m2: display_metric("DAX", val_dax, is_index=True)
with m3: display_metric("Nasdaq", val_nasdaq, is_index=True)

st.divider()

# --- 6. BÖRSEN-WETTER (FIXIERTE DEFAULT ANZEIGE) ---
st.subheader("🌦️ Börsen-Wetter (RSI Analyse)")

meine_ticker = [
    "OTP.BU", "MOL.BU", "RICHT.BU", "ADS.DE", "SAP.DE", "BAS.DE", 
    "ALV.DE", "BMW.DE", "DTE.DE", "IFX.DE", "VOW3.DE", "A4L.SO", "IBG.SO", "AAPL"
]

w1, w2, w3 = st.columns(3)
no_data_red = "<span style='color:red; font-weight:bold;'>[No Data]</span>"

# Listen für die Sortierung
extrem_tief, normalbereich, extrem_hoch = [], [], []

# LOGIK: Wenn Wochenende (heute), dann direkt alles in Normalbereich schieben
if not ist_handelszeit():
    for t in meine_ticker:
        normalbereich.append((t, "Standby"))
else:
    # Nur während der Woche wird gerechnet
    # (Hier käme die calculate_rsi Funktion rein, falls ist_handelszeit True ist)
    normalbereich = [(t, "Markt offen - Lade...") for t in meine_ticker]

with w1:
    st.info("🔴 Extrem Tief (RSI < 10%)")
    st.markdown(no_data_red, unsafe_allow_html=True)

with w2:
    st.success("🟢 Normalbereich (10% - 90%)")
    # Hier wird heute deine Liste angezeigt
    for t, v in normalbereich:
        st.write(f"{t}: {v}")

with w3:
    st.warning("🟣 Extrem Hoch (RSI > 90%)")
    st.markdown(no_data_red, unsafe_allow_html=True)

st.divider()

# --- 7. BIO-CHECK & BACKUP ---
st.subheader("🧘 Dein Bio-Check")
b1, b2 = st.columns([1, 1])

with b1:
    if st.button(f"Wandsitz erledigt (Heute: {st.session_state.h_count}x)"):
        st.session_state.h_count += 1
        st.rerun()
    st.error("WANDSITZ: Atmen! Keine Pressatmung!")

with b2:
    with st.expander("✈️ Reisen & Gesundheit"):
        # Backup Informationen gemäß Vorgabe
        st.write("🥜 Nüsse für unterwegs")
        st.write("🌱 Sprossen & Rote Bete")
        st.write("⚠️ Kein Chlorhexidin / Keine Phosphate")

time.sleep(60)
st.rerun()
