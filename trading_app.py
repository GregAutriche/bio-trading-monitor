import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime
import pytz
import requests

# 1. SETUP & ZEIT (Korrekt für Wien/Berlin)
st.set_page_config(page_title="Kontrollturm Aktiv", layout="wide")
local_tz = pytz.timezone('Europe/Berlin')
now = datetime.now(local_tz)

# --- NEU: WETTER FUNKTION (Wien) ---
def get_weather():
    try:
        # Koordinaten für Wien
        url = "https://api.open-meteo.com/v1/forecast?latitude=48.2085&longitude=16.3721&current_weather=true"
        response = requests.get(url).json()
        temp = response['current_weather']['temperature']
        return f"{temp}°C"
    except:
        return "--°C"

# --- DATEN FUNKTION MIT ECHTER 10/90 LOGIK ---
@st.cache_data(ttl=60)
def get_market_data(symbol):
    try:
        ticker = yf.Ticker(symbol)
        # Wir brauchen 1 Jahr für die Hoch/Tief Berechnung
        hist = ticker.history(period="1y")
        if hist.empty:
            return {"Preis": 0, "Pos%": 0, "Status": "N/A", "Trend": "⚪"}
        
        current_price = hist['Close'].iloc[-1]
        low_52w = hist['Low'].min()
        high_52w = hist['High'].max()
        
        # Deine 10/90 Regel Logik
        pos_percent = ((current_price - low_52w) / (high_52w - low_52w)) * 100
        
        if pos_percent < 10:
            status = "EXTREM TIEF"
            trend = "🔴" # Alarm bei extrem tiefem Stand
        elif pos_percent > 90:
            status = "EXTREM HOCH"
            trend = "🟢" # Läuft heiß
        else:
            status = "NORMAL"
            trend = "🟡"
            
        return {
            "Preis": current_price,
            "Pos%": pos_percent,
            "Status": status,
            "Trend": trend
        }
    except:
        return {"Preis": 0, "Pos%": 0, "Status": "Error", "Trend": "⚪"}

# 3. HEADER & INFOS (Jetzt mit Wetter und Checkliste)
st.title(f"🚀 KONTROLLTURM AKTIV | {now.strftime('%A, %d.%m.%Y | %H:%M:%S')}")

# Deine Gesundheits-Informationen oben (Backup-Info)
st.info(f"""
**Wetter Wien:** {get_weather()} | **Gesundheits-Check:** - Keine Mundspülungen (Chlorhexidin) & keine Phosphate (Fertiggerichte) 
- Isometrisches Training: **Wandsitz** (Vorsicht: Keine Pressatmung!) 
- Ernährung: Sprossen & Rote Bete zur Blutdrucksenkung nutzen.
""")

st.divider()

# 4. TOP INDIZES (Referenz-Header)
cols = st.columns(3)
# Ticker-Symbole für EUR/USD, DAX (Xetra) und NASDAQ
indices = [("EUR/USD", "EURUSD=X"), ("DAX (ADR)", "EWG"), ("NASDAQ", "QQQ")]

for i, (label, sym) in enumerate(indices):
    data = get_market_data(sym)
    cols[i].metric(label, f"{data['Preis']:.4f}" if "EUR" in label else f"{data['Preis']:.2f}", 
                   f"{data['Pos%']:.1f}% Pos.")

st.divider()

# 5. CHAMPIONS TABELLEN (Europa & USA)
col_left, col_right = st.columns(2)

# Liste deiner Champions (Beispiele basierend auf deinen Präferenzen)
eu_tickers = [
    ('ADS.DE', 'Adidas'), ('SAP.DE', 'SAP'), ('ASML.AS', 'ASML'), 
    ('MC.PA', 'LVMH'), ('SIE.DE', 'Siemens'), ('VOW3.DE', 'VW'), 
    ('OTP.BU', 'OTP Bank') # Inklusive Ungarn
]

us_tickers = [
    ('AAPL', 'Apple'), ('MSFT', 'Microsoft'), ('GOOGL', 'Google'), 
    ('AMZN', 'Amazon'), ('TSLA', 'Tesla'), ('META', 'Meta'), ('NVDA', 'Nvidia')
]

def create_table(ticker_list):
    table_data = []
    for sym, name in ticker_list:
        d = get_market_data(sym)
        table_data.append({
            "Trend": d['Trend'],
            "Name": name,
            "Preis(EUR)": f"{d['Preis']:.2f}",
            "Pos%": f"{d['Pos%']:.1f}%",
            "Status": d['Status']
        })
    return pd.DataFrame(table_data)

with col_left:
    st.subheader("Europa: Deine 7 Hidden Champions")
    st.table(create_table(eu_tickers))

with col_right:
    st.subheader("USA: Deine 7 Hidden Champions")
    st.table(create_table(us_tickers))
