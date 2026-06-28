import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

# ==========================================
# 1. SETUP
# ==========================================
st.set_page_config(page_title="Börsen Wetter", layout="wide")
st.title("🌦️ Börsen Wetter Dashboard")

TICKER_DICTS = {
    "Indizes": {"DAX": "^GDAXI", "Nasdaq": "^NDX", "S&P 500": "^GSPC"},
    "Osteuropa": {"OTP Bank": "OTP.BU", "MOL": "MOL.BU", "Sopharma": "SOPH.SO"}
}

# ==========================================
# 2. LOGIK & TYP-KONVERTIERUNG
# ==========================================

def get_clean_float(val):
    """Erzwingt einen sauberen Python-Float ohne NumPy-Altlasten."""
    return float(val) if not np.isnan(val) else 0.0

def load_data(ticker):
    data = yf.download(ticker, period="1y")
    if data.empty: return pd.DataFrame()
    
    # Sicherstellen, dass die Spalten nackte Floats sind
    df = pd.DataFrame(index=data.index)
    df["Close"] = data["Close"].squeeze().astype(float)
    
    # RSI
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
    # Hier erzwingen wir die Konvertierung in native Python-Typen
    curr = get_clean_float(df["Close"].iloc[-1])
    prev = get_clean_float(df["Close"].iloc[-2])
    chg = ((curr - prev) / prev) * 100
    
    # UI-Ausgabe OHNE st.metric, um jeglichen Typ-Fehler zu vermeiden
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.write("### Aktueller Kurs")
        st.markdown(f"## {curr:,.2f}")
        st.write(f"Veränderung: {chg:+.2f}%")
        
    with c2:
        st.write("### Fear & Greed (RSI)")
        val = get_clean_float(df["RSI"].iloc[-1])
        st.markdown(f"## {val:.1f} %")
        
    with c3:
        st.write("### Status")
        st.info("System stabil")

    # Plot
    fig = go.Figure(go.Scatter(x=df.index[-50:], y=df["Close"].iloc[-50:]))
    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("Datenfehler.")
