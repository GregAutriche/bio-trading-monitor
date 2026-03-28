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
    div[data-testid="stDataFrame"] { background-color: #002b55 !important; border-radius: 10px; }
    [data-testid="stMetric"] { background-color: #002b55; border: 1px solid #0074D9; border-radius: 10px; padding: 10px; }
    .stButton>button { background-color: #0074D9; color: white; font-weight: bold; width: 100%; border: none; height: 3em; border-radius: 5px; }
    /* Slider Styling */
    .stSelectSlider { padding-bottom: 2rem; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGIK: ANALYSE-FUNKTION ---
def get_analysis_data(symbol, timeframe="1h"):
    try:
        t = yf.Ticker(symbol)
        hist = t.history(period="60d", interval=timeframe)
        if hist.empty: return None
        return hist
    except: return None

# --- 3. GRAFIK-FUNKTION (DUAL AXIS & VOLUMEN) ---
def plot_advanced_chart(hist, title, current_price):
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, 
                        row_width=[0.2, 0.8], specs=[[{"secondary_y": True}], [{"secondary_y": False}]])
    
    # Candlesticks (Links-Achse)
    fig.add_trace(go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'],
                    low=hist['Low'], close=hist['Close'], name="Kurs"), row=1, col=1, secondary_y=False)
    
    # Abweichung % (Rechts-Achse)
    pct_trace = ((hist['Close'] / current_price) - 1) * 100
    fig.add_trace(go.Scatter(x=hist.index, y=pct_trace, name="Abweichung %", 
                             line=dict(color='#00d4ff', width=1.5)), row=1, col=1, secondary_y=True)
    
    # Volumen (Unten)
    v_colors = ['#00ff00' if r['Open'] < r['Close'] else '#ff4b4b' for _, r in hist.iterrows()]
    fig.add_trace(go.Bar(x=hist.index, y=hist['Volume'], marker_color=v_colors, opacity=0.5, name="Volumen"), row=2, col=1)

    # Achsen-Konfiguration (Kein Minus beim Preis)
    fig.update_yaxes(title_text="Kurs", secondary_y=False, rangemode="nonnegative", row=1, col=1)
    fig.update_yaxes(title_text="Abweichung %", secondary_y=True, showgrid=False, row=1, col=1)
    
    fig.update_layout(height=600, template="plotly_dark", paper_bgcolor="#001f3f", plot_bgcolor="#001f3f", 
                      xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=40,b=0), title=f"Fokus-Analyse: {title}")
    st.plotly_chart(fig, use_container_width=True)

# --- 4. SIDEBAR ---
st.sidebar.header("⚙️ Terminal-Setup")
intervall = st.sidebar.selectbox("Zeitintervall für Charts", ["1h", "1d", "15m", "5m"], index=0)
st.sidebar.divider()
st.sidebar.info("Der Scanner analysiert das Netto-Sentiment (Open Interest) der wichtigsten US-Tech-Werte.")

# --- 5. INDEX-HEATMAP ---
st.subheader("🌍 Markt-Übersicht (Live Indizes)")
idx_map = {"^GDAXI": "DAX", "^IXIC": "NASDAQ", "EURUSD=X": "EUR/USD", "^STOXX50E": "EURO STOXX"}
cols = st.columns(len(idx_map))
for i, (sym, name) in enumerate(idx_map.items()):
    try:
        t = yf.Ticker(sym)
        cp = t.fast_info['last_price']
        chg = ((cp / t.fast_info['previous_close']) - 1) * 100
        bg = "#008000" if chg >= 0 else "#800000"
        cols[i].markdown(f"<div style='background:{bg};padding:10px;border-radius:8px;text-align:center;'><b>{name}</b><br>{chg:.2f}%</div>", unsafe_allow_html=True)
    except: continue

st.divider()

# --- 6. TOP SENTIMENT SCANNER ---
st.subheader("📊 Top 5 Markt-Sentiment Scanner")

if st.button("🚀 Markt nach Netto-Chance scannen"):
    scan_list = {"ADS.DE": "🇩🇪 Adidas", "AIR.DE": "🇩🇪 Airbus", "ALV.DE": "🇩🇪 Allianz", "BAS.DE": "🇩🇪 BASF",
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
    all_stats = []
    
    with st.spinner('Analysiere Options-Volumen...'):
        for sym, name in scan_list.items():
            try:
                t = yf.Ticker(sym)
                if t.options:
                    opt = t.option_chain(t.options[0]) # Nächstes Verfallsdatum
                    c_oi = opt.calls['openInterest'].sum()
                    p_oi = opt.puts['openInterest'].sum()
                    total = c_oi + p_oi
                    
                    if c_oi > p_oi:
                        sentiment, chance, val = "BULLISH", (c_oi / total) * 100, c_oi
                    else:
                        sentiment, chance, val = "BEARISH", (p_oi / total) * 100, p_oi

                    all_stats.append({
                        "Aktie": name, "Symbol": sym, "Chance": chance, 
                        "Sentiment": sentiment, "Volumen (OI)": val
                    })
            except: continue

    if all_stats:
        df = pd.DataFrame(all_stats).sort_values(by='Chance', ascending=False)
        st.session_state['results'] = df # Speichern für den Slider
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### 🟢 Top Bullish (Überwiegend Calls)")
            bulls = df[df['Sentiment'] == "BULLISH"].head(5)
            st.dataframe(bulls[['Aktie', 'Chance', 'Volumen (OI)']].style.format({"Chance": "{:.1f}%", "Volumen (OI)": "{:,.0f}"}), hide_index=True, use_container_width=True)
        with c2:
            st.markdown("#### 🔴 Top Bearish (Überwiegend Puts)")
            bears = df[df['Sentiment'] == "BEARISH"].head(5)
            st.dataframe(bears[['Aktie', 'Chance', 'Volumen (OI)']].style.format({"Chance": "{:.1f}%", "Volumen (OI)": "{:,.0f}"}), hide_index=True, use_container_width=True)

# --- 7. DER DYNAMISCHE GRAFIK-SLIDER ---
if 'results' in st.session_state:
    st.divider()
    st.subheader("🔍 Detail-Fokus: Chart & Volumen")
    
    results = st.session_state['results']
    # Liste für den Slider erstellen (Name + Chance)
    slider_options = [f"{row['Aktie']} ({row['Chance']:.1f}%)" for _, row in results.iterrows()]
    
    # Der Slider zur Auswahl der Aktie
    selected_choice = st.select_slider(
        "Wähle eine Aktie aus dem Scan aus, um die detaillierte Grafik mit Volumen anzuzeigen:",
        options=slider_options
    )
    
    # Symbol aus der Auswahl extrahieren
    sel_name = selected_choice.split(" (")[0]
    sel_row = results[results['Aktie'] == sel_name].iloc[0]
    sel_sym = sel_row['Symbol']
    
    # Chart-Daten laden & anzeigen
    hist_data = get_analysis_data(sel_sym, intervall)
    if hist_data is not None:
        plot_advanced_chart(hist_data, sel_name, hist_data['Close'].iloc[-1])
    else:
        st.error("Fehler beim Laden der Chart-Daten.")

st.markdown("---")
st.caption(f"Terminal Stand: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')} | Modus: Interaktiver Sentiment-Fokus")
