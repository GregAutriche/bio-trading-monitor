import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import datetime

# --- 1. SETUP & WETTER API ---
st.set_page_config(page_title="Trading-Scanner Pro", layout="wide")
API_KEY = "DEIN_OPENWEATHER_APIimport streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import datetime

# --- 1. SETUP & WETTER API ---
st.set_page_config(page_title="Trading-Scanner Pro", layout="wide")
API_KEY = "DEIN_OPENWEATHER_API_KEY" # Hier eigenen Key einfügen
CITY = "Frankfurt" # Leitbörse für DAX

def get_weather(city):
    try:
        url = f"http://api.openweathermap.org{city}&appid={API_KEY}&units=metric&lang=de"
        data = requests.get(url).json()
        return {
            "temp": data['main']['temp'],
            "desc": data['weather'][0]['description'],
            "icon": data['weather'][0]['icon'],
            "main": data['weather'][0]['main'] # e.g. 'Clear', 'Rain'
        }
    except: return None

# --- 2. HEADER & WETTER ANZEIGE ---
weather = get_weather(CITY)
col_t1, col_t2 = st.columns([3, 1])
with col_t1:
    st.title("🚀 Trading-Monitor 2026")
with col_t2:
    if weather:
        st.markdown(f"**Börsenwetter ({CITY}):** {weather['temp']}°C, {weather['desc']}")
        # Wetter-Logik: Sonne = Bullisch (+5%), Regen = Vorsicht (-5%)
        wetter_bonus = 5 if weather['main'] in ['Clear', 'Clouds'] else -5
    else:
        wetter_bonus = 0
        st.caption("Wetterdaten nicht verfügbar")

# --- 3. SIDEBAR ---
st.sidebar.header("Konfiguration")
risiko_eur = st.sidebar.number_input("Risiko pro Trade (EUR)", value=500)
intervall = st.sidebar.selectbox("Intervall", ["1d", "1h", "15m", "5m"], index=0)
top_n = st.sidebar.slider("Top-Signale", 1, 10, 5)

# --- 4. ANALYSE-LOGIK MIT AKTIONS-FILTER ---
def get_analysis(ticker_dict, timeframe):
    results = []
    for symbol, name in ticker_dict.items():
        try:
            t = yf.Ticker(symbol)
            hist = t.history(period="60d", interval=timeframe)
            if len(hist) < 20: continue
            
            cp = hist['Close'].iloc[-1]
            sma20 = hist['Close'].rolling(20).mean().iloc[-1]
            is_bullish = cp > sma20
            
            # Basis-Wahrscheinlichkeit + Wetter-Einfluss
            prob = 50 + (20 if is_bullish else 10) + wetter_bonus
            
            # Aktionslogik: Handelsempfehlung basierend auf Wahrscheinlichkeit
            if prob >= 75: action = "🔥 AGGRESSIV KAUFEN"
            elif prob >= 60: action = "✅ POSITION HALTEN"
            else: action = "🛑 ABWARTEN"

            results.append({
                "Name": name, "Typ": "CALL 🟢" if is_bullish else "PUT 🔴",
                "Wahrscheinlichkeit": f"{min(prob, 99)}%",
                "Aktion": action, "Kurs": round(cp, 2),
                "Ziel %": f"{abs(((cp*1.05)-cp)/cp)*100:.2f}%" # Beispiel-Ziel
            })
        except: continue
    return results

# --- 5. DASHBOARD LAYOUT ---
indices = {"^GDAXI": "DAX", "^IXIC": "NASDAQ"}
stocks = {"ADS.DE": "Adidas", "SAP.DE": "SAP", "NVDA": "Nvidia", "RHM.DE": "Rheinmetall"}

st.subheader("📊 Markt-Check & Aktionslogik")
idx_data = get_analysis(indices, intervall)
if idx_data:
    st.table(pd.DataFrame(idx_data))

if st.button("🚀 Großen Aktien-Scan starten"):
    st.session_state.stock_res = get_analysis(stocks, intervall)

if 'stock_res' in st.session_state:
    df = pd.DataFrame(st.session_state.stock_res)
    col_l, col_r = st.columns(2)
    with col_l:
        st.success(f"Top {top_n} CALLS")
        st.dataframe(df[df['Typ'] == "CALL 🟢"].head(top_n))
    with col_r:
        st.error(f"Top {top_n} PUTS")
        st.dataframe(df[df['Typ'] == "PUT 🔴"].head(top_n))
_KEY" # Hier eigenen Key einfügen
CITY = "Frankfurt" # Leitbörse für DAX

def get_weather(city):
    try:
        url = f"http://api.openweathermap.org{city}&appid={API_KEY}&units=metric&lang=de"
        data = requests.get(url).json()
        return {
            "temp": data['main']['temp'],
            "desc": data['weather'][0]['description'],
            "icon": data['weather'][0]['icon'],
            "main": data['weather'][0]['main'] # e.g. 'Clear', 'Rain'
        }
    except: return None

# --- 2. HEADER & WETTER ANZEIGE ---
weather = get_weather(CITY)
col_t1, col_t2 = st.columns([3, 1])
with col_t1:
    st.title("🚀 Trading-Monitor 2026")
with col_t2:
    if weather:
        st.markdown(f"**Börsenwetter ({CITY}):** {weather['temp']}°C, {weather['desc']}")
        # Wetter-Logik: Sonne = Bullisch (+5%), Regen = Vorsicht (-5%)
        wetter_bonus = 5 if weather['main'] in ['Clear', 'Clouds'] else -5
    else:
        wetter_bonus = 0
        st.caption("Wetterdaten nicht verfügbar")

# --- 3. SIDEBAR ---
st.sidebar.header("Konfiguration")
risiko_eur = st.sidebar.number_input("Risiko pro Trade (EUR)", value=500)
intervall = st.sidebar.selectbox("Intervall", ["1d", "1h", "15m", "5m"], index=0)
top_n = st.sidebar.slider("Top-Signale", 1, 10, 5)

# --- 4. ANALYSE-LOGIK MIT AKTIONS-FILTER ---
def get_analysis(ticker_dict, timeframe):
    results = []
    for symbol, name in ticker_dict.items():
        try:
            t = yf.Ticker(symbol)
            hist = t.history(period="60d", interval=timeframe)
            if len(hist) < 20: continue
            
            cp = hist['Close'].iloc[-1]
            sma20 = hist['Close'].rolling(20).mean().iloc[-1]
            is_bullish = cp > sma20
            
            # Basis-Wahrscheinlichkeit + Wetter-Einfluss
            prob = 50 + (20 if is_bullish else 10) + wetter_bonus
            
            # Aktionslogik: Handelsempfehlung basierend auf Wahrscheinlichkeit
            if prob >= 75: action = "🔥 AGGRESSIV KAUFEN"
            elif prob >= 60: action = "✅ POSITION HALTEN"
            else: action = "🛑 ABWARTEN"

            results.append({
                "Name": name, "Typ": "CALL 🟢" if is_bullish else "PUT 🔴",
                "Wahrscheinlichkeit": f"{min(prob, 99)}%",
                "Aktion": action, "Kurs": round(cp, 2),
                "Ziel %": f"{abs(((cp*1.05)-cp)/cp)*100:.2f}%" # Beispiel-Ziel
            })
        except: continue
    return results

# --- 5. DASHBOARD LAYOUT ---
indices = {"^GDAXI": "DAX", "^IXIC": "NASDAQ"}
stocks = {"ADS.DE": "Adidas", "SAP.DE": "SAP", "NVDA": "Nvidia", "RHM.DE": "Rheinmetall"}

st.subheader("📊 Markt-Check & Aktionslogik")
idx_data = get_analysis(indices, intervall)
if idx_data:
    st.table(pd.DataFrame(idx_data))

if st.button("🚀 Großen Aktien-Scan starten"):
    st.session_state.stock_res = get_analysis(stocks, intervall)

if 'stock_res' in st.session_state:
    df = pd.DataFrame(st.session_state.stock_res)
    col_l, col_r = st.columns(2)
    with col_l:
        st.success(f"Top {top_n} CALLS")
        st.dataframe(df[df['Typ'] == "CALL 🟢"].head(top_n))
    with col_r:
        st.error(f"Top {top_n} PUTS")
        st.dataframe(df[df['Typ'] == "PUT 🔴"].head(top_n))
