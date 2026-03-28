import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# --- 1. DESIGN & FARBLOGIK (MIDNIGHT BLUE) ---
st.set_page_config(page_title="Trading-Terminal 2026", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #001f3f; color: #ffffff; } 
    div[data-testid="stTable"] { background-color: #002b55 !important; border-radius: 10px; }
    .stTable td, .stTable th { color: #ffffff !important; background-color: #002b55 !important; border-bottom: 1px solid #0074D9 !important; }
    [data-testid="stMetric"] { background-color: #002b55; border: 1px solid #0074D9; border-radius: 10px; }
    [data-testid="stMetricLabel"] { color: #b0c4de !important; font-size: 0.9rem !important; }
    [data-testid="stMetricValue"] { color: #ffffff !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. HEADER: UPDATE & INTERVALL (Ganz oben) ---
last_update = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
col_h1, col_h2 = st.columns([1, 1])
with col_h1:
    st.markdown(f"### 🕒 Letztes Update: <span style='color:#00d4ff;'>{last_update}</span>", unsafe_allow_html=True)
with col_h2:
    st.markdown(f"<h3 style='text-align:right;'>Basis: <span style='color:#00d4ff;'>{intervall}</span></h3>", unsafe_allow_html=True)

# --- 2. ANALYSE-LOGIK ---
def get_analysis(ticker_dict, timeframe, is_fx=False, kontostand=25000, risiko=500):
    data_list = []
    for symbol, name in ticker_dict.items():
        try:
            t = yf.Ticker(symbol)
            hist = t.history(period="60d", interval=timeframe)
            if hist.empty or len(hist) < 20: continue
            
            cp = hist['Close'].iloc[-1]
            prev_close = hist['Close'].iloc[-2]
            chg_pct = ((cp / prev_close) - 1) * 100
            sma20 = hist['Close'].rolling(20).mean().iloc[-1]
            is_bullish = cp > sma20
            
            # Dynamischer SL/TP (Volatilitätsbasiert)
            vol = hist['High'].rolling(14).std().iloc[-1]
            sl_dist = vol * 2 if vol > 0 else cp * 0.005
            
            # 100% Kapital-Sicherung
            min_sl_dist = (risiko * cp) / kontostand
            final_dist = max(sl_dist, min_sl_dist)
            
            sl = cp - final_dist if is_bullish else cp + final_dist
            tp = cp + (final_dist * 2.5) if is_bullish else cp - (final_dist * 2.5)
            
            chance_val = 75 if is_bullish else 45
            risk_unit = abs(cp - sl)
            lots = round(risiko / (risk_unit * 10000), 4) if is_fx else int(risiko / risk_unit)
            kap_pct = ((lots * 100000 * cp if is_fx else lots * cp) / kontostand) * 100

            data_list.append({
                "Name": name, "Symbol": symbol, "Typ": "CALL 🟢" if is_bullish else "PUT 🔴",
                "Chance": f"{chance_val}%", "Chance_Val": chance_val, "Kurs": cp, "Change": chg_pct,
                "Kapitaleinsatz": f"{min(kap_pct, 100.0):.2f}%", "SL": sl, "TP": tp, "Hist": hist
            })
        except: continue
    return data_list

# --- 3. SIDEBAR ---
st.sidebar.header("🛡️ Risikomanagement")
konto = st.sidebar.number_input("Gesamtkapital (EUR)", value=25000)
risiko = st.sidebar.number_input("Risiko pro Trade (EUR)", value=500)
intervall = st.sidebar.selectbox("Intervall", ["1d", "1h", "15m", "5m"], index=0)

# --- 4. INDEX-HEATMAP ---
indices = {"^GDAXI": "DAX", "^IXIC": "NASDAQ", "^STOXX50E": "EURO STOXX", "^NSEI": "NIFTY", "XU100.IS": "BIST 100"}
idx_data = get_analysis(indices, "1d", False, konto, risiko)

if idx_data:
    cols = st.columns(len(idx_data))
    for i, item in enumerate(idx_data):
        bg_color = "#008000" if item['Change'] >= 0 else "#800000"
        with cols[i]:
            st.markdown(f"""<div style="background-color:{bg_color};border:1px solid #0074D9;border-radius:10px;padding:12px;text-align:center;">
                <span style="color:#b0c4de;font-size:0.8rem;display:block;">{item['Name']}</span>
                <span style="color:#ffffff;font-size:1.1rem;font-weight:bold;display:block;">{item['Kurs']:,.0f}</span>
                <span style="color:#ffffff;font-size:0.9rem;">{item['Change']:.2f}%</span></div>""", unsafe_allow_html=True)

st.divider()

# --- 5. GRAFIK-FUNKTION (DUAL AXIS: WERT LINKS, % RECHTS) ---
def plot_trading_chart(item, title):
    # Subplot mit zweiter Y-Achse
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Candlestick auf linker Achse
    fig.add_trace(go.Candlestick(
        x=item['Hist'].index, open=item['Hist']['Open'], high=item['Hist']['High'],
        low=item['Hist']['Low'], close=item['Hist']['Close'], name="Kurs"
    ), secondary_y=False)
    
    # Berechne Prozent-Skala für die rechte Seite (Relativ zum aktuellen Kurs)
    current_price = item['Kurs']
    low_val = item['Hist']['Low'].min() * 0.99
    high_val = item['Hist']['High'].max() * 1.01
    
    # Dummy-Trace für die rechte Achse, um die Prozent-Skala zu erzwingen
    fig.add_trace(go.Scatter(
        x=item['Hist'].index, 
        y=[((y / current_price) - 1) * 100 for y in [low_val, high_val]],
        mode='markers', marker=dict(opacity=0), showlegend=False
    ), secondary_y=True)

    # Trading-Linien (Links fixiert)
    fig.add_hline(y=item['TP'], line_dash="dash", line_color="#00ff00", annotation_text=f"Ziel {item['TP']:.4f}", secondary_y=False)
    fig.add_hline(y=item['SL'], line_dash="dash", line_color="#ff4b4b", annotation_text=f"Stopp {item['SL']:.4f}", secondary_y=False)
    fig.add_hline(y=current_price, line_color="#00d4ff", annotation_text="Entry", secondary_y=False)

    fig.update_yaxes(title_text="<b>Kurs-Wert</b>", secondary_y=False, autorange=True)
    fig.update_yaxes(title_text="<b>Abweichung %</b>", secondary_y=True, showgrid=False)
    fig.update_layout(height=450, template="plotly_dark", paper_bgcolor="#001f3f", plot_bgcolor="#001f3f", margin=dict(l=0,r=0,t=30,b=0), xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

# --- 6. EUR/USD ANALYSE ---
st.subheader("💱 EUR/USD Live-Analyse")
fx_res = get_analysis({"EURUSD=X": "EUR/USD"}, intervall, True, konto, risiko)
if fx_res:
    res = fx_res[0]
    c1, c2, c3 = st.columns(3)
    c1.metric("Kurs", f"{res['Kurs']:.5f}")
    c2.metric("Chance", res['Chance'])
    c3.metric("Kapitaleinsatz", res['Kapitaleinsatz'])
    plot_trading_chart(res, "EUR/USD")

st.divider()

# --- 7. TOP 5 & DETAIL-ANALYSE ---
st.subheader("🔥 Top 5 Aktien-Chancen")
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
stock_results = get_analysis(stocks, intervall, False, konto, risiko)

if stock_results:
    df = pd.DataFrame(stock_results)
    l, r = st.columns(2)
    with l:
        st.success("Top 5 CALL (Long)")
        st.table(df[df['Typ'] == "CALL 🟢"].sort_values("Chance_Val", ascending=False).head(5)[["Name", "Chance", "Kapitaleinsatz", "Kurs"]])
    with r:
        st.error("Top 5 PUT (Short)")
        st.table(df[df['Typ'] == "PUT 🔴"].sort_values("Chance_Val", ascending=False).head(5)[["Name", "Chance", "Kapitaleinsatz", "Kurs"]])

    st.subheader("🔍 Aktien Detail-Ansicht")
    selection = st.selectbox("Aktie wählen:", df['Name'].tolist())
    if selection:
        sel_item = next(x for x in stock_results if x['Name'] == selection)
        plot_trading_chart(sel_item, selection)
