import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta  # Für technische Indikatoren (pip install pandas_ta)
from datetime import datetime

# --- 1. KONFIGURATION ---
st.set_page_config(page_title="Trading-Scanner Pro", layout="wide")
last_update = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
st.markdown(f"<p style='text-align: right; color: gray;'>Update: {last_update}</p>", unsafe_allow_html=True)

st.title("🚀 Tradingchancen-Rechner mit Wahrscheinlichkeit")

# --- 2. SIDEBAR ---
st.sidebar.header("Parameter")
risiko_eur = st.sidebar.number_input("Risiko pro Trade (EUR)", value=500)
intervall = st.sidebar.selectbox("Intervall", ["1d", "1h", "15m", "5m"], index=0)

# --- 3. TICKER-LISTEN ---
indices = {"^GDAXI": "DAX", "^IXIC": "NASDAQ", "^STOXX50E": "EURO STOXX 50", "^NSEI": "NIFTY 50", "XU100.IS": "BIST 100"}
forex = {"EURUSD=X": "EUR/USD"}
stocks = {"ADS.DE": "🇩🇪 Adidas", "AIR.DE": "🇩🇪 Airbus", "ALV.DE": "🇩🇪 Allianz", "BAS.DE": "🇩🇪 BASF",
    "BAYN.DE": "🇩🇪 Bayer", "BEI.DE": "🇩🇪 Beiersdorf", "BMW.DE": "🇩🇪 BMW", "BNR.DE": "🇩🇪 Brenntag",
    "CBK.DE": "🇩🇪 Commerzbank", "CON.DE": "🇩🇪 Continental", "1COV.DE": "🇩🇪 Covestro",
    "DTG.DE": "🇩🇪 Daimler Truck", "DBK.DE": "🇩🇪 Deutsche Bank", "DB1.DE": "🇩🇪 Deutsche Börse",
    "DHL.DE": "🇩🇪 DHL Group", "DTE.DE": "🇩🇪 Deutsche Telekom", "EOAN.DE": "🇩🇪 E.ON",
    "FRE.DE": "🇩🇪 Fresenius", "FME.DE": "🇩🇪 Fresenius Medical Care", "G1A.DE": "🇩🇪 GEA Group", "HEI.DE": "🇩🇪 Heidelberg Materials", "HNR1.DE": "🇩🇪 Hannover Rück", "HEN3.DE": "🇩🇪 Henkel", "IFX.DE": "🇩🇪 Infineon", "MBG.DE": "🇩🇪 Mercedes-Benz", "MRK.DE": "🇩🇪 Merck",
    "MTX.DE": "🇩🇪 MTU Aero Engines", "MUV2.DE": "🇩🇪 Münchener Rück", "PAH3.DE": "🇩🇪 Porsche SE",
    "PUM.DE": "🇩🇪 Puma", "QIA.DE": "🇩🇪 Qiagen", "RHM.DE": "🇩🇪 Rheinmetall", "RWE.DE": "🇩🇪 RWE",
    "SAP.DE": "🇩🇪 SAP", "SRT3.DE": "🇩🇪 Sartorius", "G24.DE": "🇩🇪 Scout24", "SIE.DE": "🇩🇪 Siemens", "ENR.DE": "🇩🇪 Siemens Energy", "SHL.DE": "🇩🇪 Siemens Healthineers", "SY1.DE": "🇩🇪 Symrise",
    "TKA.DE": "🇩🇪 Thyssenkrupp", "VOW3.DE": "🇩🇪 Volkswagen", "VNA.DE": "🇩🇪 Vonovia", "ZAL.DE": "🇩🇪 Zalando",

# Aktien EUROPA / EUROSTOXX ohne DEU
     # Frankreich (🇫🇷)
    "AI.PA": "🇫🇷 Air Liquide", "AIR.PA": "🇫🇷 Airbus", "CS.PA": "🇫🇷 AXA", "BNP.PA": "🇫🇷 BNP Paribas",  "BN.PA": "🇫🇷 Danone", "EL.PA": "🇫🇷 EssilorLuxottica", "RMS.PA": "🇫🇷 Hermès", "OR.PA": "🇫🇷 L'Oréal", "MC.PA": "🇫🇷 LVMH", "RI.PA": "🇫🇷 Pernod Ricard", "SAF.PA": "🇫🇷 Safran", "SAN.PA": "🇫🇷 Sanofi", "SU.PA": "🇫🇷 Schneider Electric", "TTE.PA": "🇫🇷 TotalEnergies", "DG.PA": "🇫🇷 Vinci",
    # Niederlande (🇳🇱)
    "ASML.AS": "🇳🇱 ASML Holding", "INGA.AS": "🇳🇱 ING Groep", "PRX.AS": "🇳🇱 Prosus", "AD.AS": "🇳🇱 Ahold Delhaize", "STLAM.MI": "🇳🇱 Stellantis", # (Stellantis oft via Mailand)
    # Spanien (🇪🇸)
    "BBVA.MC": "🇪🇸 BBVA", "IBE.MC": "🇪🇸 Iberdrola", "ITX.MC": "🇪🇸 Inditex", "SAN.MC": "🇪🇸 Banco Santander",
    # Italien (🇮🇹)
    "ENEL.MI": "🇮🇹 Enel", "ENI.MI": "🇮🇹 Eni", "ISP.MI": "🇮🇹 Intesa Sanpaolo", "RACE.MI": "🇮🇹 Ferrari", "UCG.MI": "🇮🇹 UniCredit",
    # Belgien (🇧🇪), Irland (🇮🇪), Finnland (🇫🇮)
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
    "DASH": "🇺🇸 DoorDash", "GOOG": "🇺🇸 Alphabet", "WBD": "🇺🇸 Warner Bros", "CHTR": "🇺🇸 Charter",
    # Healthcare & Biotech
    "AMGN": "🇺🇸 Amgen", "GILD": "🇺🇸 Gilead", "VRTX": "🇺🇸 Vertex", "REGN": "🇺🇸 Regeneron", 
    "ISRG": "🇺🇸 Intuitive Surg.", "IDXX": "🇺🇸 IDEXX Labs", "MRNA": "🇺🇸 Moderna", "BIIB": "🇺🇸 Biogen",
    "ALNY": "🇺🇸 Alnylam", "INSM": "🇺🇸 Insmed", "GEHC": "🇺🇸 GE HealthCare",
    # Consumer, Retail & Others
    "COST": "🇺🇸 Costco", "PEP": "🇺🇸 PepsiCo", "KO": "🇺🇸 Coca-Cola", "WMT": "🇺🇸 Walmart",
    "SBUX": "🇺🇸 Starbucks", "MDLZ": "🇺🇸 Mondelez", "MNST": "🇺🇸 Monster", "KDP": "🇺🇸 Keurig Dr Pepper",
    "KHC": "🇺🇸 Kraft Heinz", "MAR": "🇺🇸 Marriott", "ORLY": "🇺🇸 O'Reilly", "ROST": "🇺🇸 Ross Stores",
    "LULU": "🇺🇸 Lululemon", "TGT": "🇺🇸 Target", "CSX": "🇺🇸 CSX Corp", "CPRT": "🇺🇸 Copart",
    "FAST": "🇺🇸 Fastenal", "PAYX": "🇺🇸 Paychex", "CTAS": "🇺🇸 Cintas", "ADP": "🇺🇸 ADP",
    "MCHP": "🇺🇸 Microchip", "AXON": "🇺🇸 Axon Enterprise", "FER": "🇺🇸 Ferrovial", "CEG": "🇺🇸 Constellation",
    "ODFL": "🇺🇸 Old Dominion", "ON": "🇺🇸 ON Semi", "EXC": "🇺🇸 Exelon", "BKR": "🇺🇸 Baker Hughes", "TTD": "🇺🇸 Trade Desk",
    # Sonstige Werte
    "ADI": "🇺🇸 Analog Devices", "ANSS": "🇺🇸 Ansys", "CDNS": "🇺🇸 Cadence", "CPRT": "🇺🇸 Copart", "CTAS": "🇺🇸 Cintas", "CSX": "🇺🇸 CSX Corp", "DLTR": "🇺🇸 Dollar Tree", "DXCM": "🇺🇸 DexCom", "FAST": "🇺🇸 Fastenal", "IDXX": "🇺🇸 IDEXX Labs", "KDP": "🇺🇸 Keurig Dr Pepper", "MAR": "🇺🇸 Marriott", "ODFL": "🇺🇸 Old Dominion", "PAYX": "🇺🇸 Paychex", "VRSK": "🇺🇸 Verisk"
    }

# 1. Der Slider in der Sidebar
st.sidebar.header("Filter")
top_n = st.sidebar.slider("Top-Signale anzeigen", min_value=1, max_value=10, value=5)

# 2. Logik zur Aufteilung und Sortierung (nachdem der Scan durchgelaufen ist)
if all_data:
    df = pd.DataFrame(all_data)
    
    col_call, col_put = st.columns(2)
    
    with col_call:
        st.success(f"🔥 Top {top_n} CALL Signale")
        # Filtern nach CALL, Sortieren nach Wahrscheinlichkeit, Begrenzen durch Slider-Wert
        calls = df[df['Typ'] == "CALL 🟢"].sort_values(by="Wahrscheinlichkeit", ascending=False).head(top_n)
        st.table(calls[["Aktie/Name", "Wahrscheinlichkeit", "Kurs", "Ziel %"]])
        
    with col_put:
        st.error(f"📉 Top {top_n} PUT Signale")
        # Filtern nach PUT, Sortieren nach Wahrscheinlichkeit, Begrenzen durch Slider-Wert
        puts = df[df['Typ'] == "PUT 🔴"].sort_values(by="Wahrscheinlichkeit", ascending=False).head(top_n)
        st.table(puts[["Aktie/Name", "Wahrscheinlichkeit", "Kurs", "Ziel %"]])


# --- 4. SCANNER LOGIK MIT WAHRSCHEINLICHKEIT ---
def get_analysis(ticker_dict, timeframe, is_fx=False):
    data_list = []
    for symbol, name in ticker_dict.items():
        try:
            t = yf.Ticker(symbol)
            # Wir benötigen genug Historie für den RSI (mind. 14 Perioden)
            hist = t.history(period="1mo" if "m" in timeframe else "6mo", interval=timeframe)
            if len(hist) < 20: continue
            
            cp = hist['Close'].iloc[-1]
            
            # --- WAHRSCHEINLICHKEITS-SCORE (0-100%) ---
            score = 0
            # 1. Trend (SMA 20) - Gewichtung 40%
            sma = hist['Close'].rolling(20).mean().iloc[-1]
            if cp > sma: score += 40
            
            # 2. Momentum (RSI 14) - Gewichtung 30%
            # RSI zwischen 40 und 60 ist ideal für Trendfortsetzung
            delta = hist['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs)).iloc[-1]
            if 40 < rsi < 70: score += 30
            
            # 3. Volatilitäts-Stabilität - Gewichtung 30%
            # Check, ob der Schlusskurs nah am Tageshoch liegt
            day_range = hist['High'].iloc[-1] - hist['Low'].iloc[-1]
            if day_range > 0 and (cp - hist['Low'].iloc[-1]) / day_range > 0.6:
                score += 30
            
            # Setup-Berechnung
            volatility = hist['High'].rolling(10).std().iloc[-1]
            sl_dist = volatility * 2
            sl = cp - sl_dist
            tp = cp + (sl_dist * 2.5)
            
            risk_unit = abs(cp - sl)
            shares = int(risiko_eur / risk_unit) if risk_unit > 0 else 0
            if is_fx: shares = round(risiko_eur / (risk_unit * 10000), 2)

            data_list.append({
                "Name": name,
                "Kurs": round(cp, 4 if is_fx else 2),
                "Stück/Lots": shares,
                "Wahrscheinlichkeit": f"{score}%",
                "Status": "✅ Bullisch" if score >= 60 else "⚠️ Neutral" if score >= 40 else "❌ Schwach",
                "Ziel %": f"{((tp-cp)/cp)*100:.2f}%",
                "CRV": round((tp-cp)/risk_unit, 2)
            })
        except: continue
    return data_list

# --- 5. ANZEIGE ---
# Forex Sektion
fx_res = get_analysis(forex, intervall, is_fx=True)
if fx_res:
    f = fx_res[0]
    c1, c2, c3 = st.columns(3)
    c1.metric(f"Währung: {f['Name']}", f['Kurs'])
    c2.metric("Wahrscheinlichkeit", f['Wahrscheinlichkeit'])
    c3.write(f"**Empfehlung:** {f['Status']}  \n**Einsatz:** {f['Stück/Lots']} Lots")

st.divider()

# Indizes Sektion
st.subheader("📊 Indizes Wahrscheinlichkeits-Check")
idx_data = get_analysis(indices, intervall)
if idx_data:
    st.dataframe(pd.DataFrame(idx_data), use_container_width=True)

st.divider()

# Aktien Sektion
if st.button("Großen Aktien-Scan starten"):
    stock_data = get_analysis(stocks, intervall)
    if stock_data:
        df = pd.DataFrame(stock_data).sort_values(by="Wahrscheinlichkeit", ascending=False)
        st.dataframe(df, use_container_width=True)

st.caption("Wahrscheinlichkeit basiert auf Trend-Konfluenz (SMA), RSI-Momentum und Candle-Close-Stärke.")
