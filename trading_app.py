import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import pytz
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

# --- 1. KONFIGURATION & AUTOMATISCHER REFRESH ---
st.set_page_config(page_title="Bio-Trading Monitor Live PRO", layout="wide")

st.sidebar.title("🎛️ Monitor Steuerung")
refresh_options = {
    "30 Sekunden": 30000,
    "1 Minute": 60000,
    "5 Minuten": 300000,
    "Manuell (Aus)": 9999999
}
selected_refresh = st.sidebar.selectbox("Aktualisierungsintervall:", list(refresh_options.keys()), index=1)
st_autorefresh(interval=refresh_options[selected_refresh], limit=1000, key="fscounter")

# --- 2. TICKER-MAPPING ---
TICKER_NAMES = {
    "EURUSD=X": "💱 EUR/USD", "EURRUB=X": "💱 EUR/RUB",
    "^GDAXI": "📊 DAX 40", "^NDX": "📊 NASDAQ 100",
    "^STOXX50E": "📊 EuroStoxx 50", "^NSEI": "📊 Nifty 50", "XU100.IS": "📊 BIST 100",
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

# --- 3. CUSTOM CSS ---
st.markdown("""
 <style>
 .stApp { background-color: #0E1117 !important; color: #FFFFFF !important; font-family: 'Inter', sans-serif; }
 [data-testid="stMetricValue"] { font-size: 1.5rem !important; font-weight: 800 !important; color: #FFFFFF !important; }
 [data-testid="stMetricLabel"] { font-size: 0.75rem !important; color: #8892b0 !important; text-transform: uppercase !important; }
 div[data-testid="stMetric"] { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.05); padding: 8px 12px !important; border-radius: 10px; }
 .weather-card { text-align: center; border-radius: 12px; background: rgba(255,255,255,0.03); border: 2px solid #333; padding: 12px; margin-bottom: 10px; width: 100%; }
 .signal-alert { background-color: #FF4B4B; color: white; padding: 15px; border-radius: 10px; font-weight: bold; text-align: center; font-size: 1.2rem; margin-bottom: 20px; border: 2px solid #FFFFFF; }
 </style>
 """, unsafe_allow_html=True)

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / (loss + 1e-10)
    return 100 - (100 / (1 + rs))

# --- 4. ENGINE LOGIK ---
@st.cache_data(ttl=120)
def get_ticker_analysis(ticker_symbol):
    res = {"cp": 0, "h250": 0, "l250": 0, "chg": 0, "atr": 0, "vol": 0, "chance": 50.0, "shadow_signal": "NEUTRAL", "infinity_signal": "NEUTRAL"}
    try:
        df = yf.download(ticker_symbol, period="1mo", progress=False)
        if df.empty or len(df) <= 5:
            return res
            
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        df = df.dropna(subset=["Close"])
        if len(df) < 2:
            return res

        res["cp"] = float(df["Close"].iloc[-1])
        res["vol"] = float(df["Volume"].iloc[-1])
        res["chg"] = ((df["Close"].iloc[-1] / df["Close"].iloc[-2]) - 1) * 100
        res["h250"] = float(df["High"].max())
        res["l250"] = float(df["Low"].min())
        
        df['TR'] = df['High'] - df['Low']
        df['ATR'] = df['TR'].rolling(window=14).mean()
        res["atr"] = float(df['ATR'].iloc[-1]) if not pd.isna(df['ATR'].iloc[-1]) else 1.0
        
        last_candle = df.iloc[-1]
        high_p, low_p, open_p, close_p = float(last_candle["High"]), float(last_candle["Low"]), float(last_candle["Open"]), float(last_candle["Close"])
        total_range = high_p - low_p
        body = abs(close_p - open_p)
        upper_shadow = high_p - max(open_p, close_p)
        lower_shadow = min(open_p, close_p) - low_p
        
        if lower_shadow > (body * 2) and lower_shadow > (res["atr"] * 0.4):
            res["shadow_signal"] = "LONG (Lunte)"
        elif upper_shadow > (body * 2) and upper_shadow > (res["atr"] * 0.4):
            res["shadow_signal"] = "SHORT (Docht)"
            
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
        
        dist_to_long = abs(res["cp"] - long_band[-1])
        dist_to_short = abs(res["cp"] - short_band[-1])
        total_band_width = short_band[-1] - long_band[-1]
        
        if current_trend == 1:
            base_chance = 55.0 + ((1.0 - (dist_to_long / (total_band_width + 1e-10))) * 30.0)
            if current_rsi < 45:
                res["infinity_signal"] = "STRONG BUY"
                res["chance"] = base_chance + 10.0
            else:
                res["infinity_signal"] = "BUY"
                res["chance"] = base_chance
        else:
            base_chance = 55.0 + ((1.0 - (dist_to_short / (total_band_width + 1e-10))) * 30.0)
            if current_rsi > 55:
                res["infinity_signal"] = "STRONG SELL"
                res["chance"] = base_chance + 10.0
            else:
                res["infinity_signal"] = "SELL"
                res["chance"] = base_chance
                
        res["chance"] = round(min(max(res["chance"], 51.0), 98.8), 1)
    except Exception:
        pass
    return res

# --- 5. DASHBOARD MAIN LAYOUT ---
st.title("Bio-Trading Monitor Live PRO")

tz_europe = pytz.timezone('Europe/Berlin')
now_fixed = datetime.now(tz_europe).strftime('%H:%M:%S')
st.markdown(f'<div style="color: #8892b0; margin-bottom: 20px;">Letztes Update (Europa/Berlin): <b>{now_fixed}</b> (Intervall: {selected_refresh})</div>', unsafe_allow_html=True)

# --- 6. DATA SCANNER ---
all_signals = []
alerts_list = []

for s in EUROPE_STOCKS[:15]:
    r = get_ticker_analysis(s)
    if r.get("cp", 0) > 0:
        all_signals.append({
            'Aktie': TICKER_NAMES[s], 
            'Kerzen-Schatten': r["shadow_signal"], 
            'Infinity Algo': r["infinity_signal"],
            'Kurs': f"{r['cp']:,.2f}", 
            'Signal-Konfidenz': r["chance"]
        })
        if r["chance"] >= 90.0:
            alerts_list.append(f"{TICKER_NAMES[s]} ({r['chance']}% : {r['infinity_signal']})")

if len(alerts_list) > 0:
    st.markdown(f'<div class="signal-alert">🚨 KRITISCHER ALARM: Hochkonfidenz-Setup erkannt! {" | ".join(alerts_list)}</div>', unsafe_allow_html=True)

# --- 7. MARKTWETTER RENDERN (STABILISIERT DURCH REINE ST.CONTAINER) ---
with st.container():
    res_w1 = get_ticker_analysis("EURUSD=X")
    chg_w1 = res_w1.get("chg", 0.0)
    st.markdown(f'<div class="weather-card" style="border-color:{"#00FFA3" if chg_w1 > 0.15 else ("#1E90FF" if chg_w1 < -0.15 else "#8892b0")};"><b>{TICKER_NAMES["EURUSD=X"]} {"☀️ 🟢" if chg_w1 > 0.15 else ("⛈ 🔵" if chg_w1 < -0.15 else "⚪")}</b> | {res_w1.get("cp", 0.0):,.4f} ({chg_w1:+.2f}%)</div>', unsafe_allow_html=True)

with st.container():
    res_w2 = get_ticker_analysis("^GDAXI")
    chg_w2 = res_w2.get("chg", 0.0)
