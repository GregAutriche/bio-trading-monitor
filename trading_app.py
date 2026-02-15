import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime

# --- 1. TERMINAL LOOK (CSS) ---
st.set_page_config(layout="wide", page_title="Terminal")
st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    [data-testid="stMetric"] {
        background-color: #0a0a0a;
        border: 1px solid #1f1f1f;
        padding: 15px;
        border-radius: 10px;
    }
    h1, h2, h3, p, span, label {
        color: #e0e0e0 !important;
        font-family: 'Courier New', Courier, monospace;
    }
    hr { border-top: 1px solid #333; }
    /* Entfernt Standard-Abstände für kompaktere Darstellung */
    .stMarkdown div p { margin-bottom: 0px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATENFUNKTION ---
def get_live_data():
    # Anpassung auf STOXX 50 (^STOXX50E) und S&P 250 (^SP1000)
    mapping = {"EURUSD": "EURUSD=X", "^EUROst_50": "^STOXX50E", "SP": "^GSPC"}
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

# --- 3. FUNKTIONEN (Das Layout der Zeilen) ---
def compact_row(label, weather_icon, weather_text, signal_icon, signal_text, price, delta):
    """Erzeugt eine Zeile: Label | Wetter | Aktion | Preis & Delta"""
    cols = st.columns([2, 1, 1.5, 1, 1.5, 2, 2])
    with cols[0]:
        st.write(f"**{label}**")
    with cols[1]:
        st.write(weather_icon)
    with cols[2]:
        st.write(weather_text)
    with cols[3]:
        st.write(signal_icon)
    with cols[4]:
        st.write(signal_text)
    with cols[5]:
        st.write(f"**{price}**")
    with cols[6]:
        color = "green" if "+" in delta else "red"
        st.markdown(f"<span style='color:{color}'>{delta}</span>", unsafe_allow_html=True)

# --- 2. DATEN-SIMULATION / LADEN ---
# (Hier steht normalerweise dein yfinance-Code. Ich nutze dein 'data' Objekt)
now = datetime.now()

# --- 3. SEITEN-KONFIGURATION ---
st.set_page_config(layout="wide", page_title="Börsen-Wetter Terminal")

# --- 4. HEADER ---
header_col1, header_col2 = st.columns([2, 1])

with header_col1:
    st.title("☁️ Börsen-Wetter Terminal")

with header_col2:
    # Rechtsbündige Anzeige von Datum und Uhrzeit
    st.markdown(f"""
        <div style="text-align: right; padding-right: 20px;">
            <div style="font-size: 24px; font-weight: bold; font-family: monospace;">
                {now.strftime('%d.%m.%Y')}
            </div>
            <div style="font-size: 16px; font-family: monospace; opacity: 0.7;">
                {now.strftime('%H:%M')} LIVE TERMINAL
            </div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# --- 5. HAUPTBEREICH (Sektionen) ---

# --- WÄHRUNG ---
st.markdown("### 🌍 FOKUS/ Währung")
if data["EURUSD"]:
    compact_row("☀️", "Heiter","🟢", "Bull", "EUR/USD", f"{data['EURUSD']['price']:.5f}", f"{data['EURUSD']['delta']:.2f}%")
else:
    st.info("EUR/USD Daten momentan nicht verfügbar.")

st.markdown("---")

# --- MARKT-INDIZES ---
st.markdown("### 📈 FOKUS/ Markt-Indizes")

# EUROSTOXX
if data.get("STOXX") and data["STOXX"] is not None:
    compact_row(
        "EUROSTOXX", 
        "☁️", "Bewölkt", 
        "⚪", "Wait", 
        f"{data['STOXX']['price']:.2f}", 
        f"{data['STOXX']['delta']:.2f}%"
    )
else:
    st.info("EUROSTOXX: Keine Daten (Ticker prüfen oder Wochenende).")

st.write("") 

# S&P 1000
if data.get("SP") and data["SP"] is not None:
    compact_row(
        "S&P 1000", 
        "☀️", "Sonnig", 
        "🟢", "Buy", 
        f"{data['SP']['price']:.2f}", 
        f"{data['SP']['delta']:.2f}%"
    )
else:
    st.info("S&P 1000: Daten aktuell nicht verfügbar.")

st.markdown("---")

# --- AKTIEN ---
st.markdown("### 🍎 FOKUS/ Aktien-Analyse")

# Liste deiner Aktien (Beispielhaft)
tickers = [("APPLE", "AAPL"), ("MICROSOFT", "MSFT"), ("TESLA", "TSLA")]

for label, sym in tickers:
    if data.get(sym) and data[sym] is not None:
        compact_row(
            label, 
            "☀️", "Sonnig", 
            "🟢", "Buy", 
            f"{data[sym]['price']:.2f}", 
            f"{data[sym]['delta']:.2f}%"
        )
    else:
        st.write(f"ℹ️ {label}: Daten werden geladen...")

st.markdown("---")










