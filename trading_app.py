import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# --- 1. KONFIGURATION ---
st.set_page_config(page_title="Monitor für dich", layout="wide")

# Deine Ticker & Stand 06.02.
meine_ticker = {
    "EUR/USD": {"symbol": "EURUSD=X", "default": 1.1778, "datum": "06.02. 00:00"},
    "DAX Index": {"symbol": "^GDAXI", "default": 24721.46, "datum": "06.02. 00:00"},
    "NASDAQ 100": {"symbol": "^IXIC", "default": 23031.21, "datum": "06.02. 00:00"}
}

# --- 2. FUNKTIONEN (WETTERBERICHT & STATUS) ---
def hole_wetterbericht(symbol):
    try:
        # Kurzer Abruf für RSI/ATR
        data = yf.download(symbol, period="30d", interval="1d", progress=False)
        if data.empty: return "N/A", "N/A"
        
        # RSI (14 Tage)
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + (gain / loss))).iloc[-1]
        
        # ATR (14 Tage)
        tr = pd.concat([data['High']-data['Low'], 
                        abs(data['High']-data['Close'].shift()), 
                        abs(data['Low']-data['Close'].shift())], axis=1).max(axis=1)
        atr = tr.rolling(window=14).mean().iloc[-1]
        return f"{atr:.2f}", f"{rsi:.1f}"
    except:
        return "N/A", "N/A"

def check_daten_status(info):
    try:
        t = yf.Ticker(info["symbol"])
        df = t.history(period="1d")
        # Prüfung ob Daten vom heutigen Tag vorliegen
        if not df.empty and df.index[-1].date() == datetime.now().date():
            return df['Close'].iloc[-1], df.index[-1].strftime('%d.%m. %H:%M'), True
        return info["default"], info["datum"], False
    except:
        return info["default"], info["datum"], False

# --- 3. HEADER: NEUER NAME & ZEITSTEMPEL ---
st.title("🖥️ Monitor für dich")
letztes_update = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
st.write(f"**Letztes Update:** {letztes_update}")

cols = st.columns(len(meine_ticker))
ist_irgendwas_live = False

for i, (name, info) in enumerate(meine_ticker.items()):
    preis, zeit, live = check_daten_status(info)
    if live: ist_irgendwas_live = True
    atr, rsi = hole_wetterbericht(info["symbol"])
    
    with cols[i]:
        st.metric(label=name, value=f"{preis:,.4f}" if "USD" in name else f"{preis:,.2f}")
        st.caption(f"☁️ ATR: {atr} | 🌡️ RSI: {rsi}")
        status_tag = ":green[[data]]" if live else ":red[[no data]]"
        st.write(f"{zeit} {status_tag}")

st.divider()

# --- 4. BEWERTUNGSSKALA: EINHEITLICHE LOGIK ---
status_label = ":green[[data]]" if ist_irgendwas_live else ":red[[no data]]"
st.subheader(f"📈 Markt-Check & China-Exposure Logik {status_label}")
wert = st.number_input("Aktueller Analyse-Wert (%)", value=5, step=1)

st.write(f"### Bewertungsskala: {status_label}")
l, m, r = st.columns(3)

# Neutral-Modus bei [no data], Aktiv-Modus nur bei [data]
with l:
    if ist_irgendwas_live and wert < 10:
        st.error("🔴 **EXTREM TIEF**\n\nStatus: AKTIV")
    else:
        st.write("🔴 **Extrem Tief**")
        st.info("Möglichkeit: < 10%")

with m:
    if ist_irgendwas_live and 10 <= wert <= 90:
        st.success("🟢 **Normalbereich**\n\nStatus: AKTIV")
    else:
        st.write("🟢 **Normalbereich**")
        st.info("Möglichkeit: 10% - 90%")

with r:
    if ist_irgendwas_live and wert > 90:
        st.error("🔴 **EXTREM HOCH**\n\nStatus: AKTIV")
