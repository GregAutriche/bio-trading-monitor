import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh

# --- 1. KONFIGURATION ---
st.set_page_config(page_title="Bio-Trading Monitor Live PRO", layout="wide")
st_autorefresh(interval=60000, limit=1000, key="fscounter")

# --- 2. TICKER-MAPPING ---
TICKER_NAMES = {
    "EURUSD=X": "EUR/USD", "EURRUB=X": "EUR/RUB", "^GDAXI": "DAX 40", "^STOXX50E": "EuroStoxx 50",
    "^NDX": "NASDAQ 100", "XU100.IS": "BIST 100", "^NSEI": "Nifty 50",
    "AD.AS": "Ahold Delhaize", "ADS.DE": "Adidas", "AIR.PA": "Airbus", "ALV.DE": "Allianz", "ASML.AS": "ASML",
    "BAS.DE": "BASF", "BAYN.DE": "Bayer", "BMW.DE": "BMW", "DHL.DE": "DHL Group", "DTE.DE": "Telekom",
    "AAPL": "Apple", "MSFT": "Microsoft", "NVDA": "Nvidia", "AMD": "AMD", "NFLX": "Netflix", "RHM.DE": "Rheinmetall"
}

TICKER_GROUPS = {
    "EuroStoxx 50 (EU)": ["AD.AS", "ADS.DE", "AIR.PA", "ALV.DE", "ASML.AS", "BAS.DE", "BAYN.DE", "BMW.DE", "DHL.DE", "DTE.DE"],
    "DAX 40 (DE)": [k for k in TICKER_NAMES.keys() if k.endswith(".DE")],
    "NASDAQ 100 (US)": ["AAPL", "MSFT", "NVDA", "NFLX", "AMD"]
}

# --- 3. DESIGN ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #E0E0E0; }
    .header-box { padding: 15px; border-radius: 12px; text-align: center; margin-bottom: 25px; border: 1px solid #1E90FF; background: rgba(30,144,255,0.05); }
    .vol-container { background: rgba(255,255,255,0.03); padding: 20px; border-radius: 10px; border: 1px solid #333; margin-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FUNKTIONEN ---
@st.cache_data(ttl=60)
def get_data(ticker, period="60d", interval="4h"):
    try:
        d = yf.download(ticker, period=period, interval=interval, progress=False)
        if isinstance(d.columns, pd.MultiIndex):
            d.columns = d.columns.get_level_values(0)
        return d
    except:
        return pd.DataFrame()

def extract_price(df, idx):
    try:
        if df.empty: return 0.0
        val = df['Close'].iloc[idx]
        return float(val)
    except:
        return 0.0

# --- 5. AUFBAU ---
st.title("🚀 Bio-Trading Monitor Live PRO")

cs1, cs2 = st.columns(2)
sel_market = cs1.selectbox("Markt wählen:", list(TICKER_GROUPS.keys()))
sorted_stocks = sorted(TICKER_GROUPS[sel_market], key=lambda x: TICKER_NAMES.get(x, x))
sel_stock = cs2.selectbox("Aktie wählen:", sorted_stocks, format_func=lambda x: TICKER_NAMES.get(x, x))

    # --- VOLUMENSINFO DER LETZTEN 20 TAGE (CA. 120 KERZEN À 4H) ---
    st.divider()
    st.subheader("📊 Volumens-Analyse (Letzte 20 Handelstage)")

    # 1. Datenaufbereitung
    # Da das Intervall 4h ist, entsprechen 20 Handelstage ca. 120 Datenpunkten (6 pro Tag)
    vol_20d = d_s['Volume'].tail(120)
    avg_vol_20d = vol_20d.mean()
    max_vol_20d = vol_20d.max()
    
    # Vergleich aktuelles Volumen zu 20-Tage-Schnitt
    vol_20d_data = d_s['Volume'].tail(120)
    avg_vol_20d = vol_20d_data.mean()
    current_vol_final = float(d_s['Volume'].iloc[-1])
    
    # Abweichung zum 20-Tage-Schnitt
    v_diff_20d = ((current_vol_final / avg_vol_20d) - 1) * 100 if avg_vol_20d > 0 else 0

    # Anzeige in Spalten
    cv1, cv2, cv3 = st.columns(3)
    
    with cv1:
        st.metric("Aktuelles Volumen", f"{current_vol_final:,.0f}")
    with cv2:
        st.metric("Ø Volumen (20d)", f"{avg_vol_20d:,.0f}")
    with cv3:
        # Farbe je nach Stärke
        v_color = "normal" if abs(v_diff_20d) < 15 else "inverse"
        st.metric("Abweichung", f"{v_diff_20d:+.1f}%", delta_color=v_color)

    # Kleiner visueller Balken-Chart für die Bestätigung
    st.bar_chart(d_s['Volume'].tail(20)) # Zeigt die letzten 20 Datenpunkte grafisch

    # 2. Visualisierung (Balkendiagramm)
    # Wir zeigen die letzten 40 Perioden für eine bessere Übersichtlichkeit
    fig, ax = plt.subplots(figsize=(12, 3))
    fig.patch.set_facecolor('#0E1117')
    ax.set_facecolor('#0E1117')
    
    # Farben basierend auf Volumenstärke
    vol_colors = ['#00FFA3' if v > avg_vol_20d else '#1E90FF' for v in vol_20d.tail(40)]
    
    ax.bar(range(len(vol_20d.tail(40))), vol_20d.tail(40), color=vol_colors, alpha=0.8)
    ax.axhline(avg_20, color='#FF4B4B', linestyle='--', label="Ø 20 Tage")
    
    # Styling
    ax.set_title("Volumen-Verlauf (Letzte 40 Perioden)", color='white', fontsize=10)
    ax.tick_params(axis='both', colors='#8892b0', labelsize=8)
    for spine in ax.spines.values():
        spine.set_edgecolor('#333')
    
    st.pyplot(fig)


# FOOTER
st.info(f"🕒 Stand: {pd.Timestamp.now().strftime('%d.%m.%Y | %H:%M:%S')} | 📊 Analyse: 4h-Intervall")
