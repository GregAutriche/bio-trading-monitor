import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from streamlit_autorefresh import st_autorefresh

# --- 1. KONFIGURATION ---
st.set_page_config(page_title="Bio-Trading Monitor Live PRO", layout="wide")
st_autorefresh(interval=60000, limit=1000, key="fscounter")

# --- 2. TICKER-MAPPING ---
TICKER_NAMES = {
    "EURUSD=X": "💱 EUR/USD", "EURRUB=X": "💱 EUR/RUB", 
    "^GDAXI": "📊 DAX 40", "^NDX": "📊 NASDAQ 100",
    "^STOXX50E": "📊 EuroStoxx 50", "^NSEI": "📊 Nifty 50", "XU100.IS": "📊 BIST 100",
    "ADS.DE": "🇩🇪 Adidas", "AIR.DE": "🇩🇪 Airbus", "ALV.DE": "🇩🇪 Allianz", "BAS.DE": "🇩🇪 BASF", 
    "BAYN.DE": "🇩🇪 Bayer", "BMW.DE": "🇩🇪 BMW", "DBK.DE": "🇩🇪 Deutsche Bank", "DTE.DE": "🇩🇪 Telekom", 
    "RHM.DE": "🇩🇪 Rheinmetall", "SAP.DE": "🇩🇪 SAP", "AAPL": "🇺🇸 Apple", "MSFT": "🇺🇸 Microsoft", 
    "NVDA": "🇺🇸 Nvidia", "TSLA": "🇺🇸 Tesla", "AMD": "🇺🇸 AMD", "PLTR": "🇺🇸 Palantir"
}

# FILTER: Nur Aktien für Top 5 und Detail-Auswahl
STOCKS_ONLY = [k for k in TICKER_NAMES.keys() if not k.startswith("^") and not "=X" in k]

# --- 3. DESIGN (MAXIMALER KONTRAST) ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117 !important; color: #FFFFFF !important; }
    .weather-card { text-align:center; border-radius:12px; background:rgba(255,255,255,0.03); border: 1px solid #333; padding: 15px; margin-bottom: 10px; }
    thead tr th { background-color: #2D3748 !important; color: #FFFFFF !important; font-weight: 900 !important; border-bottom: 3px solid #1E90FF !important; }
    tbody tr td { color: #FFFFFF !important; background-color: #161B22 !important; border-bottom: 1px solid #30363D !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FUNKTIONEN ---
@st.cache_data(ttl=60)
def get_data(ticker, period="60d", interval="1h"):
    try:
        d = yf.download(ticker, period=period, interval=interval, progress=False)
        if isinstance(d.columns, pd.MultiIndex): d.columns = d.columns.get_level_values(0)
        return d
    except: return pd.DataFrame()

def calculate_metrics(df):
    if df.empty or len(df) < 20: return 0.0, 50, 0.0
    cp = float(df['Close'].iloc[-1])
    # ATR (14)
    high_low = df['High'] - df['Low']
    atr = high_low.rolling(14).mean().iloc[-1]
    # Chance via Monte Carlo (Log-Returns Simulation)
    returns = np.log(df['Close'] / df['Close'].shift(1)).dropna()
    sim = np.random.normal(returns.mean(), returns.std(), 1000)
    chance = int((sim > 0).sum() / 10)
    return cp, chance, atr

# --- 5. DASHBOARD ---
st.title("🚀 Bio-Trading Monitor Live PRO")

# 5a. MARKT-WETTER (3 ZEILEN)
WEATHER_ROWS = [["EURUSD=X", "EURRUB=X"], ["^GDAXI", "^NDX"], ["^STOXX50E", "^NSEI", "XU100.IS"]]
for row in WEATHER_ROWS:
    cols = st.columns(len(row))
    for i, t in enumerate(row):
        df_m = get_data(t, period="5d")
        if not df_m.empty:
            cp, _, _ = calculate_metrics(df_m)
            chg = ((cp / df_m['Close'].iloc[-2]) - 1) * 100
            color = "#00FFA3" if chg > 0.15 else "#1E90FF" if chg < -0.15 else "#8892b0"
            prec = ".4f" if "=X" in t else ".2f"
            with cols[i]:
                st.markdown(f'<div class="weather-card" style="border-color:{color};"><small>{TICKER_NAMES.get(t,t)}</small><br><b style="font-size:1.4rem;">{cp: ,{prec}}</b><br><span style="color:{color};">{chg:+.2f}%</span></div>', unsafe_allow_html=True)

st.divider()

# 5b. TOP 5 AKTIEN NACH CHANCE SORTIERT
st.subheader("📊 Top 5 Aktien-Chancen (nach Wahrscheinlichkeit sortiert)")
signals = []
with st.spinner("Berechne Gewinn-Chancen..."):
    for s in STOCKS_ONLY:
        df_s = get_data(s, period="10d", interval="1h")
        if not df_s.empty:
            cp, chance, _ = calculate_metrics(df_s)
            ret = ((cp / df_s['Close'].iloc[-2]) - 1) * 100
            signals.append({
                'Status': '☀️' if chance > 60 else '⛈️' if chance < 40 else '☁️',
                'Aktie': TICKER_NAMES.get(s,s), 
                'Trend': f"{ret:+.2f}%", 
                'Chance': chance, # Numerisch für Sortierung
                'Chance_Str': f"{chance}%"
            })

df_sig = pd.DataFrame(signals)
c_top1, c_top2 = st.columns(2)

if not df_sig.empty:
    with c_top1:
        st.markdown("<h4 style='color:#00FFA3;'>Top 5 CALL (Höchste Chance)</h4>", unsafe_allow_html=True)
        # Sortiert nach höchster Chance
        top_calls = df_sig.sort_values(by='Chance', ascending=False).head(5)
        st.table(top_calls[['Status', 'Aktie', 'Trend', 'Chance_Str']].rename(columns={'Chance_Str': 'Chance'}))
    
    with c_top2:
        st.markdown("<h4 style='color:#1E90FF;'>Top 5 PUT (Niedrigste Chance)</h4>", unsafe_allow_html=True)
        # Sortiert nach niedrigster Chance
        top_puts = df_sig.sort_values(by='Chance', ascending=True).head(5)
        st.table(top_puts[['Status', 'Aktie', 'Trend', 'Chance_Str']].rename(columns={'Chance_Str': 'Chance'}))

st.divider()

# 5c. DETAIL-ANALYSE (NUR AKTIEN)
st.subheader("🔍 Detail-Analyse (Aktien)")
sel_stock = st.selectbox("Aktie für Details wählen:", STOCKS_ONLY, format_func=lambda x: TICKER_NAMES[x])

d_det = get_data(sel_stock, period="60d", interval="4h")
if not d_det.empty:
    cp, chance, atr = calculate_metrics(d_det)
    avg_vol = d_det['Volume'].tail(120).mean()
    cur_vol = d_det['Volume'].iloc[-1]
    v_trend = ((cur_vol / avg_vol) - 1) * 100 if avg_vol > 0 else 0
    
    col_d1, col_d2, col_d3, col_d4 = st.columns(4)
    col_d1.metric("KURS", f"{cp:,.2f}")
    col_d2.metric("CHANCE", f"{chance}%", delta=f"{chance-50}%")
    col_d3.metric("ATR (14h)", f"{atr:.2f}")
    col_d4.metric("VOL.-TREND (20d)", f"{v_trend:+.1f}%")
    
    st.write("**Volumen-Verlauf (Letzte 40 Perioden):**")
    st.bar_chart(d_det['Volume'].tail(40))

st.info(f"🕒 Update: {pd.Timestamp.now().strftime('%H:%M:%S')} | Top 5 jetzt nach Gewinn-Chance sortiert.")
