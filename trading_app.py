import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from streamlit_autorefresh import st_autorefresh
from datetime import datetime, timedelta

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
    
    # Aktien EUROPA / EUROSTOXX ohne DEU
    # Frankreich (FR)
    "AI.PA": "🇫🇷 Air Liquide", "AIR.PA": "🇫🇷 Airbus", "CS.PA": "🇫🇷 AXA", "BNP.PA": "🇫🇷 BNP Paribas", 
    "BN.PA": "🇫🇷 Danone", "EL.PA": "🇫🇷 EssilorLuxottica", "RMS.PA": "🇫🇷 Hermès",
    "OR.PA": "🇫🇷 L'Oréal", "MC.PA": "🇫🇷 LVMH", "RI.PA": "🇫🇷 Pernod Ricard", "SAF.PA": "🇫🇷 Safran", 
    "SAN.PA": "🇫🇷 Sanofi", "SU.PA": "🇫🇷 Schneider Electric", "TTE.PA": "🇫🇷 TotalEnergies", "DG.PA": "🇫🇷 Vinci",
    
    # Niederlande (NL)
    "ASML.AS": "🇳🇱 ASML Holding", "INGA.AS": "🇳🇱 ING Groep", "PRX.AS": "🇳🇱 Prosus",
    "AD.AS": "🇳🇱 Ahold Delhaize", "STLAM.MI": "🇳🇱 Stellantis",
    
    # Spanien (ES)
    "BBVA.MC": "🇪🇸 BBVA", "IBE.MC": "🇪🇸 Iberdrola", "ITX.MC": "🇪🇸 Inditex", "SAN.MC": "🇪🇸 Banco Santander",
    
    # Italien (IT)
    "ENEL.MI": "🇮🇹 Enel", "ENI.MI": "🇮🇹 Eni", "ISP.MI": "🇮🇹 Intesa Sanpaolo", "RACE.MI": "🇮🇹 Ferrari", "UCG.MI": "🇮🇹 UniCredit",
    
    # Belgien (BE), Irland (IE), Finnland (FI)
    "ABI.BR": "🇧🇪 Anheuser-Busch InBev", "CRH.AS": "🇮🇪 CRH", "FLTR.IR": "🇮🇪 Flutter Entertainment", "NOKIA.HE": "🇫🇮 Nokia",
    
    # Aktien US / NASDAQ
    "AAPL": "🇺🇸 Apple", "MSFT": "🇺🇸 Microsoft", "GOOGL": "🇺🇸 Alphabet (A)", "GOOG": "🇺🇸 Alphabet (C)",
    "AMZN": "🇺🇸 Amazon", "META": "🇺🇸 Meta", "NVDA": "🇺🇸 Nvidia", "TSLA": "🇺🇸 Tesla",
    
    # Halbleiter & Hardware
    "AMD": "🇺🇸 AMD", "AVGO": "🇺🇸 Broadcom", "INTC": "🇺🇸 Intel", "QCOM": "🇺🇸 Qualcomm",
    "TXN": "🇺🇸 Texas Instruments", "AMAT": "🇺🇸 Applied Materials", "LRCX": "🇺🇸 Lam Research",
    "MU": "🇺🇸 Micron", "ADI": "🇺🇸 Analog Devices", "KLAC": "🇺🇸 KLA Corp", "ASML": "🇺🇸 ASML (ADS)",
    "ARM": "🇺🇸 ARM Holdings", "MPWR": "🇺🇸 Monolithic Power", "STX": "🇺🇸 Seagate", "WDC": "🇺🇸 Western Digital",
    
    # Software & Cloud
    "ADBE": "🇺🇸 Adobe", "CRM": "🇺🇸 Salesforce", "ORCL": "🇺🇸 Oracle", "INTU": "🇺🇸 Intuit",
    "PANW": "🇺🇸 Palo Alto", "SNPS": "🇺🇸 Synopsys", "CDNS": "🇺🇸 Cadence", "WDAY": "🇺🇸 Workday",
    "ROP": "🇺🇸 Roper", "ADSK": "🇺🇸 Autodesk", "TEAM": "🇺🇸 Atlassian", "DDOG": "🇺🇸 Datadog",
    "ZS": "🇺🇸 Zscaler", "CRWD": "🇺🇸 CrowdStrike", "PLTR": "🇺🇸 Palantir", "APP": "🇺🇸 AppLovin",
    
    # Internet, Media & E-Commerce
    "NFLX": "🇺🇸 Netflix", "BKNG": "🇺🇸 Booking", "ABNB": "🇺🇸 Airbnb", "PDD": "🇺🇸 PDD Holdings",
    "MELI": "🇺🇸 MercadoLibre", "JD": "🇺🇸 JD.com", "PYPL": "🇺🇸 PayPal", "EBAY": "🇺🇸 eBay",
    "DASH": "🇺🇸 DoorDash", "WBD": "🇺🇸 Warner Bros", "CHTR": "🇺🇸 Charter",
    
    # Healthcare & Biotech
    "AMGN": "🇺🇸 Amgen", "GILD": "🇺🇸 Gilead", "VRTX": "🇺🇸 Vertex", "REGN": "🇺🇸 Regeneron",
    "ISRG": "🇺🇸 Intuitive Surg.", "IDXX": "🇺🇸 IDEXX Labs", "MRNA": "🇺🇸 Moderna", "BIIB": "🇺🇸 Biogen",
    "ALNY": "🇺🇸 Alnyam", "INSM": "🇺🇸 Insmed", "GEHC": "🇺🇸 GE HealthCare",
    
    # Consumer, Retail & Others
    "COST": "🇺🇸 Costco", "PEP": "🇺🇸 PepsiCo", "KO": "🇺🇸 Coca-Cola", "WMT": "🇺🇸 Walmart",
    "SBUX": "🇺🇸 Starbucks", "MDLZ": "🇺🇸 Mondelez", "MNST": "🇺🇸 Monster", "KDP": "🇺🇸 Keurig Dr Pepper",
    "KHC": "🇺🇸 Kraft Heinz", "MAR": "🇺🇸 Marriott", "ORLY": "🇺🇸 O'Reilly", "ROST": "🇺🇸 Ross Stores",
    "LULU": "🇺🇸 Lululemon", "TGT": "🇺🇸 Target", "CSX": "🇺🇸 CSX Corp", "CPRT": "🇺🇸 Copart",
    "FAST": "🇺🇸 Fastenal", "PAYX": "🇺🇸 Paychex", "CTAS": "🇺🇸 Cintas", "ADP": "🇺🇸 ADP",
    "MCHP": "🇺🇸 Microchip", "AXON": "🇺🇸 Axon Enterprise", "FER": "🇺🇸 Ferrovial", "CEG": "🇺🇸 Constellation",
    "ODFL": "🇺🇸 Old Dominion", "ON": "🇺🇸 ON Semi", "EXC": "🇺🇸 Exelon", "BKR": "🇺🇸 Baker Hughes", "TTD": "🇺🇸 Trade Desk",
    "ANSS": "🇺🇸 Ansys", "DLTR": "🇺🇸 Dollar Tree", "DXCM": "🇺🇸 DexCom", "VRSK": "🇺🇸 Verisk"
}

# Filter für Detail-Analyse (Keine Währungen/Indizes)
STOCKS_ONLY = [k for k in TICKER_NAMES.keys() if not k.startswith("^") and not "=X" in k and k != "XU100.IS"]

# STRATEGIE-FILTER: Nur europäische Werte für den Schattenfolge-Monitor extrahieren
EUROPE_STOCKS = [
    k for k in STOCKS_ONLY 
    if any(k.endswith(ext) for ext in [".DE", ".PA", ".AS", ".MI", ".MC", ".BR", ".HE", ".IR"])
]

# --- 3. DESIGN (DARK MODE & KONTRAST) ---
st.markdown("""
 <style>
 /* 1. Haupt-Hintergrund & Basisschrift */
 .stApp { 
 background-color: #0E1117 !important; 
 color: #FFFFFF !important; 
 font-family: 'Inter', sans-serif;
 }
 /* 2. METRIKEN (Kurs, ATR, Chance etc.) */
 [data-testid="stMetricValue"] {
 font-size: 1.5rem !important; 
 font-weight: 800 !important; 
 color: #FFFFFF !important; 
 letter-spacing: -0.5px;
 }
 
 [data-testid="stMetricLabel"] {
 font-size: 0.75rem !important;
 color: #8892b0 !important; 
 text-transform: uppercase !important;
 letter-spacing: 1px !important;
 margin-bottom: -5px !important;
 }
 div[data-testid="stMetric"] {
 background: rgba(255,255,255,0.03);
 border: 1px solid rgba(255,255,255,0.05);
 padding: 8px 12px !important;
 border-radius: 10px;
 }
 /* 3. SPEZIAL-BOX FÜR CRV */
 .crv-box {
 text-align: center;
 border: 1px solid #1E90FF;
 background: rgba(30,144,255,0.1);
 border-radius: 10px;
 padding: 5px;
 height: 100%;
 }
 /* 4. MARKT-WETTER KARTEN */
 .weather-card { 
 text-align: center; 
 border-radius: 12px; 
 background: rgba(255,255,255,0.03); 
 border: 2px solid #333; 
 padding: 12px; 
 margin-bottom: 10px; 
 }
 /* 5. TABELLEN */
 thead tr th { 
 background-color: #2D3748 !important; 
 color: #FFFFFF !important; 
 font-weight: 900 !important; 
 font-size: 0.9rem !important;
 border-bottom: 3px solid #1E90FF !important;
 text-transform: uppercase !important;
 }
 tbody tr td { 
 color: #FFFFFF !important; 
 background-color: #161B22 !important;
 border-bottom: 1px solid #30363D !important;
 font-size: 0.95rem !important;
 }
 /* 6. STATUS-BANNER */
 .status-banner {
 background: rgba(255,255,255,0.03); 
 padding: 12px; 
 border-radius: 12px; 
 border-left: 6px solid #1E90FF; 
 margin-bottom: 15px;
 }
 
 ::-webkit-scrollbar { width: 5px; height: 5px; }
 ::-webkit-scrollbar-thumb { background: #333; border-radius: 10px; }
 </style>
 """, unsafe_allow_html=True)

# --- 4. ZENTRALE FUNKTION ---
@st.cache_data(ttl=60)
def get_analysis(ticker_symbol):
    res = {"cp": 0, "h250": 0, "l250": 0, "chg": 0, "atr": 0, "vol": 0, "chance": 50, "shadow_signal": "NEUTRAL", "df": None}
    
    try:
        tk = yf.Ticker(ticker_symbol)
        df = tk.history(period="1y") 
        
        if not df.empty and len(df) > 1:
            res["cp"] = float(df["Close"].iloc[-1])
            res["vol"] = float(df["Volume"].iloc[-1])
            res["chg"] = ((df["Close"].iloc[-1] / df["Close"].iloc[-2]) - 1) * 100
            
            res["h250"] = float(df["High"].max())
            res["l250"] = float(df["Low"].min())
            
            df['TR'] = df['High'] - df['Low']
            res["atr"] = float(df['TR'].tail(14).mean())
            
            # Standard-Dummy-Chance
            res["chance"] = 54.2 
            res["df"] = df
            
            # --- INTEGRIERTE SCHATTENFOLGE-STRATEGIE (STOP-HUNTING) ---
            last_candle = df.iloc[-1]
            open_p = float(last_candle["Open"])
            close_p = float(last_candle["Close"])
            high_p = float(last_candle["High"])
            low_p = float(last_candle["Low"])
            
            body = abs(close_p - open_p)
            upper_shadow = high_p - max(open_p, close_p)
            lower_shadow = min(open_p, close_p) - low_p
            
            # Filter-Bedingung: Schatten ist mindestens 2x größer als der Körper 
            # und signifikant im Vergleich zur aktuellen ATR
            min_shadow_size = res["atr"] * 0.4
            
            if lower_shadow > (body * 2) and lower_shadow > min_shadow_size:
                res["shadow_signal"] = "LONG (Lunte/Stop-Hunt)"
                res["chance"] = 68.5  # Anpassung der Konfidenz für Rebound-Setup
