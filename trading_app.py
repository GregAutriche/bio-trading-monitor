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

# STRATEGIE-FILTER: Nur europäische Endungen
EUROPE_STOCKS = [
    k for k in STOCKS_ONLY 
    if any(k.endswith(ext) for ext in [".DE", ".PA", ".AS", ".MI", ".MC", ".BR", ".HE", ".IR"])
]

# --- 3. DESIGN (DARK MODE & KONTRAST) ---
st.markdown("""
 <style>
 .stApp { 
 background-color: #0E1117 !important; 
 color: #FFFFFF !important; 
 font-family: 'Inter', sans-serif;
 }
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
 .crv-box {
 text-align: center;
 border: 1px solid #1E90FF;
 background: rgba(30,144,255,0.1);
 border-radius: 10px;
 padding: 5px;
 height: 100%;
 }
 .weather-card { 
 text-align: center; 
 border-radius: 12px; 
 background: rgba(255,255,255,0.03); 
 border: 2px solid #333; 
 padding: 12px; 
 margin-bottom: 10px; 
 }
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
            
            res["chance"] = 54.2 
            res["df"] = df
            
            # --- SCHATTENFOLGE LOGIK ---
            last_candle = df.iloc[-1]
            open_p = float(last_candle["Open"])
            close_p = float(last_candle["Close"])
            high_p = float(last_candle["High"])
            low_p = float(last_candle["Low"])
            
            body = abs(close_p - open_p)
            upper_shadow = high_p - max(open_p, close_p)
            lower_shadow = min(open_p, close_p) - low_p
            
            min_shadow_size = res["atr"] * 0.4
            
            if lower_shadow > (body * 2) and lower_shadow > min_shadow_size:
                res["shadow_signal"] = "LONG (Lunte/Stop-Hunt)"
                res["chance"] = 68.5  
            elif upper_shadow > (body * 2) and upper_shadow > min_shadow_size:
                res["shadow_signal"] = "SHORT (Docht/Abweisung)"
                res["chance"] = 31.5  
                
    except Exception as e:
        print(f"Fehler bei {ticker_symbol}: {e}")
        
    return res

def get_style(chg):
    if chg > 0.15: return "☀️", "#00FFA3", "🟢"
    if chg < -0.15: return "⛈️", "#1E90FF", "🔵"
    return "🌤️", "#8892b0", "⚪"

# --- 5. DASHBOARD AUFBAU ---
st.title("🚀 Bio-Trading Monitor Live PRO")

now_fixed = (datetime.now() + timedelta(hours=1)).strftime('%H:%M:%S')
st.markdown(f"""

5a. MARKT-WETTERWEATHER_ROWS = [["EURUSD=X", "EURRUB=X"],["^GDAXI", "^NDX"],["^STOXX50E", "XU100.IS"]]for row in WEATHER_ROWS:cols = st.columns(len(row))for i, t in enumerate(row):res = get_analysis(t)icon, color, dot = get_style(res["chg"])prec = ".4f" if "=X" in t else ".2f"price_str = f"{res['cp']: ,{prec}}"with cols[i]:st.markdown(f"""{TICKER_NAMES.get(t,t)}{icon}{price_str}{res['chg']:+.2f}%{dot}""", unsafe_allow_html=True)st.divider()5b. TOP 5 AKTIEN CHANCENst.subheader("📊 Top 5 Aktien-Chancen")signals = []failed_scans = []for s in STOCKS_ONLY:r = get_analysis(s)if r["cp"] > 0:_, _, dot = get_style(r["chg"])signals.append({'Status': dot,'Aktie': TICKER_NAMES.get(s,s),'Trend_Val': r["chg"],'Trend': f"{r['chg']:+.2f}%",'Chance': r["chance"]})else:failed_scans.append(TICKER_NAMES.get(s, s))count_de = len([k for k in STOCKS_ONLY if k.endswith(".DE")])count_us = len([k for k in STOCKS_ONLY if not k.endswith(".DE")])st.markdown(f"Info: {count_de} Aktien aus DE / {count_us} Aktien aus US gescannt (Gesamt: {len(STOCKS_ONLY)})", unsafe_allow_html=True)if failed_scans:st.warning(f"Nicht gescannt: {', '.join(failed_scans)}")df_sig = pd.DataFrame(signals)if not df_sig.empty:c_t1, c_t2 = st.columns(2)with c_t1:st.markdown("Top 5 CALL (Chance)", unsafe_allow_html=True)calls = df_sig[df_sig['Trend_Val'] > 0].nlargest(5, 'Chance')st.table(calls[['Status', 'Aktie', 'Trend', 'Chance']])with c_t2:st.markdown("Top 5 PUT (Chance)", unsafe_allow_html=True)puts = df_sig[df_sig['Trend_Val'] < 0].nsmallest(5, 'Chance')st.table(puts[['Status', 'Aktie', 'Trend', 'Chance']])5c. EUROPA SCHATTENFOLGE MONITORst.divider()st.subheader("🇪🇺 Europäischer Schattenfolge-Monitor (Stop-Hunting)")shadow_signals = []for s in EUROPE_STOCKS:r = get_analysis(s)if r["cp"] > 0 and r["shadow_signal"] != "NEUTRAL":shadow_signals.append({'Aktie': TICKER_NAMES.get(s, s),'Formation': r["shadow_signal"],'Kurs': f"{r['cp']:,.2f}",'ATR': f"{r['atr']:,.2f}",'Chance': f"{r['chance']}%"})if shadow_signals:st.dataframe(pd.DataFrame(shadow_signals), use_container_width=True, hide_index=True)else:st.info("Aktuell keine markanten Schatten-Formationen im europäischen Raum erkannt.")5d. DETAIL-ANALYSEst.divider()sorted_stocks = sorted(STOCKS_ONLY, key=lambda x: TICKER_NAMES.get(x, x))sel_stock = st.selectbox("Aktie wählen:", sorted_stocks, format_func=lambda x: TICKER_NAMES.get(x, x))st.subheader(f"🔍 Detail-Analyse: {TICKER_NAMES.get(sel_stock, sel_stock)}")res_d = get_analysis(sel_stock)if res_d.get("cp", 0) > 0:cp = res_d["cp"]atr = res_d["atr"]chance = res_d["chance"]chg = res_d["chg"]h250 = res_d.get("h250", cp)l250 = res_d.get("l250", cp)risk = atr * 1.5reward = risk * 3.0vola_pct = (atr / cp) * 100if res_d["shadow_signal"] != "NEUTRAL":setup_type = f"SCHATTENFOLGE {res_d['shadow_signal']}"setup_color = "#00FFA3" if "LONG" in res_d["shadow_signal"] else "#FF4B4B"else:setup_type, setup_color = ("LONG (CALL)", "#00FFA3") if chance >= 50 else ("SHORT (PUT)", "#FF4B4B")target, stop = (cp + reward, cp - risk) if chance >= 50 else (cp - reward, cp + risk)st.markdown(f"""{setup_type} SETUP AKTIV | {chance}% Konfidenz""", unsafe_allow_html=True)r1c1, r1c2, r1c3, r1c4 = st.columns(4)r1c1.metric("KURS", f"{cp:,.2f}", f"{chg:+.2f}%")r1c2.metric("250-T HOCH", f"{h250:,.2f}")r1c3.metric("250-T TIEF", f"{l250:,.2f}")r1c4.metric("VOLA (ATR %)", f"{vola_pct:.2f}%")r2c1, r2c2, r2c3, r2c4 = st.columns(4)r2c1.metric("CHANCE", f"{chance}%")r2c2.metric("ZIEL (TP)", f"{target:,.2f}")r2c3.metric("STOP (SL)", f"{stop:,.2f}")r2c4.markdown('CRV3.0', unsafe_allow_html=True)try:df_plot = res_d["df"].tail(60).copy()df_plot['x_label'] = df_plot.index.strftime('%d.%m')fig = go.Figure(data=[go.Candlestick(x=df_plot['x_label'], open=df_plot['Open'], high=df_plot['High'],low=df_plot['Low'], close=df_plot['Close'],increasing_line_color='#00FFA3', decreasing_line_color='#FF4B4B')])fig.update_layout(height=450, template="plotly_dark", xaxis_rangeslider_visible=False)st.plotly_chart(fig, use_container_width=True)except Exception as e:st.error(f"Fehler im Chart: {e}")
