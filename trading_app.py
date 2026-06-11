import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- 1. KONFIGURATION & UNTERNEHMENSLISTE ---
st.set_page_config(page_title="Live Market-Maker Flow Monitor", layout="wide")

ASSETS = {
    "DE": {
        "ADS.DE": "Adidas", "AIR.DE": "Airbus", "ALV.DE": "Allianz", "BAS.DE": "BASF",
        "BAYN.DE": "Bayer", "BEI.DE": "Beiersdorf", "BMW.DE": "BMW", "BNR.DE": "Brenntag",
        "CBK.DE": "Commerzbank", "CON.DE": "Continental", "1COV.DE": "Covestro",
        "DTG.DE": "Daimler Truck", "DBK.DE": "Deutsche Bank", "DB1.DE": "Deutsche Börse",
        "DHL.DE": "DHL Group", "DTE.DE": "Deutsche Telekom", "EOAN.DE": "E.ON",
        "FRE.DE": "Fresenius", "FME.DE": "Fresenius Medical Care", "G1A.DE": "GEA Group",
        "HEI.DE": "Heidelberg Materials", "HNR1.DE": "Hannover Rück", "HEN3.DE": "Henkel",
        "IFX.DE": "Infineon", "MBG.DE": "Mercedes-Benz", "MRK.DE": "Merck",
        "MTX.DE": "MTU Aero Engines", "MUV2.DE": "Münchener Rück", "PAH3.DE": "Porsche SE",
        "PUM.DE": "Puma", "QIA.DE": "Qiagen", "RHM.DE": "Rheinmetall", "RWE.DE": "RWE",
        "SAP.DE": "SAP", "SRT3.DE": "Sartorius", "G24.DE": "Scout24", "SIE.DE": "Siemens",
        "ENR.DE": "Siemens Energy", "SHL.DE": "Siemens Healthineers", "SY1.DE": "Symrise",
        "TKA.DE": "Thyssenkrupp", "VOW3.DE": "Volkswagen", "VNA.DE": "Vonovia", "ZAL.DE": "Zalando"
    },
    "US": {
        "AAPL": "Apple", "MSFT": "Microsoft", "GOOGL": "Alphabet (A)", "GOOG": "Alphabet (C)",
        "AMZN": "Amazon", "META": "Meta", "NVDA": "Nvidia", "TSLA": "Tesla",
        "AMD": "AMD", "AVGO": "Broadcom", "INTC": "Intel", "QCOM": "Qualcomm",
        "TXN": "Texas Instruments", "AMAT": "Applied Materials", "LRCX": "Lam Research",
        "MU": "Micron", "ADI": "Analog Devices", "KLAC": "KLA Corp", "ASML": "ASML (ADS)",
        "ARM": "ARM Holdings", "MPWR": "Monolithic Power", "STX": "Seagate", "WDC": "Western Digital",
        "ADBE": "Adobe", "CRM": "Salesforce", "ORCL": "Oracle", "INTU": "Intuit",
        "PANW": "Palo Alto", "SNPS": "Synopsys", "CDNS": "Cadence", "WDAY": "Workday", 
        "ROP": "Roper", "ADSK": "Autodesk", "TEAM": "Atlassian", "DDOG": "Datadog",
        "ZS": "Zscaler", "CRWD": "CrowdStrike", "PLTR": "Palantir", "APP": "AppLovin",
        "NFLX": "Netflix", "BKNG": "Booking", "ABNB": "Airbnb", "PDD": "PDD Holdings",
        "MELI": "MercadoLibre", "JD": "JD.com", "PYPL": "PayPal", "EBAY": "eBay",
        "DASH": "DoorDash", "WBD": "Warner Bros", "CHTR": "Charter",
        "AMGN": "Amgen", "GILD": "Gilead", "VRTX": "Vertex", "REGN": "Regeneron",
        "ISRG": "Intuitive Surg.", "IDXX": "IDEXX Labs", "MRNA": "Moderna", "BIIB": "Biogen",
        "ALNY": "Alnylam", "INSM": "Insmed", "GEHC": "GE HealthCare",
        "COST": "Costco", "PEP": "PepsiCo", "KO": "Coca-Cola", "WMT": "Walmart",
        "SBUX": "Starbucks", "MDLZ": "Mondelez", "MNST": "Monster", "KDP": "Keurig Dr Pepper",
        "KHC": "Kraft Heinz", "MAR": "Marriott", "ORLY": "O'Reilly", "ROST": "Ross Stores",
        "LULU": "Lululemon", "TGT": "Target", "CSX": "CSX Corp", "CPRT": "Copart",
        "FAST": "Fastenal", "PAYX": "Paychex", "CTAS": "Cintas", "ADP": "ADP",
        "MCHP": "Microchip", "AXON": "Axon Enterprise", "FER": "Ferrovial", "CEG": "Constellation",
        "ODFL": "Old Dominion", "ON": "ON Semi", "EXC": "Exelon", "BKR": "Baker Hughes", "TTD": "Trade Desk"
    },
    "EU": {
        "AI.PA": "Air Liquide", "AIR.PA": "Airbus", "CS.PA": "AXA", "BNP.PA": "BNP Paribas",
        "BN.PA": "Danone", "EL.PA": "EssilorLuxottica", "RMS.PA": "Hermès", "OR.PA": "L'Oréal",
        "MC.PA": "LVMH", "RI.PA": "Pernod Ricard", "SAF.PA": "Safran", "SAN.PA": "Sanofi",
        "SU.PA": "Schneider Electric", "TTE.PA": "TotalEnergies", "DG.PA": "Vinci",
        "ASML.AS": "ASML Holding", "INGA.AS": "ING Groep", "PRX.AS": "Prosus", "AD.AS": "Ahold Delhaize",
        "STLAM.MI": "Stellantis", "BBVA.MC": "BBVA", "IBE.MC": "Iberdrola", "ITX.MC": "Inditex",
        "SAN.MC": "Banco Santander", "ENEL.MI": "Enel", "ENI.MI": "Eni", "ISP.MI": "Intesa Sanpaolo",
        "RACE.MI": "Ferrari", "UCG.MI": "UniCredit", "ABI.BR": "Anheuser-Busch InBev",
        "CRH.AS": "CRH", "FLTR.IR": "Flutter Entertainment", "NOKIA.HE": "Nokia"
    }
}

TICKER_TO_NAME = {ticker: name for region in ASSETS.values() for ticker, name in region.items()}
ALL_TICKERS = list(TICKER_TO_NAME.keys())
INDEX_MAP = {"^GDAXI": "DAX", "^STOXX50E": "EUROSTOXX 50", "^IXIC": "NASDAQ"}

# --- 2. HILFSFUNKTIONEN & SICHERHEITSELEMENTE ---
def safe_float(val):
    if isinstance(val, (pd.Series, np.ndarray, pd.DataFrame)):
        return float(val.iloc[-1]) if hasattr(val, 'iloc') else float(val[0])
    return float(val)

def get_logic_icons(chg):
    chg = safe_float(chg)
    weather = "☀️" if chg > 0.5 else "⛈️" if chg < -0.5 else "☁️"
    dot = "🟢" if chg > 0.4 else "🔴" if chg < -0.4 else "⚪"
    return weather, dot

@st.cache_data(ttl=300)
def get_live_data(ticker, period="60d", interval="1d"):
    try:
        # multi_level_index=False zwingt yfinance zu klassischen, flachen Spalten
        df = yf.download(ticker, period=period, interval=interval, progress=False, multi_level_index=False)
        
        if df is not None and not df.empty:
            # Sicherheitsnetz: Falls Spalten trotzdem ein MultiIndex sind, plattmachen
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            return df
        return None
    except Exception as e:
        # Hilfreich für das Streamlit-Protokoll im Hintergrund
        print(f"Fehler beim Laden von {ticker}: {e}")
        return None

# --- 3. CORE LOGIC: MARKET MAKER & INSTITUTIONAL FLOW ---
def analyze_market_maker_flow(ticker, df):
    cp = safe_float(df['Close'].iloc[-1])
    prev_3d = safe_float(df['Close'].iloc[-4])
    chg_3d = ((cp / prev_3d) - 1) * 100
    
    # 1. Volatilität (ATR) für Market-Maker-Spreads
    df['TR'] = np.maximum(df['High'] - df['Low'], np.maximum(abs(df['High'] - df['Close'].shift(1)), abs(df['Low'] - df['Close'].shift(1))))
    atr = safe_float(df['TR'].tail(14).mean())
    
    # 2. Institutionelles Volumen tracken (Volumen-Ausbruch)
    df['Vol_SMA20'] = df['Volume'].rolling(window=20).mean()
    current_vol = safe_float(df['Volume'].iloc[-1])
    avg_vol = safe_float(df['Vol_SMA20'].iloc[-1])
    high_volume_break = current_vol > (avg_vol * 1.5)  # 50% über dem Durchschnitt
    
    # 3. Liquiditäts-Pools definieren (20-Tage Hochs/Tiefs der Retail-Stops)
    liquidity_pool_high = safe_float(df['High'].tail(20).max())
    liquidity_pool_low = safe_float(df['Low'].tail(20).min())
    
    # 4. Distanz zu den Liquiditäts-Zonen berechnen
    dist_to_low = (cp - liquidity_pool_low) / cp
    dist_to_high = (liquidity_pool_high - cp) / cp
    
    # 5. Signal-Generierung nach Market-Maker-Verhalten
    # CALL: Kurs holt Stops am Tief ab + hohes institutionelles Kaufvolumen (Absorption)
    if dist_to_low < 0.02 and high_volume_break:
        direction = 1  # INSTITUTIONAL CALL
        chance = 75.0 + (abs(chg_3d) * 0.1)
        signal_type = "Liquidity Grab (Buy)"
    # PUT: Kurs holt Stops am Hoch ab + hohes institutionelles Verkaufsvolumen (Distribution)
    elif dist_to_high < 0.02 and high_volume_break:
        direction = -1  # INSTITUTIONAL PUT
        chance = 70.0 + (abs(chg_3d) * 0.1)
        signal_type = "Liquidity Grab (Sell)"
    else:
        # Standard Orderflow-Trendfolge bei normaler Liquidität
        direction = 1 if chg_3d > 0 else -1
        chance = 45.0 + (abs(chg_3d) * 0.2)
        signal_type = "Standard Order Flow"
        
    weather, dot = get_logic_icons(chg_3d)
    
    return {
        "cp": cp, "chg_3d": chg_3d, "atr": atr, "weather": weather, 
        "dot": dot, "chance": chance, "direction": direction, "df": df,
        "pool_high": liquidity_pool_high, "pool_low": liquidity_pool_low, "type": signal_type
    }

# --- 4. HEADER: FX INDIKATION ---
eurusd_df = get_live_data("EURUSD=X", period="5d")
if eurusd_df is not None:
    cp = safe_float(eurusd_df['Close'].iloc[-1])
    prev = safe_float(eurusd_df['Close'].iloc[-2])
    chg = ((cp / prev) - 1) * 100
    w, dot = get_logic_icons(chg)
    st.markdown(f"<h1 style='text-align: center; color: #5DADE2;'>{w} EUR / USD: {cp:.5f} {dot}</h1>", unsafe_allow_html=True)

st.divider()

# --- 5. GLOBALE INDIZES ---
st.subheader("🌐 Globale Markt-Indikation")
idx_keys = list(INDEX_MAP.keys())
r1 = st.columns(3)
for i in range(3):
    sym = idx_keys[i]
    df = get_live_data(sym, period="5d")
    if df is not None:
        cp = safe_float(df['Close'].iloc[-1])
        prev = safe_float(df['Close'].iloc[-2])
        chg = ((cp / prev) - 1) * 100
        w, dot = get_logic_icons(chg)
        r1[i].metric(f"{w} {INDEX_MAP[sym]}", f"{cp:,.2f}", f"{dot} {chg:.2f}%", delta_color="normal" if chg >= 0 else "inverse")

st.divider()

# --- 6. TOP 7 MARKET MAKER CHANCEN (LIQUIDITY TRACKER) ---
st.subheader("🎯 Top 7 Institutionelle Liquiditäts-Chancen")
rank_list = []
for t in ALL_TICKERS:
    df = get_live_data(t, period="60d")
    if df is not None and len(df) > 20:
        res = analyze_market_maker_flow(t, df)
        # Wir filtern primär nach echten "Liquidity Grabs" für die Top-Liste
        if "Grab" in res["type"]:
            rank_list.append({
                "Aktie": f"{res['weather']} {TICKER_TO_NAME[t]}", 
                "MM-Setup": res["type"],
                "Signal": f"{res['dot']} {'CALL' if res['direction'] == 1 else 'PUT'}", 
                "Konfidenz (%)": f"{res['chance']:.2f}", 
                "Trend 3D": f"{res['chg_3d']:.2f}%", 
                "Kurs": f"{res['cp']:.2f} €"
            })

if rank_list:
    st.table(pd.DataFrame(rank_list).sort_values(by="Konfidenz (%)", ascending=False).head(7))
else:
    st.info("Aktuell keine scharfen Liquidity-Grabs an den Extrempunkten. Es gelten Standard-Orderflows.")

st.divider()

# --- 7. DETAIL-ANALYSE & INSTITUTIONELLES ORDER-TICKET ---
reg = st.radio("Region auswählen:", ["DE", "US", "EU"], horizontal=True)
sel = st.selectbox("Aktie analysieren:", list(ASSETS[reg].keys()), format_func=lambda x: ASSETS[reg][x])

df_sel = get_live_data(sel, period="60d")
if df_sel is not None and len(df_sel) > 20:
    det = analyze_market_maker_flow(sel, df_sel)
    direction = det['direction']
    
