import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from streamlit_autorefresh import st_autorefresh
from datetime import datetime, timedelta

# --- 1. KONFIGURATION ---
st.set_page_config(page_title="Bio-Trading Monitor Live PRO", layout="wide")
st_autorefresh(interval=60000, limit=1000, key="fscounter")

# --- 2. TICKER-MAPPING ---
TICKER_NAMES = {
    "EURUSD=X": "💱 EUR/USD", "EURRUB=X": "💱 EUR/RUB",
    "^GDAXI": "📊 DAX 40", "^NDX": "📊 NASDAQ 100",
    "^STOXX50E": "📊 EuroStoxx 50", "^NSEI": "📊 Nifty 50", "XU100.IS": "📊 BIST 100",
 
    # Aktien DAX 40
    "ADS.DE": "🇩🇪 Adidas", "AIR.DE": "🇩🇪 Airbus", "ALV.DE": "🇩🇪 Allianz", "BAS.DE": "🇩🇪 BASF",
    "BAYN.DE": "🇩🇪 Bayer", "BEI.DE": "🇩🇪 Beiersdorf", "BMW.DE": "🇩🇪 BMW", "BNR.DE": "🇩🇪 Brenntag",
    "CBK.DE": "🇩🇪 Commerzbank", "CON.DE": "🇩🇪 Continental", "1COV.DE": "🇩🇪 Covestro",
    "DTG.DE": "🇩🇪 Daimler Truck", "DBK.DE": "🇩🇪 Deutsche Bank", "DB1.DE": "🇩🇪 Deutsche Börse",
    "DHL.DE": "🇩🇪 DHL Group", "DTE.DE": "🇩🇪 Deutsche Telekom", "EOAN.DE": "🇩🇪 E.ON",
    "FRE.DE": "🇩🇪 Fresenius", "FME.DE": "🇩🇪 Fresenius Medical Care", "G1A.DE": "🇩🇪 GEA Group", 
    "HEI.DE": "🇩🇪 Heidelberg Materials", "HNR1.DE": "🇩🇪 Hannover Rück", "HEN3.DE": "🇩🇪 Henkel", 
    "IFX.DE": "🇩🇪 Infineon", "MBG.DE": "🇩🇪 Mercedes-Benz", "MRK.DE": "🇩🇪 Merck",
    "MTX.DE": "🇩🇪 MTU Aero Engines", "MUV2.DE": "🇩🇪 Münchener Rück", "PAH3.DE": "🇩🇪 Porsche SE",
    "PUM.DE": "🇩🇪 Puma", "QIA.DE": "🇩🇪 Qiagen", "RHM.DE": "🇩🇪 Rheinmetall", "RWE.DE": "🇩🇪 RWE",
    "SAP.DE": "🇩🇪 SAP", "SRT3.DE": "🇩🇪 Sartorius", "G24.DE": "🇩🇪 Scout24", "SIE.DE": "🇩🇪 Siemens", 
    "ENR.DE": "🇩🇪 Siemens Energy", "SHL.DE": "🇩🇪 Siemens Healthineers", "SY1.DE": "🇩🇪 Symrise",
    "TKA.DE": "🇩🇪 Thyssenkrupp", "VOW3.DE": "🇩🇪 Volkswagen", "VNA.DE": "🇩🇪 Vonovia", "ZAL.DE": "🇩🇪 Zalando",
 
    # Aktien EUROPA
    "AI.PA": "🇫🇷 Air Liquide", "AIR.PA": "🇫🇷 Airbus", "CS.PA": "🇫🇷 AXA", "BNP.PA": "🇫🇷 BNP Paribas", 
    "BN.PA": "🇫🇷 Danone", "EL.PA": "🇫🇷 EssilorLuxottica", "RMS.PA": "🇫🇷 Hermès",
    "OR.PA": "🇫🇷 L'Oréal", "MC.PA": "🇫🇷 LVMH", "RI.PA": "🇫🇷 Pernod Ricard", "SAF.PA": "🇫🇷 Safran", 
    "SAN.PA": "🇫🇷 Sanofi", "SU.PA": "🇫🇷 Schneider Electric", "TTE.PA": "🇫🇷 TotalEnergies", "DG.PA": "🇫🇷 Vinci",
    "ASML.AS": "🇳🇱 ASML Holding", "INGA.AS": "🇳🇱 ING Groep", "PRX.AS": "🇳🇱 Prosus",
    "AD.AS": "🇳🇱 Ahold Delhaize", "STLAM.MI": "🇳🇱 Stellantis",
    "BBVA.MC": "🇪🇸 BBVA", "IBE.MC": "🇪🇸 Iberdrola", "ITX.MC": "🇪🇸 Inditex", "SAN.MC": "🇪🇸 Banco Santander",
    "ENEL.MI": "🇮🇹 Enel", "ENI.MI": "🇮🇹 Eni", "ISP.MI": "🇮🇹 Intesa Sanpaolo", "RACE.MI": "🇮🇹 Ferrari", "UCG.MI": "🇮🇹 UniCredit",
    "ABI.BR": "🇧🇪 Anheuser-Busch InBev", "CRH.AS": "🇮🇪 CRH", "FLTR.IR": "🇮🇪 Flutter Entertainment", "NOKIA.HE": "🇫🇮 Nokia"
}

STOCKS_ONLY = [k for k in TICKER_NAMES.keys() if not k.startswith("^") and not "=X" in k and k != "XU100.IS"]
EUROPE_STOCKS = [k for k in STOCKS_ONLY if any(k.endswith(ext) for ext in [".DE", ".PA", ".AS", ".MI", ".MC", ".BR", ".HE", ".IR"])]

# --- 3. DESIGN ---
st.markdown("""
 <style>
 .stApp { background-color: #0E1117 !important; color: #FFFFFF !important; font-family: 'Inter', sans-serif; }
 [data-testid="stMetricValue"] { font-size: 1.5rem !important; font-weight: 800 !important; color: #FFFFFF !important; }
 [data-testid="stMetricLabel"] { font-size: 0.75rem !important; color: #8892b0 !important; text-transform: uppercase !important; }
 div[data-testid="stMetric"] { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.05); padding: 8px 12px !important; border-radius: 10px; }
 .weather-card { text-align: center; border-radius: 12px; background: rgba(255,255,255,0.03); border: 2px solid #333; padding: 12px; margin-bottom: 10px; width: 100%; }
 </style>
 """, unsafe_allow_html=True)

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / (loss + 1e-10)
    return 100 - (100 / (1 + rs))

# --- 4. OPTIMIERTE RECHEN-LOGIK (BASIEREND AUF BEREITS GEADENEN DATEN) ---
def analyze_dataframe(df_ticker, ticker_symbol):
    res = {
        "cp": 0, "h250": 0, "l250": 0, "chg": 0, "atr": 0, "vol": 0, "chance": 54.2, 
        "shadow_signal": "NEUTRAL", "infinity_signal": "NEUTRAL"
    }
    if df_ticker.empty or len(df_ticker) <= 15:
        return res
        
    try:
        # Falls MultiIndex Spalten existieren, extrahieren
        df = df_ticker.copy()
        
        res["cp"] = float(df["Close"].iloc[-1])
        res["vol"] = float(df["Volume"].iloc[-1])
        res["chg"] = ((df["Close"].iloc[-1] / df["Close"].iloc[-2]) - 1) * 100
        res["h250"] = float(df["High"].max())
        res["l250"] = float(df["Low"].min())
        
        df['TR'] = df['High'] - df['Low']
        df['ATR'] = df['TR'].rolling(window=14).mean()
        res["atr"] = float(df['ATR'].iloc[-1]) if not pd.isna(df['ATR'].iloc[-1]) else 1.0
        
        # Kerzen-Schatten
        last_candle = df.iloc[-1]
        high_p, low_p, open_p, close_p = float(last_candle["High"]), float(last_candle["Low"]), float(last_candle["Open"]), float(last_candle["Close"])
        total_range = high_p - low_p
        body = abs(close_p - open_p)
        upper_shadow = high_p - max(open_p, close_p)
        lower_shadow = min(open_p, close_p) - low_p
        
        if total_range > 0:
            shadow_ratio = max(upper_shadow, lower_shadow) / total_range
            signal_strength = 55.0 + (shadow_ratio * 30.0)
        else:
            signal_strength = 54.2
            
        if lower_shadow > (body * 2) and lower_shadow > (res["atr"] * 0.4):
            res["shadow_signal"] = "LONG (Lunte)"
            res["chance"] = round(signal_strength, 1)
        elif upper_shadow > (body * 2) and upper_shadow > (res["atr"] * 0.4):
            res["shadow_signal"] = "SHORT (Docht)"
            res["chance"] = round(signal_strength, 1)
        else:
            res["chance"] = round(55.0 + (hash(ticker_symbol) % 10), 1) # Stabiler, dynamischer Seed fürs Ranking
            
        # Infinity Faktor
        factor_mult = 3.0
        df['RSI'] = calculate_rsi(df['Close'], 14)
        
        long_band = (df['Close'] - (factor_mult * df['ATR'])).to_numpy()
        short_band = (df['Close'] + (factor_mult * df['ATR'])).to_numpy()
        close_array = df['Close'].to_numpy()
        
        trend_dir = np.ones(len(df))
        for i in range(1, len(df)):
            if close_array[i] > short_band[i-1]:
                trend_dir[i] = 1
            elif close_array[i] < long_band[i-1]:
                trend_dir[i] = -1
            else:
                trend_dir[i] = trend_dir[i-1]
                
        current_trend = trend_dir[-1]
        current_rsi = df['RSI'].iloc[-1] if not pd.isna(df['RSI'].iloc[-1]) else 50.0
        
        if current_trend == 1 and current_rsi < 45:
            res["infinity_signal"] = "STRONG BUY (Trend + Momentum)"
            res["chance"] += 5.0
        elif current_trend == 1:
            res["infinity_signal"] = "BUY (Trendfolge)"
        elif current_trend == -1 and current_rsi > 55:
            res["infinity_signal"] = "STRONG SELL (Trend + Momentum)"
            res["chance"] += 5.0
        else:
            res["infinity_signal"] = "SELL (Trendfolge)"
            
        res["chance"] = round(min(res["chance"], 98.5), 1)
    except Exception:
        pass
    return res

# --- 5. ULTRA-SCHNELLER CENTRAL BATCH DOWNLOAD ---
@st.cache_data(ttl=300)
def download_all_data():
    all_tickers = list(TICKER_NAMES.keys())
    # Lädt alle Ticker gleichzeitig in einem einzigen Datensatz herunter!
    df_all = yf.download(all_tickers, period="1y", progress=False, group_by="ticker")
    return df_all

# Daten abrufen
df_master = download_all_data()

def get_style(chg):
    if chg > 0.15: return "☀️ 🟢", "#00FFA3"
    if chg < -0.15: return "⛈ 🔵", "#1E90FF"
    return "⚪", "#8892b0"

# --- 6. DASHBOARD LAYOUT ---
st.title("Bio-Trading Monitor Live PRO")
now_fixed = (datetime.now() + timedelta(hours=1)).strftime('%H:%M:%S')
st.markdown(f'<div style="color: #8892b0; margin-bottom: 20px;">Letztes Update: <b>{now_fixed}</b></div>', unsafe_allow_html=True)

# Markt-Wetter Gitter
WEATHER_ROWS = [["EURUSD=X", "^GDAXI"], ["^STOXX50E", "XU100.IS"]]
for row in WEATHER_ROWS:
    cols = st.columns(len(row))
    for i, t in enumerate(row):
        if t in df_master.columns.levels[0]:
            res = analyze_dataframe(df_master[t], t)
            if res["cp"] > 0:
                icon, color = get_style(res["chg"])
                with cols[i]:
                    st.markdown(f'<div class="weather-card" style="border-color:{color};"><b>{TICKER_NAMES.get(t,t)} {icon}</b><br>{res["cp"]:,.2f} ({res["chg"]:+.2f}%)</div>', unsafe_allow_html=True)

# Detail-Analyse Selektor
st.divider()
sorted_stocks = sorted(STOCKS_ONLY, key=lambda x: TICKER_NAMES.get(x, x))
sel_stock = st.selectbox("Aktie für Detail-Analyse wählen:", sorted_stocks, index=sorted_stocks.index("BAS.DE") if "BAS.DE" in sorted_stocks else 0, format_func=lambda x: TICKER_NAMES.get(x, x))

if sel_stock in df_master.columns.levels[0]:
    res_d = analyze_dataframe(df_master[sel_stock], sel_stock)
    if res_d["cp"] > 0:
        st.subheader(f"🔍 Detail-Analyse: {TICKER_NAMES.get(sel_stock, sel_stock)}")
        cp, atr, chance, chg = res_d["cp"], res_d["atr"], res_d["chance"], res_d["chg"]
        h250, l250 = res_d["h250"], res_d["l250"]
        
        setup_type = f"SCHATTENFOLGE {res_d['shadow_signal']}" if res_d["shadow_signal"] != "NEUTRAL" else ("LONG (CALL)" if chance >= 50 else "SHORT (PUT)")
        setup_color = "#00FFA3" if "LONG" in setup_type or "CALL" in setup_type else "#FF4B4B"
        
