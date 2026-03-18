import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- 1. SYSTEM-INFO (Versionsnummern) ---
st.sidebar.text(f"Streamlit: {st.__version__}")
st.sidebar.text(f"Yfinance: {yf.__version__}")
st.sidebar.text(f"Pandas: {pd.__version__}")

# --- 2. DATEN-FUNKTION (Mit Cache gegen Warteschleife) ---
@st.cache_data(ttl=600)
def get_data(ticker, interval="1d", period="60d"):
    try:
        # Timeout verhindert endloses Laden
        data = yf.download(ticker, period=period, interval=interval, progress=False, timeout=10)
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        return data
    except:
        return pd.DataFrame()

# --- 3. SEKTION 1: MARKT-FRAMEWORK (Untereinander) ---
st.header("1. Globales Markt-Framework")

SYMBOLS = {
    "EUR/USD": "EURUSD=X", "EUR/RUB": "EURRUB=X", 
    "DAX Index": "^GDAXI", "EuroStoxx 50": "^STOXX50E", 
    "Nifty 50": "^NSEI", "BIST 100": "XU100.IS"
}

for name, ticker in SYMBOLS.items():
    df = get_data(ticker, period="5d")
    if not df.empty and len(df) >= 2:
        last = float(df['Close'].iloc[-1])
        prev = float(df['Close'].iloc[-2])
        chg = ((last / prev) - 1) * 100
        
        # LOGIK: Währungen 5 Stellen, Indizes 2 Stellen
        fmt = ".5f" if "/" in name else ".2f"
        
        st.write(f"**{name}**")
        st.write(f"Kurs: {last:{fmt}} | Änderung: {chg:+.2f}%")
        st.divider()

# --- 4. SEKTION 2: H4 MOMENTUM & TOP 7 AKTIEN ---
st.header("2. H4 Momentum Analyse")

TOP_STOCKS = {
    "DAX": ["SAP.DE", "SIE.DE", "ALV.DE", "DTE.DE", "AIR.DE", "BMW.DE", "MBG.DE"],
    "NASDAQ": ["AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "TSLA"],
    "EuroStoxx": ["ASML.AS", "MC.PA", "OR.PA", "SAP.DE", "LIN.DE", "TTE.PA", "SAN.MC"],
    "BIST100": ["THYAO.IS", "ASELS.IS", "KCHOL.IS", "EREGL.IS", "TUPRS.IS", "SISE.IS", "AKBNK.IS"],
    "Nifty": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", "HINDUNILVR.NS", "SBIN.NS"]
}

idx_sel = st.selectbox("Index wählen:", list(TOP_STOCKS.keys()))
stock_sel = st.selectbox("Aktie wählen:", TOP_STOCKS[idx_sel])

if stock_sel:
    # --- H4 LOGIK ---
    # Laden der 4-Stunden-Daten (Yahoo erlaubt max 60 Tage für 4h)
    h4_data = get_data(stock_sel, interval="4h", period="60d")
    
    if not h4_data.empty and len(h4_data) > 14:
        # Momentum Berechnung: Aktueller Preis minus Preis vor 14 Perioden (H4)
        h4_data['Momentum'] = h4_data['Close'] - h4_data['Close'].shift(14)
        curr_price = float(h4_data['Close'].iloc[-1])
        curr_mom = float(h4_data['Momentum'].iloc[-1])

        st.write(f"**Analyse: {stock_sel}**")
        st.write(f"Aktueller Kurs: {curr_price:.2f}")
        st.write(f"H4 Momentum (14 Perioden): {curr_mom:+.2f}")
        
        # Charts untereinander
        st.line_chart(h4_data['Close'])
        st.area_chart(h4_data['Momentum'])

        # --- MONTE CARLO ---
        st.subheader("Monte Carlo Ausarbeitung (30 Tage)")
        returns = h4_data['Close'].pct_change().dropna()
        
        plt.figure(figsize=(10, 4))
        sim_ends = []
        for _ in range(100):
            prices = [curr_price]
            for _ in range(30):
                prices.append(prices[-1] * (1 + np.random.normal(0, returns.std())))
            plt.plot(prices, color='gray', alpha=0.1)
            sim_ends.append(prices[-1])
        
        plt.title(f"Simulationspfade {stock_sel}")
        st.pyplot(plt)
        
        st.write(f"Erwarteter Kurs (Mittelwert): {np.mean(sim_ends):.2f}")
        st.write(f"Chance auf Steigerung: {(np.array(sim_ends) > curr_price).mean()*100:.1f}%")
