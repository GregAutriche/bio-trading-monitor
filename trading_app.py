import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh

# --- 1. KONFIGURATION ---
st.set_page_config(page_title="Bio-Trading Monitor Live PRO", layout="wide")
st_autorefresh(interval=60000, limit=1000, key="fscounter")

# --- 2. TICKER-NAMEN MAPPING (VOLLSTÄNDIG FÜR EUROSTOXX & CO) ---
TICKER_NAMES = {
    "EURUSD=X": "EUR/USD", "EURRUB=X": "EUR/RUB", "^GDAXI": "DAX 40", "^STOXX50E": "EuroStoxx 50",
    "^NDX": "NASDAQ 100", "XU100.IS": "BIST 100", "^NSEI": "Nifty 50",
    # EuroStoxx 50 & DAX Mix
    "AIR.PA": "Airbus", "MC.PA": "LVMH", "OR.PA": "L'Oréal", "ASML.AS": "ASML", 
    "SAP.DE": "SAP", "SIE.DE": "Siemens", "ALV.DE": "Allianz", "DTE.DE": "Telekom",
    "ADS.DE": "Adidas", "BMW.DE": "BMW", "BAYN.DE": "Bayer", "BAS.DE": "BASF",
    "SAN.PA": "Sanofi", "BNP.PA": "BNP Paribas", "TTE.PA": "TotalEnergies", "ITX.MC": "Inditex",
    "AAPL": "Apple", "NVDA": "Nvidia", "TSLA": "Tesla", "MSFT": "Microsoft",
    "THYAO.IS": "Turkish Airlines", "RELIANCE.NS": "Reliance Ind."
}

TICKER_GROUPS = {
    "DAX 40 (DE)": ["SAP.DE", "SIE.DE", "ALV.DE", "DTE.DE", "ADS.DE", "BMW.DE", "BAYN.DE", "BAS.DE"],
    "EuroStoxx 50 (EU)": ["AIR.PA", "MC.PA", "OR.PA", "ASML.AS", "SAN.PA", "BNP.PA", "TTE.PA", "ITX.MC"],
    "NASDAQ 100 (US)": ["AAPL", "NVDA", "TSLA", "MSFT"],
    "BIST 100 (TR)": ["THYAO.IS"],
    "Nifty 50 (IN)": ["RELIANCE.NS"]
}

# --- 3. DESIGN ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #E0E0E0; }
    .market-card { background: rgba(255,255,255,0.03); border-radius: 10px; padding: 12px; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 10px; }
    .metric-value { font-size: 1.1rem; font-weight: bold; font-family: 'Courier New', monospace; color: white; }
    .bullish { color: #00FFA3; font-weight: bold; }
    .bearish { color: #FF4B4B; font-weight: bold; }
    .header-box { background: rgba(30,144,255,0.1); padding: 15px; border-radius: 10px; border: 1px solid #1E90FF; text-align: center; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. NEUE SCANNER-FUNKTION ---
def run_market_scanner(ticker_list):
    results = []
    for t in ticker_list:
        df = get_data(t, period="5d")
        if not df.empty:
            last = float(df['Close'].iloc[-1])
            prev = float(df['Close'].iloc[-2])
            chg = ((last / prev) - 1) * 100
            # Wir nutzen den RSI als Indikator für den Scanner
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rsi = 100 - (100 / (1 + (gain / loss))).iloc[-1]
            
            results.append({
                "Aktie": TICKER_NAMES.get(t, t),
                "Kurs": f"{last:,.2f}",
                "Trend %": round(chg, 2),
                "RSI": round(rsi, 1)
            })
    return pd.DataFrame(results)

# --- 6. DEEP-DIVE & SCANNER BEREICH ---
st.divider()
ca, cb = st.columns(2)
market_sel = ca.selectbox("Markt für Scanner wählen:", list(TICKER_GROUPS.keys()))

# Wir führen den Scan für den gesamten Index aus
with st.spinner(f"Scanne {market_sel}..."):
    scan_results = run_market_scanner(TICKER_GROUPS[market_sel])

cl, cr = st.columns([1.2, 1])

with cl:
    st.subheader("🔮 Markt-Visualisierung")
    # (Dein bisheriger Monte-Carlo Chart Code für einen ausgewählten Einzelwert hier)
    # ...

with cr:
    st.subheader(f"🎯 Top 5 Scanner: {market_sel}")
    
    # TOP CALLS: Aktien mit starkem Aufwärtsmoment (Hoher Trend, moderater RSI)
    st.markdown("<span class='bullish'>🟢 TOP 5 CALL-SIGNALE (Bullish)</span>", unsafe_allow_html=True)
    top_calls = scan_results.sort_values(by="Trend %", ascending=False).head(5)
    st.table(top_calls[["Aktie", "Kurs", "Trend %"]])
    
    st.write("") # Abstand
    
    # TOP PUTS: Aktien mit Schwäche oder Überhitzung (Niedriger Trend)
    st.markdown("<span class='bearish'>🔴 TOP 5 PUT-SIGNALE (Bearish)</span>", unsafe_allow_html=True)
    top_puts = scan_results.sort_values(by="Trend %", ascending=True).head(5)
    st.table(top_puts[["Aktie", "Kurs", "Trend %"]])
