import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh

# --- 1. KONFIGURATION ---
st.set_page_config(page_title="Bio-Trading Monitor Live PRO", layout="wide")
st_autorefresh(interval=60000, limit=1000, key="fscounter")

# --- 3. DESIGN (ERZWUNGENER DARK MODE) ---
st.markdown("""
    <style>
    /* Haupt-Hintergrund */
    .stApp { 
        background-color: #0E1117 !important; 
        color: #E0E0E0 !important; 
    }
    
    /* Header & Karten */
    .header-box { 
        padding: 15px; 
        border-radius: 12px; 
        text-align: center; 
        margin-bottom: 25px; 
        border: 1px solid #1E90FF; 
        background: rgba(30,144,255,0.05); 
    }
    
    /* Wetter-Karten Fix */
    .weather-card { 
        background-color: #161B22 !important; 
        border: 1px solid #30363D !important; 
        border-radius: 10px; 
        padding: 12px;
    }

    /* Tabellen-Farben erzwingen */
    .stTable, table { 
        background-color: #161B22 !important; 
        color: white !important; 
    }
    
    /* Texte in Selectboxen und Inputs */
    .stSelectbox label, .stMetric label { 
        color: #8892b0 !important; 
    }
    
    /* Trennlinien */
    hr { border-color: #30363D !important; }
    </style>
    """, unsafe_allow_html=True)


# --- 2. TICKER-MAPPING ---
st.info(f"🕒 Letztes Update: {pd.Timestamp.now().strftime('%H:%M:%S')} | Logik: Trend + MC + Vol")
TICKER_NAMES = {
    "EURUSD=X": "EUR/USD", "EURRUB=X": "EUR/RUB", "^GDAXI": "DAX 40 Index", "^NDX": "NASDAQ 100 Index",
    "^STOXX50E": "EuroStoxx 50", "XU100.IS": "BIST 100", "^NSEI": "Nifty 50",
    "ADS.DE": "🇩🇪 Adidas", "AIR.DE": "🇩🇪 Airbus", "ALV.DE": "🇩🇪 Allianz", "BAS.DE": "🇩🇪 BASF", "BAYN.DE": "🇩🇪 Bayer", 
    "RHM.DE": "🇩🇪 Rheinmetall", "SAP.DE": "🇩🇪 SAP", "SIE.DE": "🇩🇪 Siemens", "VOW3.DE": "🇩🇪 Volkswagen",
    "AAPL": "🇺🇸 Apple", "MSFT": "🇺🇸 Microsoft", "NVDA": "🇺🇸 Nvidia", "TSLA": "🇺🇸 Tesla", "PLTR": "🇺🇸 Palantir"
}

WEATHER_STRUCTURE = [["EURUSD=X", "EURRUB=X"], ["^GDAXI", "^NDX"], ["^STOXX50E", "XU100.IS", "^NSEI"]]
STOCKS_ONLY = [k for k in TICKER_NAMES.keys() if not k.startswith("^") and not "=X" in k]

# --- 3. DIE ZENTRALE 3-FAKTOR-LOGIK (KONSISTENZ-MODUL) ---
def get_bio_decision(df, ticker):
    if df.empty or len(df) < 20:
        return "☁️", "#8892b0", "⚪", "WARTEN", 50.0, 1.0
    
    # Faktor 1: Bio-Trend (Kurzfristig 1h)
    cp = float(df['Close'].iloc[-1])
    prev_cp = float(df['Close'].iloc[-2])
    chg = ((cp / prev_cp) - 1) * 100
    
    # Faktor 2: Monte-Carlo Konfidenz (Statistisch 15h)
    log_returns = np.log(df['Close'] / df['Close'].shift(1)).dropna()
    vola = log_returns.std()
    np.random.seed(42)
    # 100 Pfade simulieren
    sims = cp * np.exp(np.cumsum(np.random.normal(0, vola, (15, 100)), axis=0))
    prob_up = (sims[-1, :] > cp).sum() # Wie viele der 100 Pfade enden im Plus?
    
    # Faktor 3: Volumen-Bestätigung (Kraft)
    has_vol = 'Volume' in df.columns and df['Volume'].iloc[-1] > 0
    avg_vol = df['Volume'].tail(20).mean()
    vol_ratio = (df['Volume'].iloc[-1] / avg_vol) if has_vol and avg_vol > 0 else 1.0

    # ENTSCHEIDUNGSMATRIX (Die 3-Faktor-UND-Verknüpfung)
    # CALL: Trend positiv (>0.15%) UND Wahrscheinlichkeit (>55%) UND Volumen ok (>0.9)
    if chg > 0.15 and prob_up > 55 and vol_ratio > 0.9:
        return "☀️", "#00FFA3", "🟢", "CALL", prob_up, vol_ratio
    # PUT: Trend negativ (<-0.15%) UND Wahrscheinlichkeit (<45%) UND Volumen ok (>0.9)
    elif chg < -0.15 and prob_up < 45 and vol_ratio > 0.9:
        return "⛈️", "#1E90FF", "🔵", "PUT", prob_up, vol_ratio
    # WARTEN: In allen anderen Fällen (Widersprüche oder Seitwärts)
    else:
        return "☁️", "#8892b0", "⚪", "WARTEN", prob_up, vol_ratio

# --- 4. DATA LOADER ---
@st.cache_data(ttl=60)
def get_data(ticker):
    try:
        d = yf.download(ticker, period="60d", interval="1h", progress=False)
        if isinstance(d.columns, pd.MultiIndex): d.columns = d.columns.get_level_values(0)
        return d
    except: return pd.DataFrame()

# --- 5. DASHBOARD LAYOUT ---
st.title("🚀 Bio-Trading Monitor Live PRO")

# 5a. MARKT-WETTER (Konsistent)
st.subheader("🌐 Globales Markt-Wetter")
for row in WEATHER_STRUCTURE:
    cols = st.columns(len(row))
    for i, t in enumerate(row):
        data = get_data(t)
        icon, col, dot, status, prob, vol = get_bio_decision(data, t)
        cp = data['Close'].iloc[-1] if not data.empty else 0
        chg = ((cp / data['Close'].iloc[-2]) - 1) * 100 if not data.empty else 0
        prec = 5 if "=X" in t else 2
        with cols[i]:
            st.markdown(f"""
                <div style="border: 1px solid {col}; padding: 12px; border-radius: 10px; background: rgba(255,255,255,0.02); margin-bottom:10px;">
                    <div style="display: flex; justify-content: space-between;"><small style="color:#8892b0;">{TICKER_NAMES.get(t, t)}</small><span>{icon}</span></div>
                    <b style="font-size: 1.5rem;">{cp:,.{prec}f}</b><br>
                    <div style="display: flex; justify-content: space-between; margin-top: 5px;">
                        <span style="color:{col}; font-weight:bold;">{chg:+.2f}%</span>
                        <span style="color:{col}; font-size:1.2rem;">{dot}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

st.divider()

# 5b. TOP 5 (Synchronisiert & mit Wahrscheinlichkeits-Info)
st.subheader("📊 Top 5 Markt-Signale")
t1, t2 = st.columns(2)
all_sigs = []
for t in STOCKS_ONLY:
    d = get_data(t)
    if not d.empty:
        icon, col, dot, status, prob, vol = get_bio_decision(d, t)
        all_sigs.append({
            'Status': dot, 
            'Aktie': TICKER_NAMES.get(t, t), 
            'Trend': ((d['Close'].iloc[-1]/d['Close'].iloc[-2])-1)*100, 
            'Konfidenz': f"{prob:.0f}%",
            'Ticker': t
        })

df_sigs = pd.DataFrame(all_sigs)
with t1:
    st.markdown("<h4 style='color:#00FFA3;'>🟢 Top CALL-Kandidaten</h4>", unsafe_allow_html=True)
    st.table(df_sigs.nlargest(5, 'Trend')[['Status', 'Aktie', 'Trend', 'Konfidenz']])
with t2:
    st.markdown("<h4 style='color:#1E90FF;'>🔵 Top PUT-Kandidaten</h4>", unsafe_allow_html=True)
    st.table(df_sigs.nsmallest(5, 'Trend')[['Status', 'Aktie', 'Trend', 'Konfidenz']])

st.divider()

# 5c. EINZELBEWERTUNG (Die Detail-Ansicht)
st.subheader("🔍 Einzelwert Bio-Check")
sel_stock = st.selectbox("Wähle einen Wert zur Tiefenanalyse:", STOCKS_ONLY, format_func=lambda x: TICKER_NAMES.get(x, x))
d_s = get_data(sel_stock)

if not d_s.empty:
    icon, col, dot, status, prob, vol = get_bio_decision(d_s, sel_stock)
    cp = d_s['Close'].iloc[-1]
    chg = ((cp / d_s['Close'].iloc[-2]) - 1) * 100

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Kurs", f"{cp:,.2f}", f"{chg:+.2f}%")
    m2.metric("Wetter-Status", f"{status} {icon}")
    m3.metric("MC-Konfidenz", f"{prob:.0f}%", delta=f"{prob-50:.0f}%")
    m4.markdown(f'<div style="text-align:center; background:{col}22; padding:10px; border:1px solid {col}; color:{col}; font-weight:bold; border-radius:8px;">{dot} SIGNAL: {status}</div>', unsafe_allow_html=True)

    # KOMBI-CHART
    fig, ax1 = plt.subplots(figsize=(12, 4), facecolor='#0E1117')
    ax1.set_facecolor('#0E1117')
    ax1.plot(d_s.index, d_s['Close'], color='#1E90FF', linewidth=2)
    ax1.tick_params(axis='both', colors='#8892b0')
    
    ax2 = ax1.twinx()
    v_cols = ['#00FFA3' if d_s['Close'].iloc[i] >= d_s['Open'].iloc[i] else '#1E90FF' for i in range(len(d_s))]
    ax2.bar(d_s.index, d_s['Volume'], color=v_cols, alpha=0.25, width=0.03)
    ax2.set_ylim(0, d_s['Volume'].max() * 5)
    
    st.pyplot(fig)

    st.markdown(f"""
    <div style="padding:15px; border-radius:10px; background:rgba(255,255,255,0.02); border: 1px solid #333;">
        <b>Bio-Fazit:</b> Der aktuelle <b>{status}</b>-Status basiert auf einer Wahrscheinlichkeit von <b>{prob:.0f}%</b> 
        und einem Volumen-Trend von <b>{vol:.2f}x</b>. {'🔥 Signal durch Volumen bestätigt.' if vol > 1.1 else '⚠️ Achtung: Zu wenig Volumen für einen sicheren Trade.'}
    </div>
    """, unsafe_allow_html=True)

st.info(f"🕒 Letztes Update: {pd.Timestamp.now().strftime('%H:%M:%S')} | Logik: Trend + MC + Vol")
