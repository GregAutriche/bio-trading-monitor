import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import concurrent.futures

# --- 1. KONFIGURATION & ASSETS ---
st.set_page_config(page_title="Bio-Trading Monitor", layout="wide", page_icon="📈")

ASSETS = {
    "DE": {"^GDAXI": "DAX", "BAS.DE": "BASF", "SAP.DE": "SAP"},
    "US": {"^IXIC": "NASDAQ", "TSLA": "Tesla", "NVDA": "Nvidia"},
    "BIO": {"BNTX": "BioNTech", "VRTX": "Vertex", "MRNA": "Moderna"}
}

TICKER_TO_NAME = {ticker: name for region in ASSETS.values() for ticker, name in region.items()}
ALL_TICKERS = list(TICKER_TO_NAME.keys())

# --- 2. HILFSFUNKTIONEN ---
def safe_float(val):
    if isinstance(val, (pd.Series, np.ndarray, pd.DataFrame)):
        return float(val.iloc[-1]) if hasattr(val, 'iloc') else float(val[0])
    return float(val)

def get_logic_icons(chg):
    chg = safe_float(chg)
    weather = "☀️" if chg > 0.5 else "⛈️" if chg < -0.5 else "☁️"
    dot = "🟢" if chg > 0.4 else "🔵" if chg < -0.4 else "⚪"
    return weather, dot

@st.cache_data(ttl=300)
def get_live_data(ticker):
    try:
        df = yf.download(ticker, period="60d", interval="1d", progress=False)
        if df.empty or len(df) < 20: return None
        # Falls MultiIndex (neuere yfinance Version), Spalten flach machen
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df
    except: return None

def analyze_swing(ticker, df):
    cp = safe_float(df['Close'].iloc[-1])
    prev_3d = safe_float(df['Close'].iloc[-4])
    chg_3d = ((cp / prev_3d) - 1) * 100
    
    # ATR Berechnung
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = tr.rolling(14).mean().iloc[-1]
    
    # Trend & Volume
    sma20 = df['Close'].rolling(window=20).mean().iloc[-1]
    is_bullish = cp > sma20
    vol_ratio = df['Volume'].iloc[-1] / df['Volume'].tail(10).mean()
    
    weather, dot = get_logic_icons(chg_3d)
    chance = 50.0 + (15 if is_bullish else -10) + (min(abs(chg_3d) * 0.8, 25))
    
    return {
        "name": TICKER_TO_NAME.get(ticker, ticker),
        "cp": cp, "chg_3d": chg_3d, "atr": atr, 
        "weather": weather, "dot": dot, "chance": min(chance, 98),
        "vol_ratio": vol_ratio, "df": df
    }

# --- 3. PARALLELES LADEN ---
def load_and_analyze_all():
    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_ticker = {executor.submit(get_live_data, t): t for t in ALL_TICKERS}
        for future in concurrent.futures.as_completed(future_to_ticker):
            ticker = future_to_ticker[future]
            df = future.result()
            if df is not None:
                results[ticker] = analyze_swing(ticker, df)
    return results

# --- 4. DASHBOARD UI ---
st.title("🧪 Bio-Trading Monitor")
st.sidebar.header("Einstellungen")
if st.sidebar.button("Daten jetzt aktualisieren"):
    st.cache_data.clear()

with st.spinner("Marktdaten werden analysiert..."):
    data_pool = load_and_analyze_all()

# Top Metriken (Beispiel für Indizes)
cols = st.columns(len(data_pool))
for i, (ticker, res) in enumerate(list(data_pool.items())[:4]):
    with cols[i]:
        st.metric(res['name'], f"{res['cp']:,.2f}", f"{res['chg_3d']:.2f}%")

# Haupttabelle
st.subheader("Swing-Trading Signale")
df_display = pd.DataFrame([
    {"Ticker": t, "Name": v["name"], "Preis": v["cp"], "3D %": v["chg_3d"], 
     "Chance": v["chance"], "Wetter": v["weather"], "Trend": v["dot"]}
    for t, v in data_pool.items()
])
st.dataframe(df_display.sort_values("Chance", ascending=False), use_container_width=True)

# Einzelansicht & Charting
st.divider()
selected_ticker = st.selectbox("Detaillierte Analyse wählen:", list(data_pool.keys()))

if selected_ticker:
    res = data_pool[selected_ticker]
    col_a, col_b = st.columns([1, 2])
    
    with col_a:
        st.write(f"### {res['name']} Analyse")
        st.write(f"Wetter-Rating: {res['weather']}")
        st.progress(res['chance'] / 100)
        st.write(f"**ATR (14):** {res['atr']:.2f}")
        st.write(f"**Volumen-Faktor:** {res['vol_ratio']:.2f}x")

    with col_b:
        fig = go.Figure(data=[go.Candlestick(
            x=res['df'].index,
            open=res['df']['Open'],
            high=res['df']['High'],
            low=res['df']['Low'],
            close=res['df']['Close'],
            name="Kurs"
        )])
        fig.update_layout(height=400, margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig, use_container_width=True)
