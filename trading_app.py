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

# --- WETTER FUNKTION (Wien) ---
def get_weather():
    try:
        # Wetterdaten für Wien abrufen (Österreich-Kontext)
        url = "https://api.open-meteo.com/v1/forecast?latitude=48.2085&longitude=16.3721&current_weather=true"
        response = requests.get(url).json()
        temp = response['current_weather']['temperature']
        return f"{temp}°C"
    except:
        return "--°C"

# --- DATEN FUNKTION MIT AKTIVER BERECHNUNG ---
@st.cache_data(ttl=60)
def get_market_data(symbol):
    try:
        ticker = yf.Ticker(symbol)
        # 1-Jahres-Zeitraum für die 52-Wochen-Berechnung
        hist = ticker.history(period="1y")
        if hist.empty:
            return {"Preis": 0, "Pos%": 0, "Status": "N/A", "Trend": "⚪"}
        
        current_price = hist['Close'].iloc[-1]
        low_52w = hist['Low'].min()
        high_52w = hist['High'].max()
        
        # Aktive Berechnung der Position im 52-Wochen-Kanal
        pos_percent = ((current_price - low_52w) / (high_52w - low_52w)) * 100
        
        # Deine 10/90 Regel Definition
        if pos_percent < 10:
            status = "EXTREM TIEF"
            trend = "🔴"
        elif pos_percent > 90:
            status = "EXTREM HOCH"
            trend = "🟢"
        else:
            status = "NORMAL"
            trend = "🟡"
            
        return {
