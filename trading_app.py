import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

# ==========================================
# 1. INITIALISIERUNG & SETUP
# ==========================================
st.set_page_config(
    page_title="Börsen Wetter Dashboard", page_icon="🌦️", layout="wide"
)
st.title("🌦️ Börsen Wetter & Trading Dashboard")

# Ticker-Konfiguration
TICKER_DICTS = {
    "Indizes / Champions": {
        "DAX": "^GDAXI",
        "Nasdaq 100": "^NDX",
        "S&P 500": "^GSPC",
        "Euro Stoxx 50": "^STOXX50E",
    },
    "Bulgarien & Ungarn": {
        "OTP Bank (Ungarn)": "OTP.BU",
        "MOL (Ungarn)": "MOL.BU",
        "Richter Gedeon (Ungarn)": "RICHT.BU",
        "Sopharma (Bulgarien)": "SOPH.SO",
        "Eurohold (Bulgarien)": "EUBG.SO",
    },
}

# ==========================================
# 2. ANALYTISCHE FUNKTIONEN (TYP-SICHER)
# ==========================================

def calculate_rsi(df, window=14):
    df = df.copy()
    if df is None or df.empty or "Close" not in df.columns:
        df["RSI"] = 50.0
        return df
    
    # Sicherstellen, dass Close ein Series-Objekt mit Float-Werten ist
    close_series = df["Close"].squeeze()
    if isinstance(close_series, pd.DataFrame):
        close_series = close_series.iloc[:, 0]
    
    delta = close_series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / (loss + 1e-9)
    df["RSI"] = 100 - (100 / (1 + rs))
    df["RSI"] = df["RSI"].fillna(50.0)
    return df

def calculate_custom_fear_greed(df):
    if df is None or df.empty or "Close" not in df.columns or len(df) < 200:
        return 50.0
    
    # Explizite Umwandlung in natives Python-Float
    rsi_val = float(df["RSI"].iloc[-1])
    current_close = float(df["Close"].iloc[-1])
    sma_200 = float(df["Close"].rolling(window=200).mean().iloc[-1])
    
    distance_pct = ((current_close - sma_200) / sma_200) * 100 if sma_200 != 0 else 0
    distance_score = np.clip((distance_pct + 15) / 30 * 100, 0, 100)
    
    fg_score = (rsi_val * 0.5) + (distance_score * 0.5)
    return float(np.clip(fg_score, 0, 100))

# ==========================================
# 3. DATENBESCHAFFUNG
# ==========================================

@st.cache_data(ttl=3600)
def load_market_data(ticker_symbol):
    try:
        data = yf.download(ticker_symbol, period="2y")
        if data.empty: return pd.DataFrame()
        
        # Flaches DataFrame erzwingen
        df = pd.DataFrame(index=data.index)
        if isinstance(data.columns, pd.MultiIndex):
            df["Close"] = data.iloc[:, 0]
        else:
            df["Close"] = data["Close"]
            
        df = calculate_rsi(df)
        return df.astype(float) # Alles in einfache Floats erzwingen
    except:
        return pd.DataFrame()

# ==========================================
# 4. DASHBOARD LOGIK
# ==========================================
category = st.sidebar.selectbox("Kategorie", list(TICKER_DICTS.keys()))
ticker = st.sidebar.selectbox("Asset", list(TICKER_DICTS[category].keys()))
df = load_market_data(TICKER_DICTS[category][ticker])

if not df.empty:
    current_price = float(df["Close"].iloc[-1])
    prev_price = float(df["Close"].iloc[-2])
    chg = ((current_price - prev_price) / prev_price) * 100
    fg_val = calculate_custom_fear_greed(df)
    
    col1, col2, col3 = st.columns(3)
    
    # Saubere, typ-sichere Ausgabe
    with col1:
        st.markdown(f"**Aktueller Kurs**")
        st.write(f"# {current_price:,.2f}")
        st.write(f"{chg:+.2f}%")
        
    with col2:
        st.markdown(f"**Fear & Greed**")
        st.write(f"# {fg_val:.1f} %")
        st.write("Indikator: RSI & SMA")
        
    # Chart (Plotly)
    st.plotly_chart(go.Figure(data=go.Scatter(x=df.index[-50:], y=df["Close"].iloc[-50:])), use_container_width=True)
else:
    st.error("Daten konnten nicht geladen werden.")
