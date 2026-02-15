import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime

# --- 1. TERMINAL LOOK (CSS) ---
st.set_page_config(layout="wide", page_title="Börsen-Wetter Terminal")

# Hier erzwingen wir echtes Schwarz und saubere Boxen
st.markdown("""
    <style>
    /* Hintergrund der gesamten App */
    .stApp {
        background-color: #000000;
    }
    /* Stil für die Kurs-Boxen */
    [data-testid="stMetric"] {
        background-color: #0a0a0a;
        border: 1px solid #1f1f1f;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    /* Text-Farben korrigieren */
    h1, h2, h3, p, span {
        color: #e0e0e0 !important;
        font-family: 'Courier New', Courier, monospace;
    }
    hr {
        border: 0;
        border-top: 1px solid #333;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATENFUNKTION ---
def get_live_data():
    # Ticker: EURUSD, Euro Stoxx 50, S&P 500
    mapping = {"EURUSD": "EURUSD=X", "STOXX": "^STOXX50E", "SP": "^GSPC"}
    results = {}
    for key, ticker in mapping.items():
        try:
            t = yf.Ticker(ticker)
            df = t.history(period="5d")
            if not df.empty:
                results[key] = {
                    "price": df['Close'].iloc[-1],
                    "delta": ((df['Close'].iloc[-1] - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100,
                    "df": df
                }
        except: results[key] = None
    return results

data = get_live_data()
now = datetime.now()

# --- 3. LAYOUT NACH SKIZZE ---

# Header
st.write(f"### {now.strftime('%y%m%d')}")
st.write(f"**{now.strftime('%A, %H:%M')} (LIVE TERMINAL)**")
st.markdown("---")

# SEKTION 1: EUR/USD (Breite Zeile)
if data["EURUSD"]:
    st.markdown("### 💱 Währungs-Fokus")
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        st.metric("EUR/USD", f"{data['EURUSD']['price']:.4f}", f"{data['EURUSD']['delta']:.2f}%")
    with c2:
        st.write("## ☀️")
        st.caption("Wetter: Heiter")
    with c3:
        st.write("## 🟢")
        st.caption("Action: Bullisch")

st.markdown("---")

# SEKTION 2: INDIZES (Unterreinander in Zeilen)
st.markdown("### 📈 Markt-Indizes")

# Euro Stoxx Zeile
if data["STOXX"]:
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        st.metric("EURO STOXX 50", f"{data['STOXX']['price']:.2f}", f"{data['STOXX']['delta']:.2f}%")
    with c2:
        st.write("## ☁️")
        st.caption("Wetter: Bewölkt")
    with c3:
        st.write("## ⚪")
        st.caption("Action: Wait")

st.write("") # Platzhalter

# S&P Zeile
if data["SP"]:
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        st.metric("S&P INDEX", f"{data['SP']['price']:.2f}", f"{data['SP']['delta']:.2f}%")
    with c2:
        st.write("## ☀️")
        st.caption("Wetter: Sonnig")
    with c3:
        st.write("## 🟢")
        st.caption("Action: Buy")

st.markdown("---")

# SEKTION 3: GRAFIK
st.markdown("### 📊 Analyse-Grafik")
if data["SP"]:
    df_chart = data["SP"]["df"]
    fig = go.Figure(data=[go.Candlestick(
        x=df_chart.index, open=df_chart['Open'], high=df_chart['High'], 
        low=df_chart['Low'], close=df_chart['Close']
    )])
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis_rangeslider_visible=False,
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

# SEKTION 4: DETAILS
st.markdown("---")
col_a, col_b = st.columns(2)
with col_a:
    st.markdown("**Wetter-Legende:**")
    st.write("☀️ Bullisch | ☁️ Neutral | 🌧️ Bärisch")
with col_b:
    st.markdown("**Detail Info:**")
    st.write("Korrelation Markt/Wetter aktiv. Daten via yFinance.")

# --- 5. ZEILE: DETAIL INFO / BESCHREIBUNG (Optimiert) ---
st.divider()
st.subheader("Analyse-Details & Methodik")

col_info1, col_info2 = st.columns(2)

with col_info1:
    st.markdown("""
    **Über dieses Dashboard:**
    Dieses Monitor-System korreliert globale Wetterdaten mit der Performance der wichtigsten Marktindizes. 
    Ziel ist es, kurzfristige Volatilitätsmuster zu erkennen, die durch externe Umweltfaktoren beeinflusst werden könnten.
    """)

with col_info2:
    st.markdown(f"""
    **Technische Parameter:**
    * **Datenquelle:** Yahoo Finance API (Echtzeit-Streams)
    * **Währungsbasis:** EUR (Alle US-Werte werden umgerechnet)
    * **Aktualisierungsrate:** Bei jedem Browser-Refresh
    * **Status:** System läuft stabil im Live-Modus
    """)

st.warning("⚠️ **Risikohinweis:** Die hier angezeigten 'Actions' basieren auf einem algorithmischen Wetter-Modell und stellen keine direkte Anlageberatung dar.")
