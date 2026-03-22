import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

# --- 1. KONFIGURATION ---
st.set_page_config(page_title="Bio-Trading Monitor Live PRO", layout="wide")
st_autorefresh(interval=60000, limit=1000, key="fscounter")

# --- 2. TICKER-MAPPING ---
TICKER_NAMES = {
    # Wetter (Forex & Indizes)
    "EURUSD=X": "💱 EUR/USD", "EURRUB=X": "💱 EUR/RUB", 
    "^GDAXI": "📊 DAX 40", "^NDX": "📊 NASDAQ 100",
    "^STOXX50E": "📊 EuroStoxx 50", "^NSEI": "📊 Nifty 50", "XU100.IS": "📊 BIST 100",
    # Aktien DAX 40
    "ADS.DE": "🇩🇪 Adidas", "AIR.DE": "🇩🇪 Airbus", "ALV.DE": "🇩🇪 Allianz", "BAS.DE": "🇩🇪 BASF", "BAYN.DE": "🇩🇪 Bayer", 
    "BMW.DE": "🇩🇪 BMW", "DBK.DE": "🇩🇪 Deutsche Bank", "DTE.DE": "🇩🇪 Telekom", "RHM.DE": "🇩🇪 Rheinmetall", 
    "RWE.DE": "🇩🇪 RWE", "SAP.DE": "🇩🇪 SAP", "SIE.DE": "🇩🇪 Siemens", "VOW3.DE": "🇩🇪 VW",
    # Aktien US / NASDAQ
    "AAPL": "🇺🇸 Apple", "MSFT": "🇺🇸 Microsoft", "NVDA": "🇺🇸 Nvidia", "TSLA": "🇺🇸 Tesla", 
    "AMD": "🇺🇸 AMD", "PLTR": "🇺🇸 Palantir", "MSTR": "🇺🇸 MicroStrategy", "AMZN": "🇺🇸 Amazon"
}

# Filter für Detail-Analyse (Keine Währungen/Indizes)
STOCKS_ONLY = [k for k in TICKER_NAMES.keys() if not k.startswith("^") and not "=X" in k and k != "XU100.IS"]

# --- 3. DESIGN (DARK MODE & KONTRAST) ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117 !important; color: #FFFFFF !important; }
    .weather-card { text-align:center; border-radius:12px; background:rgba(255,255,255,0.03); border: 2px solid #333; padding: 15px; margin-bottom: 10px; }
    .update-info { color: #8892b0; font-size: 0.85rem; margin-bottom: 20px; text-align: center; border: 1px solid #1E90FF; padding: 5px; border-radius: 5px; }
    thead tr th { background-color: #2D3748 !important; color: #FFFFFF !important; font-weight: 900 !important; border-bottom: 3px solid #1E90FF !important; }
    tbody tr td { color: #FFFFFF !important; background-color: #161B22 !important; border-bottom: 1px solid #30363D !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. ZENTRALE FUNKTION ---
@st.cache_data(ttl=60)
def get_analysis(ticker):
    try:
        df = yf.download(ticker, period="30d", interval="1h", progress=False)
        if df.empty or len(df) < 15: 
            return {"cp": 0.0, "chg": 0.0, "chance": 50, "atr": 0.0, "vol": 0, "df": df}
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        cp = float(df['Close'].iloc[-1])
        prev = float(df['Close'].iloc[-2])
        chg = ((cp / prev) - 1) * 100
        atr = (df['High'] - df['Low']).rolling(14).mean().iloc[-1]
        
        # Chance Simulation (Synchronisiert)
        returns = np.log(df['Close'] / df['Close'].shift(1)).dropna()
        np.random.seed(42)
        sim = np.random.normal(returns.mean(), returns.std(), 1000)
        chance = int((sim > 0).sum() / 10)
        
        return {"cp": cp, "chg": chg, "chance": chance, "atr": atr, "vol": int(df['Volume'].iloc[-1]), "df": df}
    except:
        return {"cp": 0.0, "chg": 0.0, "chance": 50, "atr": 0.0, "vol": 0, "df": pd.DataFrame()}

def get_style(chg):
    if chg > 0.15: return "☀️", "#00FFA3", "🟢"
    if chg < -0.15: return "⛈️", "#1E90FF", "🔵"
    return "☁️", "#8892b0", "⚪"

# --- 5. DASHBOARD AUFBAU ---
st.title("🚀 Bio-Trading Monitor Live PRO")
now = datetime.now().strftime('%H:%M:%S')
st.markdown(f'<div class="update-info">🕒 Letztes Update: <b>{now}</b> | Intervall: 60s | Synchronisiert</div>', unsafe_allow_html=True)

# 5a. MARKT-WETTER (3 ZEILEN)
WEATHER_ROWS = [
    ["EURUSD=X", "EURRUB=X"],                   # 1. Währungen
    ["^GDAXI", "^NDX"],                         # 2. Leit-Indizes
    ["^STOXX50E", "^NSEI", "XU100.IS"]          # 3. Weitere Indizes
]

for row in WEATHER_ROWS:
    cols = st.columns(len(row))
    for i, t in enumerate(row):
        res = get_analysis(t)
        icon, color, dot = get_style(res["chg"])
        prec = ".4f" if "=X" in t else ".2f"
        price_str = f"{res['cp']: ,{prec}}"
        with cols[i]:
            st.markdown(f"""
                <div class="weather-card" style="border-color:{color};">
                    <div style="display: flex; justify-content: space-between;"><small>{TICKER_NAMES.get(t,t)}</small><span>{icon}</span></div>
                    <b style="font-size:1.5rem;">{price_str}</b><br>
                    <div style="display: flex; justify-content: space-between; margin-top: 5px;">
                        <span style="color:{color};">{res['chg']:+.2f}%</span><span>{dot}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

st.divider()

# 5b. TOP 5 AKTIEN
st.subheader("📊 Top 5 Aktien-Chancen")
signals = []
with st.spinner("Analysiere Markt..."):
    for s in STOCKS_ONLY:
        r = get_analysis(s)
        if r["cp"] > 0:
            _, _, dot = get_style(r["chg"])
            signals.append({'Status': dot, 'Aktie': TICKER_NAMES.get(s,s), 'Trend_Val': r["chg"], 'Trend': f"{r['chg']:+.2f}%", 'Chance': r["chance"]})

df_sig = pd.DataFrame(signals)
if not df_sig.empty:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<h4 style='color:#00FFA3;'>Top 5 CALL (Chance)</h4>", unsafe_allow_html=True)
        st.table(df_sig[df_sig['Trend_Val'] > 0].nlargest(5, 'Chance')[['Status', 'Aktie', 'Trend', 'Chance']])
    with c2:
        st.markdown("<h4 style='color:#1E90FF;'>Top 5 PUT (Chance)</h4>", unsafe_allow_html=True)
        st.table(df_sig[df_sig['Trend_Val'] < 0].nsmallest(5, 'Chance')[['Status', 'Aktie', 'Trend', 'Chance']])

st.divider()

# 5c. DETAIL-ANALYSE
st.subheader("🔍 Detail-Analyse & Volumen-Profil")
sorted_stocks = sorted(STOCKS_ONLY, key=lambda x: TICKER_NAMES.get(x, x))
sel_stock = st.selectbox("Aktie wählen:", sorted_stocks, format_func=lambda x: TICKER_NAMES.get(x, x))

res_d = get_analysis(sel_stock)

if res_d["cp"] > 0:
    icon_d, color_d, dot_d = get_style(res_d["chg"])
    
    # Metriken
    col_d1, col_d2, col_d3, col_d4 = st.columns(4)
    col_d1.metric("KURS", f"{res_d['cp']:,.2f}", f"{res_d['chg']:+.2f}%")
    col_d2.metric("CHANCE", f"{res_d['chance']}%", delta=f"{res_d['chance']-50}%")
    col_d3.metric("ATR (14h)", f"{res_d['atr']:.2f}")
    col_d4.metric("VOLUMEN", f"{res_d['vol']:,.0f}")
    
    st.markdown(f"**Aktueller Status:** {icon_d} {dot_d}")

    # Grafik (Lückenlose Candlesticks & Volumen)
    try:
        df_plot = res_d["df"].tail(60).copy()
        df_plot['x_label'] = df_plot.index.strftime('%d.%m %H:%M')
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        # Volumen (Links)
        fig.add_trace(go.Bar(x=df_plot['x_label'], y=df_plot['Volume'], name="Volumen", marker_color='#1E90FF', opacity=0.25), secondary_y=False)
        # Candlesticks (Rechts)
        fig.add_trace(go.Candlestick(x=df_plot['x_label'], open=df_plot['Open'], high=df_plot['High'], low=df_plot['Low'], close=df_plot['Close'], name="Kurs", increasing_line_color='#00FFA3', decreasing_line_color='#FF4B4B'), secondary_y=True)

        fig.update_layout(height=500, margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False, xaxis_rangeslider_visible=False, xaxis=dict(type='category', tickangle=-45, nticks=12, gridcolor='#333', showgrid=False))
        fig.update_yaxes(title_text="Volumen", secondary_y=False, showgrid=False, color="#8892b0")
        fig.update_yaxes(title_text="Kurs", secondary_y=True, gridcolor='#333', side="right")

        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Grafik-Fehler: {e}")
