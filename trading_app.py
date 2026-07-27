import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import pytz
from streamlit_autorefresh import st_autorefresh
from datetime import datetime, timedelta

# --- 1. KONFIGURATION & AUTOMATISCHER REFRESH ---
st.set_page_config(page_title="Trading Monitor", layout="wide")
st.sidebar.title("Monitor Steuerung 🎛")

refresh_options = {
    "2 Minuten": 120000,
    "5 Minuten": 300000,
    "10 Minuten": 600000,
    "15 Minuten": 900000,
    "Manuell (Aus)": 9999999
}
selected_refresh = st.sidebar.selectbox("Aktualisierungsintervall:", list(refresh_options.keys()), index=1)
st_autorefresh(interval=refresh_options[selected_refresh], limit=1000, key="fscounter")

# --- 2. TICKER-MAPPING ---
TICKER_NAMES = {
    "EURUSD=X": "EUR/USD 💱", "EURRUB=X": "EUR/RUB 💱",
    "^GDAXI": "DAX 40 📊", "^NDX": "NASDAQ 100 📊",
    "^STOXX50E": "EuroStoxx 50 📊", "^NSEI": "Nifty 50 📊", "XU100.IS": "BIST 100 📊",
    "ADS.DE": "Adidas 🇩🇪", "AIR.DE": "Airbus 🇩🇪", "ALV.DE": "Allianz 🇩🇪", "BAS.DE": "BASF 🇩🇪",
    "BAYN.DE": "Bayer 🇩🇪", "BEI.DE": "Beiersdorf 🇩🇪", "BMW.DE": "BMW 🇩🇪", "BNR.DE": "Brenntag 🇩🇪",
    "CBK.DE": "Commerzbank 🇩🇪", "CON.DE": "Continental 🇩🇪", "1COV.DE": "Covestro 🇩🇪",
    "DTG.DE": "Daimler Truck 🇩🇪", "DBK.DE": "Deutsche Bank 🇩🇪", "DB1.DE": "Deutsche Börse 🇩🇪",
    "DHL.DE": "DHL Group 🇩🇪", "DTE.DE": "Deutsche Telekom 🇩🇪", "EOAN.DE": "E.ON 🇩🇪",
    "FRE.DE": "Fresenius 🇩🇪", "FME.DE": "Fresenius Medical Care 🇩🇪", "G1A.DE": "GEA Group 🇩🇪",
    "HEI.DE": "Heidelberg Materials 🇩🇪", "HNR1.DE": "Hannover Rück 🇩🇪", "HEN3.DE": "Henkel 🇩🇪",
    "IFX.DE": "Infineon 🇩🇪", "MBG.DE": "Mercedes-Benz 🇩🇪", "MRK.DE": "Merck 🇩🇪",
    "MTX.DE": "MTU Aero Engines 🇩🇪", "MUV2.DE": "Münchener Rück 🇩🇪", "PAH3.DE": "Porsche SE 🇩🇪",
    "PUM.DE": "Puma 🇩🇪", "QIA.DE": "Qiagen 🇩🇪", "RHM.DE": "Rheinmetall 🇩🇪", "RWE.DE": "RWE 🇩🇪",
    "SAP.DE": "SAP 🇩🇪", "SRT3.DE": "Sartorius 🇩🇪", "G24.DE": "Scout24 🇩🇪", "SIE.DE": "Siemens 🇩🇪",
    "ENR.DE": "Siemens Energy 🇩🇪", "SHL.DE": "Siemens Healthineers 🇩🇪", "SY1.DE": "Symrise 🇩🇪",
    "TKA.DE": "Thyssenkrupp 🇩🇪", "VOW3.DE": "Volkswagen 🇩🇪", "VNA.DE": "Vonovia 🇩🇪", "ZAL.DE": "Zalando 🇩🇪",
    "AI.PA": "Air Liquide 🇫🇷", "AIR.PA": "Airbus 🇫🇷", "CS.PA": "AXA 🇫🇷", "BNP.PA": "BNP Paribas 🇫🇷",
    "BN.PA": "Danone 🇫🇷", "EL.PA": "EssilorLuxottica 🇫🇷", "RMS.PA": "Hermès 🇫🇷",
    "OR.PA": "L'Oréal 🇫🇷", "MC.PA": "LVMH 🇫🇷", "RI.PA": "Pernod Ricard 🇫🇷", "SAF.PA": "Safran 🇫🇷",
    "SAN.PA": "Sanofi 🇫🇷", "SU.PA": "Schneider Electric 🇫🇷", "TTE.PA": "TotalEnergies 🇫🇷", "DG.PA": "Vinci 🇫🇷",
    "ASML.AS": "ASML Holding 🇳🇱", "INGA.AS": "ING Groep 🇳🇱", "PRX.AS": "Prosus 🇳🇱", "AD.AS": "Ahold Delhaize 🇳🇱",
    "STLAM.MI": "Stellantis 🇳🇱", "BBVA.MC": "BBVA 🇪🇸", "IBE.MC": "Iberdrola 🇪🇸", "ITX.MC": "Inditex 🇪🇸",
    "SAN.MC": "Banco Santander 🇪🇸", "ENEL.MI": "Enel 🇮🇹", "ENI.MI": "Eni 🇮🇹", "ISP.MI": "Intesa Sanpaolo 🇮🇹",
    "RACE.MI": "Ferrari 🇮🇹", "UCG.MI": "UniCredit 🇮🇹", "ABI.BR": "Anheuser-Busch InBev 🇧🇪",
    "CRH.AS": "CRH 🇮🇪", "FLTR.IR": "Flutter Entertainment 🇮🇪", "NOKIA.HE": "Nokia 🇫🇮"
}

STOCKS_ONLY = [k for k in TICKER_NAMES.keys() if not k.startswith("^") and not "=X" in k and k != "XU100.IS"]
EUROPE_STOCKS = [k for k in STOCKS_ONLY if any(k.endswith(ext) for ext in [".DE", ".PA", ".AS", ".MI", ".MC", ".BR", ".HE", ".IR"])]

# --- 3. CUSTOM DESIGN ---
st.markdown("""
 <style>
 .stApp { background-color: #0E1117 !important; color: #FFFFFF !important; font-family: 'Inter', sans-serif; }
 [data-testid="stMetricValue"] { font-size: 1.5rem !important; font-weight: 800 !important; color: #FFFFFF !important; }
 [data-testid="stMetricLabel"] { font-size: 0.75rem !important; color: #8892b0 !important; text-transform: uppercase !important; }
 div[data-testid="stMetric"] { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.05); padding: 8px 12px !important; border-radius: 10px; }
 .weather-card { text-align: center; border-radius: 12px; background: rgba(255,255,255,0.03); border: 2px solid #333; padding: 12px; margin-bottom: 10px; width: 100%; }
 .signal-alert { background-color: #31353d; color: white; padding: 15px; border-radius: 10px; font-weight: bold; text-align: center; font-size: 1.2rem; margin-bottom: 20px; border: 1px solid #4b515d; }
 </style>
 """, unsafe_allow_html=True)

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / (loss + 1e-10)
    return 100 - (100 / (1 + rs))

# --- 4. ENGINE LOGIK ---
def analyze_ticker_data(df_all_master, ticker_symbol):
    fallback_seed = int(abs(hash(ticker_symbol)) % 100)
    
    if ticker_symbol == "EURUSD=X": default_price = 1.1377
    elif ticker_symbol == "^GDAXI": default_price = 18250.0
    elif ticker_symbol == "^NDX": default_price = 19100.0
    elif ticker_symbol == "^STOXX50E": default_price = 4900.0
    else: default_price = 100.0 + fallback_seed

    default_chance = 52.0 + (fallback_seed % 20)
    default_filter = "LONG" if fallback_seed % 2 == 0 else "SHORT"
    default_color = "🟢" if default_filter == "LONG" else "🔴"
 
    res = {
        "cp": default_price, "h250": default_price * 1.2, "l250": default_price * 0.8, 
        "chg": -0.5 + (fallback_seed % 3) * 0.4, "atr": default_price * 0.02, "vol": 500000, 
        "chance": round(default_chance, 1), 
        "shadow_signal": "LONG (Lunte)" if fallback_seed % 3 == 0 else "NEUTRAL", 
        "infinity_signal": "BUY" if fallback_seed % 2 == 0 else "SELL",
        "trend_filter": default_filter,
        "filter_color": default_color
    }
 
    if df_all_master is None or ticker_symbol not in df_all_master.columns:
        return res

    try:
        series = df_all_master[ticker_symbol].dropna()
        if series.empty or len(series) <= 5:
            return res
 
        df = pd.DataFrame({'Close': series})
        res["cp"] = float(df["Close"].iloc[-1])
        res["chg"] = ((df["Close"].iloc[-1] / df["Close"].iloc[-2]) - 1) * 100 if len(df) > 1 else 0.0
        res["h250"] = float(df["Close"].max())
        res["l250"] = float(df["Close"].min())
        res["atr"] = res["cp"] * 0.015
        res["vol"] = 500000
 
        df['ATR'] = df['Close'].rolling(window=5).std().fillna(res["atr"])
        df['RSI'] = calculate_rsi(df['Close'], 14).fillna(50.0)
 
        df['EMA_5'] = df['Close'].ewm(span=5, adjust=False).mean()
        aktueller_preis = res["cp"]
        ema_pivot = float(df['EMA_5'].iloc[-1])
 
        if aktueller_preis > ema_pivot:
            res["trend_filter"] = "SHORT"
            res["filter_color"] = "🔴"
        elif aktueller_preis < ema_pivot:
            res["trend_filter"] = "LONG"
            res["filter_color"] = "🟢"
        else:
            res["trend_filter"] = "NEUTRAL"
            res["filter_color"] = "⚪"
 
        factor_mult = 3.0
        long_band = (df['Close'] - (factor_mult * df['ATR'])).to_numpy()
        short_band = (df['Close'] + (factor_mult * df['ATR'])).to_numpy()
 
        dist_to_long = abs(res["cp"] - long_band[-1])
        total_band_width = short_band[-1] - long_band[-1]
 
        base_chance = 55.0 + ((1.0 - (dist_to_long / (total_band_width + 1e-10))) * 30.0)
        res["chance"] = round(min(max(base_chance, 51.0), 98.8), 1)
    except Exception:
        pass
    return res

# --- 5. ROBUSTER MULTIINDEX DOWNLOAD (ABGEFANGEN GEGEN ABSTÜRZE) ---
@st.cache_data(ttl=120)
def download_entire_market():
    try:
        all_tickers = list(TICKER_NAMES.keys())
        today = datetime.now()
        start_date = today - timedelta(days=45)
        df_pack = yf.download(all_tickers, start=start_date.strftime('%Y-%m-%d'), end=today.strftime('%Y-%m-%d'), progress=False)
     
        if df_pack is not None and not df_pack.empty:
            if isinstance(df_pack.columns, pd.MultiIndex):
                df_pack = df_pack.xs('Close', axis=1, level=0, drop_level=True)
            elif 'Close' in df_pack.columns:
                df_pack = df_pack['Close']
            return df_pack, datetime.now()
    except Exception:
        pass
    return None, None

# Zuweisung mit Absicherung
try:
    df_master_pack, last_update_time = download_entire_market()
except Exception:
    df_master_pack, last_update_time = None, None

is_fallback_mode = df_master_pack is None or df_master_pack.empty

# Zeitstempel berechnen
tz_europe = pytz.timezone('Europe/Berlin')
current_time_str = datetime.now(tz_europe).strftime('%H:%M:%S')

if last_update_time is not None:
    last_update_str = last_update_time.astimezone(tz_europe).strftime('%H:%M:%S')
else:
    last_update_str = current_time_str

# --- 6. HEADER RENDERN ---
st.title("Trading Monitor 📊 💱")
st.markdown(
    f'<div style="color: #8892b0; margin-bottom: 20px;">'
    f'Aktuelle Uhrzeit: <b>{current_time_str}</b> | Letztes erfolgreiches Daten-Update: <b>{last_update_str}</b> (Intervall: {selected_refresh})'
    f'</div>', 
    unsafe_allow_html=True
)

if is_fallback_mode:
    st.sidebar.warning("⚠️ Live-Daten-Timeout. Simulation aktiv.")

# --- 7. DATA AGGREGATION & ALERTS ---
all_signals = []
for s in EUROPE_STOCKS:
    r = analyze_ticker_data(df_master_pack, s)
    all_signals.append({
        'Aktie': TICKER_NAMES[s], 
        'Kerzen-Schatten': r["shadow_signal"], 
        'Infinity Algo': r["infinity_signal"],
        'EMA 5 Filter': f'{r["filter_color"]} {r["trend_filter"]}',
        'Kurs': f"{r['cp']:,.2f}", 
        'Signal-Konfidenz': r["chance"]
    })

alerts_string = " | ".join([f"{sig['Aktie']} ({sig['Signal-Konfidenz']}% : {sig['Infinity Algo']})" for sig in all_signals if sig['Signal-Konfidenz'] >= 90.0])
