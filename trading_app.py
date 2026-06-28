import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

# ==========================================
# 1. SETUP & TICKER-ERWEITERUNG
# ==========================================
st.set_page_config(page_title="Börsen Wetter", layout="wide")
st.title("🌦️ Börsen Wetter & Trading Dashboard")

# Erweiterte Konfiguration
TICKER_DICTS = {
    "Indizes": {
        "DAX": "^GDAXI", 
        "Nasdaq 100": "^NDX", 
        "S&P 500": "^GSPC"
    },
    "Währungen": {
        "EUR/USD": "EURUSD=X"
    },
    "Osteuropa": {
        "OTP Bank": "OTP.BU", 
        "MOL": "MOL.BU"
    }
}

# ==========================================
# 2. LOGIK & TYP-KONVERTIERUNG
# ==========================================

def get_clean_float(val):
    """Erzwingt saubere Python-Floats."""
    try:
        return float(val)
    except:
        return 0.0

def load_data(ticker):
    # Zeitraum auf 1y für saubere Indikatoren
    data = yf.download(ticker, period="1y")
    if data.empty: return pd.DataFrame()
    
    df = pd.DataFrame(index=data.index)
    # yfinance liefert manchmal Tuples bei MultiIndex, wir extrahieren den ersten 'Close'
    if isinstance(data.columns, pd.MultiIndex):
        df["Close"] = data.iloc[:, 0].astype(float)
    else:
        df["Close"] = data["Close"].astype(float)
    
    # RSI Berechnung
    delta = df["Close"].diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = -delta.where(delta < 0, 0).rolling(14).mean()
    rs = gain / (loss + 1e-9)
    df["RSI"] = (100 - (100 / (1 + rs))).fillna(50.0).astype(float)
    return df

# ==========================================
# 3. DASHBOARD (TYP-SICHER)
# ==========================================
cat = st.sidebar.selectbox("Kategorie", list(TICKER_DICTS.keys()))
tick = st.sidebar.selectbox("Asset", list(TICKER_DICTS[cat].keys()))
df = load_data(TICKER_DICTS[cat][tick])

if not df.empty:
    curr = get_clean_float(df["Close"].iloc[-1])
    prev = get_clean_float(df["Close"].iloc[-2])
    chg = ((curr - prev) / prev) * 100
    
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.write(f"### {tick} Kurs")
        st.markdown(f"## {curr:,.4f}") # 4 Nachkommastellen für FX
        st.write(f"Veränderung: {chg:+.2f}%")
        
    with c2:
        st.write("### Fear & Greed (RSI)")
        val = get_clean_float(df["RSI"].iloc[-1])
        st.markdown(f"## {val:.1f} %")
        # Visualisierungshilfe für RSI-Verständnis
        if val > 70: st.warning("Überkauft")
        elif val < 30: st.success("Überverkauft")
        
    with c3:
        st.write("### Status")
        st.info("System bereit")

    fig = go.Figure(go.Scatter(x=df.index[-60:], y=df["Close"].iloc[-60:]))
    fig.update_layout(template="plotly_dark", title=f"Chartverlauf: {tick}")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("Daten konnten nicht geladen werden.")
