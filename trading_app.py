import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

# --- 1. CONFIG & TERMINAL LOOK (CSS) ---
st.set_page_config(layout="wide", page_title="Börsen-Wetter Terminal")

st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    h1, h2, h3, p, span, label, div {
        color: #e0e0e0 !important;
        font-family: 'Courier New', Courier, monospace;
    }
    [data-testid="stMetricValue"] { 
        font-size: 32px !important; 
        color: #ffffff !important; 
        font-weight: bold !important;
    }
    [data-testid="stMetricDelta"] { font-size: 20px !important; }
    hr { border-top: 1px solid #333; }
    
    /* Styling für den Expander */
    .streamlit-expanderHeader { 
        background-color: #111111 !important; 
        color: #00ff00 !important;
        border: 1px solid #333 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SESSION STATE (Startwerte fixieren) ---
if 'initial_values' not in st.session_state:
    st.session_state.initial_values = {}

# --- 3. DATENFUNKTION ---
def get_live_data():
    mapping = {
        "EURUSD": "EURUSD=X", 
        "STOXX": "^STOXX50E", 
        "SP": "^GSPC",
        "AAPL": "AAPL", 
        "MSFT": "MSFT"
    }
    results = {}
    for key, ticker in mapping.items():
        try:
            t = yf.Ticker(ticker)
            df = t.history(period="1d")
            if not df.empty:
                current_price = df['Close'].iloc[-1]
                
                # Startwert beim ersten Run speichern
                if key not in st.session_state.initial_values:
                    st.session_state.initial_values[key] = current_price
                
                start_price = st.session_state.initial_values[key]
                delta = ((current_price - start_price) / start_price) * 100
                
                results[key] = {
                    "price": current_price,
                    "delta": delta,
                    "start": start_price
                }
        except:
            results[key] = None
    return results

data = get_live_data()

# ZEITKORREKTUR: Korrektur um -1 Stunde (wegen Systemuhr-Fehler)
now = datetime.now() - timedelta(hours=-1)

# --- 4. LAYOUT FUNKTION ---
def compact_row(label, price, delta_val, format_str="{:.2f}"):
    cols = st.columns([2, 3])
    with cols[0]:
        st.write(f"*{label}*")
    with cols[1]:
        st.metric(label="Session-Kurs", value=format_str.format(price), delta=f"{delta_val:+.4f}%")

# --- 5. HEADER (Rechtsbündige Uhrzeit) ---
header_col1, header_col2 = st.columns([2, 1])

with header_col1:
    st.title("☁️ Börsen-Wetter")

with header_col2:
    st.markdown(f"""
        <div style="text-align: right; border-right: 4px solid #00ff00; padding-right: 15px;">
            <p style="margin:0; font-size: 14px; opacity: 0.6; color: #00ff00 !important;">LETZTES UPDATE (FIXED)</p>
            <p style="margin:0; font-size: 24px; font-weight: bold;">{now.strftime('%d.%m.%Y')}</p>
            <p style="margin:0; font-size: 18px; color: #00ff00 !important;">{now.strftime('%H:%M:%S')} LIVE</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# --- 6. ANZEIGE SEKTIONEN ---

# WÄHRUNG
st.markdown("### 🌍 FOKUS/ Währung")
if data.get("EURUSD"):
    compact_row("EUR/USD", data['EURUSD']['price'], data['EURUSD']['delta'], "{:.4f}")

st.markdown("---")

# MARKT-INDIZES
st.markdown("### 📈 FOKUS/ Markt-Indizes")
if data.get("STOXX"):
    compact_row("EUROSTOXX", data['STOXX']['price'], data['STOXX']['delta'])
if data.get("SP"):
    compact_row("S&P 500", data['SP']['price'], data['SP']['delta'])

# --- 7. DER AUFKLAPPBARE SLIDER & SESSION-INFO ---
st.write("")
with st.expander("🛠️ SESSION-ANALYSE & UPDATE-SLIDER"):
    st.subheader("Vergleich seit Session-Beginn")
    for key in ["EURUSD", "STOXX", "SP"]:
        if data.get(key):
            start_val = data[key]['start']
            current_val = data[key]['price']
            diff = current_val - start_val
            st.write(f"*{key}*: Start: {start_val:.4f} → Aktuell: {current_val:.4f} (Diff: {diff:+.4f})")
    
    st.markdown("---")
    # Der Slider für das Update-Intervall
    update_seconds = st.slider("Update-Intervall (Sekunden):", min_value=10, max_value=300, value=60, step=10)
    st.info(f"Nächstes Update in {update_seconds} Sekunden.")

st.markdown("---")

# AKTIEN
st.markdown("### 🍎 FOKUS/ Aktien-Analyse")
for label, sym in [("APPLE", "AAPL"), ("MICROSOFT", "MSFT")]:
    if data.get(sym):
        compact_row(label, data[sym]['price'], data[sym]['delta'])

# --- 8. AUTOMATISCHER REFRESH ---
time.sleep(update_seconds)
st.rerun()










