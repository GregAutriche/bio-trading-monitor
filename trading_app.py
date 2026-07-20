import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
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
 .crv-box { text-align: center; border: 1px solid #1E90FF; background: rgba(30,144,255,0.1); border-radius: 10px; padding: 5px; height: 100%; }
 .weather-card { text-align: center; border-radius: 12px; background: rgba(255,255,255,0.03); border: 2px solid #333; padding: 12px; margin-bottom: 10px; }
 </style>
 """, unsafe_allow_html=True)

# --- 4. ZENTRALE FUNKTION ---
@st.cache_data(ttl=300)
def get_analysis(ticker_symbol):
    res = {"cp": 0, "h250": 0, "l250": 0, "chg": 0, "atr": 0, "vol": 0, "chance": 50.0, "shadow_signal": "NEUTRAL", "df": None}
    try:
        df = yf.download(ticker_symbol, period="1y", progress=False, group_by="ticker")
        if not df.empty and len(df) > 1:
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.droplevel(0)
            
            res["cp"] = float(df["Close"].iloc[-1])
            res["vol"] = float(df["Volume"].iloc[-1])
            res["chg"] = ((df["Close"].iloc[-1] / df["Close"].iloc[-2]) - 1) * 100
            res["h250"] = float(df["High"].max())
            res["l250"] = float(df["Low"].min())
            
            df['TR'] = df['High'] - df['Low']
            res["atr"] = float(df['TR'].tail(14).mean())
            res["df"] = df
            
            # --- SCHATTENFOLGE-LOGIK MIT INTUITIVER SIGNALSTÄRKE ---
            last_candle = df.iloc[-1]
            high_p = float(last_candle["High"])
            low_p = float(last_candle["Low"])
            open_p = float(last_candle["Open"])
            close_p = float(last_candle["Close"])
            
            total_range = high_p - low_p
            body = abs(close_p - open_p)
            upper_shadow = high_p - max(open_p, close_p)
            lower_shadow = min(open_p, close_p) - low_p
            
            min_shadow_size = res["atr"] * 0.4
            
            if total_range > 0:
                shadow_ratio = max(upper_shadow, lower_shadow) / total_range
                # Skalierung der Signalstärke (55% bis 85%) je ausgeprägter der Schatten ist
                signal_strength = 55.0 + (shadow_ratio * 30.0)
            else:
                signal_strength = 54.2
            
            if lower_shadow > (body * 2) and lower_shadow > min_shadow_size:
                res["shadow_signal"] = "LONG (Lunte)"
                res["chance"] = round(signal_strength, 1)  # Höhere Zahl = Extremerer Liquiditätsabgriff unten
            elif upper_shadow > (body * 2) and upper_shadow > min_shadow_size:
                res["shadow_signal"] = "SHORT (Docht)"
                res["chance"] = round(signal_strength, 1)  # Höhere Zahl = Extremere Kursabweisung oben
            else:
                res["chance"] = 54.2
                
    except Exception:
        pass
    return res

def get_style(chg):
    if chg > 0.15: return "☀️", "#00FFA3", "🟢"
    if chg < -0.15: return "⛈️", "#1E90FF", "🔵"
    return "🌤️", "#8892b0", "⚪"

# --- 5. DASHBOARD AUFBAU ---
st.title("🚀 Bio-Trading Monitor Live PRO")

now_fixed = (datetime.now() + timedelta(hours=1)).strftime('%H:%M:%S')
st.markdown(f'<div style="color: #8892b0; margin-bottom: 20px;">Letztes Update: <b>{now_fixed}</b></div>', unsafe_allow_html=True)

# 5a. MARKT-WETTER
WEATHER_ROWS = [["EURUSD=X", "^GDAXI", "^NDX"], ["^STOXX50E", "XU100.IS"]]
for row in WEATHER_ROWS:
    cols = st.columns(len(row))
    for i, t in enumerate(row):
        res = get_analysis(t)
        if res["cp"] > 0:
            icon, color, _ = get_style(res["chg"])
            st.markdown(f'<div class="weather-card" style="border-color:{color};"><b>{TICKER_NAMES.get(t,t)} {icon}</b><br>{res["cp"]:,.2f} ({res["chg"]:+.2f}%)</div>', unsafe_allow_html=True)

# 5b. DETAIL-ANALYSE
st.divider()
sorted_stocks = sorted(STOCKS_ONLY, key=lambda x: TICKER_NAMES.get(x, x))
sel_stock = st.selectbox("Aktie für Detail-Analyse wählen:", sorted_stocks, format_func=lambda x: TICKER_NAMES.get(x, x))

res_d = get_analysis(sel_stock)
if res_d["cp"] > 0:
    st.subheader(f"🔍 Detail-Analyse: {TICKER_NAMES.get(sel_stock, sel_stock)}")
    cp, atr, chance, chg = res_d["cp"], res_d["atr"], res_d["chance"], res_d["chg"]
    h250, l250 = res_d["h250"], res_d["l250"]
    
    if res_d["shadow_signal"] != "NEUTRAL":
        setup_type = f"SCHATTENFOLGE {res_d['shadow_signal']}"
        setup_color = "#00FFA3" if "LONG" in setup_type else "#FF4B4B"
    else:
        setup_type = "LONG (CALL)" if chance >= 50 else "SHORT (PUT)"
        setup_color = "#00FFA3" if chance >= 50 else "#FF4B4B"
    
    st.markdown(f'<div style="background:rgba(255,255,255,0.03); padding:12px; border-radius:10px; border-left:6px solid {setup_color}; margin-bottom:15px;"><b>{setup_type} SETUP</b> | {chance}% Signal-Konfidenz</div>', unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("KURS", f"{cp:,.2f}", f"{chg:+.2f}%")
    c2.metric("250-T HOCH", f"{h250:,.2f}")
    c3.metric("250-T TIEF", f"{l250:,.2f}")
    c4.metric("ATR (14)", f"{atr:,.2f}")

# 5c. EUROPA SCHATTENFOLGE MONITOR
st.divider()
st.subheader("🇪🇺 Europäischer Schattenfolge-Monitor (Top Werte)")
shadow_signals = []

for s in EUROPE_STOCKS[:15]:
    r = get_analysis(s)
    if r["cp"] > 0 and r["shadow_signal"] != "NEUTRAL":
        shadow_signals.append({
            'Aktie': TICKER_NAMES.get(s, s), 
            'Signal': r["shadow_signal"], 
            'Kurs': f"{r['cp']:,.2f}", 
            'Signalstärke (Chance)': f"{r['chance']}%"
        })

if shadow_signals:
    st.dataframe(pd.DataFrame(shadow_signals), use_container_width=True, hide_index=True)
else:
    st.info("Aktuell keine markanten Kerzenschatten im primären europäischen Raum erkannt.")
