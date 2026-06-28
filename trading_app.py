import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

# ==========================================
# 1. KONFIGURATION & SETUP
# ==========================================
st.set_page_config(page_title="Börsen Wetter", layout="wide")
st.title("🌦️ Börsen Wetter & Trading Dashboard")

# Ticker-Konfiguration inkl. NASDAQ & EUR/USD
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
# 2. HILFSFUNKTIONEN (TYP-SICHER)
# ==========================================

def get_clean_float(val):
    """Wandelt Werte sicher in native Python-Floats um."""
    try:
        return float(val)
    except (ValueError, TypeError):
        return 0.0

@st.cache_data(ttl=600)
def load_data(ticker):
    """Lädt Daten und bereinigt sie für die UI."""
    data = yf.download(ticker, period="1y", interval="1d")
    if data.empty: return pd.DataFrame()
    
    # DataFrame-Bereinigung
    df = pd.DataFrame(index=data.index)
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
# 3. DASHBOARD RENDERING
# ==========================================
cat = st.sidebar.selectbox("Kategorie", list(TICKER_DICTS.keys()))
tick_name = st.sidebar.selectbox("Asset", list(TICKER_DICTS[cat].keys()))
ticker_symbol = TICKER_DICTS[cat][tick_name]

df = load_data(ticker_symbol)

if not df.empty:
    # Daten-Extrahierung als native Python-Floats
    curr = get_clean_float(df["Close"].iloc[-1])
    prev = get_clean_float(df["Close"].iloc[-2])
    chg = ((curr - prev) / prev) * 100
    rsi = get_clean_float(df["RSI"].iloc[-1])
    
    # Header-Metriken (Stabiler Ersatz für st.metric)
    c1, c2, c3 = st.columns(3)
    c1.subheader(f"Kurs {tick_name}")
    c1.markdown(f"## {curr:,.4f}")
    c1.write(f"Veränderung: {chg:+.2f}%")
    
    c2.subheader("Fear & Greed (RSI)")
    c2.markdown(f"## {rsi:.1f} %")
    c2.write("Indikator: RSI & SMA")
    
    c3.subheader("Status")
    c3.info(f"System bereit für {tick_name}")
    
    # Chart-Visualisierung
    fig = go.Figure(go.Scatter(x=df.index[-60:], y=df["Close"].iloc[-60:], line=dict(color='#00CC96')))
    fig.update_layout(template="plotly_dark", title=f"Historie: {tick_name}")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error(f"Daten für {tick_name} konnten nicht geladen werden.")

# ==========================================
# 4. HINWEISE ZUR VERBESSERUNG
# ==========================================
st.markdown("---")
st.write("💡 **Tipps zur Verbesserung:**")
st.markdown("* **Backups:** Denke daran, isometrisches Training (Wandsitz) und Ernährungstipps (Rote Bete, Sprossen) zur Blutdrucksenkung im Blick zu behalten.")
st.markdown("* **Überwachung:** Achte bei der Analyse von Währungen auf das Zusammenspiel mit Leitzinsentscheidungen.")
