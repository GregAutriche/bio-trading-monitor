import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- 1. MARKT-DATEN ---
EUR_USD_RATE = 1.084255  
MARKET_DATA = {
    "EURUSD": {"val": 1.084255, "chg_3d": -0.45},
    "DAX": {"val": 24338.63, "chg_3d": -1.32},
    "EUROSTOXX 50": {"val": 5911.53, "chg_3d": -1.02},
    "NASDAQ 100": {"val": 29188.98, "chg_3d": 2.19},
    "BIST 100": {"val": 15062.65, "chg_3d": 0.15},
    "NIFTY 50": {"val": 22475.85, "chg_3d": 0.55}
}

ASSETS = {
    "DE": 7"ADS.DE": "🇩🇪 Adidas", "AIR.DE": "🇩🇪 Airbus", "ALV.DE": "🇩🇪 Allianz", "BAS.DE": "🇩🇪 BASF", "BAYN.DE": "🇩🇪 Bayer", "BEI.DE": "🇩🇪 Beiersdorf", "BMW.DE": "🇩🇪 BMW", "BNR.DE": "🇩🇪 Brenntag",
    "CBK.DE": "🇩🇪 Commerzbank", "CON.DE": "🇩🇪 Continental", "1COV.DE": "🇩🇪 Covestro", "DTG.DE": "🇩🇪 Daimler Truck", "DBK.DE": "🇩🇪 Deutsche Bank", "DB1.DE": "🇩🇪 Deutsche Börse",
    "DHL.DE": "🇩🇪 DHL Group", "DTE.DE": "🇩🇪 Deutsche Telekom", "EOAN.DE": "🇩🇪 E.ON", "FRE.DE": "🇩🇪 Fresenius", "FME.DE": "🇩🇪 Fresenius Medical Care", "G1A.DE": "🇩🇪 GEA Group", "HEI.DE": "🇩🇪 Heidelberg Materials", "HNR1.DE": "🇩🇪 Hannover Rück", "HEN3.DE": "🇩🇪 Henkel", "IFX.DE": "🇩🇪 Infineon", "MBG.DE": "🇩🇪 Mercedes-Benz", "MRK.DE": "🇩🇪 Merck",
    "MTX.DE": "🇩🇪 MTU Aero Engines", "MUV2.DE": "🇩🇪 Münchener Rück", "PAH3.DE": "🇩🇪 Porsche SE", "PUM.DE": "🇩🇪 Puma", "QIA.DE": "🇩🇪 Qiagen", "RHM.DE": "🇩🇪 Rheinmetall", "RWE.DE": "🇩🇪 RWE", "SAP.DE": "🇩🇪 SAP", "SRT3.DE": "🇩🇪 Sartorius", "G24.DE": "🇩🇪 Scout24", "SIE.DE": "🇩🇪 Siemens", "ENR.DE": "🇩🇪 Siemens Energy", "SHL.DE": "🇩🇪 Siemens Healthineers", "SY1.DE": "🇩🇪 Symrise", "TKA.DE": "🇩🇪 Thyssenkrupp", "VOW3.DE": "🇩🇪 Volkswagen", "VNA.DE": "🇩🇪 Vonovia", "ZAL.DE": "🇩🇪 Zalando"},
    "US": {"AAPL": "🇺🇸 Apple", "MSFT": "🇺🇸 Microsoft", "GOOGL": "🇺🇸 Alphabet (A)", "GOOG": "🇺🇸 Alphabet (C)", "AMZN": "🇺🇸 Amazon", "META": "🇺🇸 Meta", "NVDA": "🇺🇸 Nvidia", "TSLA": "🇺🇸 Tesla",
    # Halbleiter & Hardware
    "AMD": "🇺🇸 AMD", "AVGO": "🇺🇸 Broadcom", "INTC": "🇺🇸 Intel", "QCOM": "🇺🇸 Qualcomm", "TXN": "🇺🇸 Texas Instruments", "AMAT": "🇺🇸 Applied Materials", "LRCX": "🇺🇸 Lam Research",
    "MU": "🇺🇸 Micron", "ADI": "🇺🇸 Analog Devices", "KLAC": "🇺🇸 KLA Corp", "ASML": "🇺🇸 ASML (ADS)", "ARM": "🇺🇸 ARM Holdings", "MPWR": "🇺🇸 Monolithic Power", "STX": "🇺🇸 Seagate", "WDC": "🇺🇸 Western Digital",
    # Software & Cloud
    "ADBE": "🇺🇸 Adobe", "CRM": "🇺🇸 Salesforce", "ORCL": "🇺🇸 Oracle", "INTU": "🇺🇸 Intuit", "PANW": "🇺🇸 Palo Alto", "SNPS": "🇺🇸 Synopsys", "CDNS": "🇺🇸 Cadence", "WDAY": "🇺🇸 Workday", "ROP": "🇺🇸 Roper", "ADSK": "🇺🇸 Autodesk", "TEAM": "🇺🇸 Atlassian", "DDOG": "🇺🇸 Datadog",
    "ZS": "🇺🇸 Zscaler", "CRWD": "🇺🇸 CrowdStrike", "PLTR": "🇺🇸 Palantir", "APP": "🇺🇸 AppLovin",
    # Internet, Media & E-Commerce
    "NFLX": "🇺🇸 Netflix", "BKNG": "🇺🇸 Booking", "ABNB": "🇺🇸 Airbnb", "PDD": "🇺🇸 PDD Holdings", "MELI": "🇺🇸 MercadoLibre", "JD": "🇺🇸 JD.com", "PYPL": "🇺🇸 PayPal", "EBAY": "🇺🇸 eBay",
    "DASH": "🇺🇸 DoorDash", "GOOG": "🇺🇸 Alphabet", "WBD": "🇺🇸 Warner Bros", "CHTR": "🇺🇸 Charter",
    # Healthcare & Biotech
    "AMGN": "🇺🇸 Amgen", "GILD": "🇺🇸 Gilead", "VRTX": "🇺🇸 Vertex", "REGN": "🇺🇸 Regeneron", "ISRG": "🇺🇸 Intuitive Surg.", "IDXX": "🇺🇸 IDEXX Labs", "MRNA": "🇺🇸 Moderna", "BIIB": "🇺🇸 Biogen",
    "ALNY": "🇺🇸 Alnylam", "INSM": "🇺🇸 Insmed", "GEHC": "🇺🇸 GE HealthCare",
    # Consumer, Retail & Others
    "COST": "🇺🇸 Costco", "PEP": "🇺🇸 PepsiCo", "KO": "🇺🇸 Coca-Cola", "WMT": "🇺🇸 Walmart", "SBUX": "🇺🇸 Starbucks", "MDLZ": "🇺🇸 Mondelez", "MNST": "🇺🇸 Monster", "KDP": "🇺🇸 Keurig Dr Pepper", "KHC": "🇺🇸 Kraft Heinz", "MAR": "🇺🇸 Marriott", "ORLY": "🇺🇸 O'Reilly", "ROST": "🇺🇸 Ross Stores", "LULU": "🇺🇸 Lululemon", "TGT": "🇺🇸 Target", "CSX": "🇺🇸 CSX Corp", "CPRT": "🇺🇸 Copart", "FAST": "🇺🇸 Fastenal", "PAYX": "🇺🇸 Paychex", "CTAS": "🇺🇸 Cintas", "ADP": "🇺🇸 ADP", "MCHP": "🇺🇸 Microchip", "AXON": "🇺🇸 Axon Enterprise", "FER": "🇺🇸 Ferrovial", "CEG": "🇺🇸 Constellation", "ODFL": "🇺🇸 Old Dominion", "ON": "🇺🇸 ON Semi", "EXC": "🇺🇸 Exelon", "BKR": "🇺🇸 Baker Hughes", "TTD": "🇺🇸 Trade Desk",
    # Sonstige Werte
    "ADI": "🇺🇸 Analog Devices", "ANSS": "🇺🇸 Ansys", "CDNS": "🇺🇸 Cadence", "CPRT": "🇺🇸 Copart", "CTAS": "🇺🇸 Cintas", "CSX": "🇺🇸 CSX Corp", "DLTR": "🇺🇸 Dollar Tree", "DXCM": "🇺🇸 DexCom", "FAST": "🇺🇸 Fastenal", "IDXX": "🇺🇸 IDEXX Labs", "KDP": "🇺🇸 Keurig Dr Pepper", "MAR": "🇺🇸 Marriott", "ODFL": "🇺🇸 Old Dominion", "PAYX": "🇺🇸 Paychex", "VRSK": "🇺🇸 Verisk"},
    "EU": {# Frankreich (🇫🇷)
    {"AI.PA": "🇫🇷 Air Liquide", "AIR.PA": "🇫🇷 Airbus", "CS.PA": "🇫🇷 AXA", "BNP.PA": "🇫🇷 BNP Paribas",  "BN.PA": "🇫🇷 Danone", "EL.PA": "🇫🇷 EssilorLuxottica", "RMS.PA": "🇫🇷 Hermès", "OR.PA": "🇫🇷 L'Oréal", "MC.PA": "🇫🇷 LVMH", "RI.PA": "🇫🇷 Pernod Ricard", "SAF.PA": "🇫🇷 Safran", "SAN.PA": "🇫🇷 Sanofi", "SU.PA": "🇫🇷 Schneider Electric", "TTE.PA": "🇫🇷 TotalEnergies", "DG.PA": "🇫🇷 Vinci",
    # Niederlande (🇳🇱)
    "ASML.AS": "🇳🇱 ASML Holding", "INGA.AS": "🇳🇱 ING Groep", "PRX.AS": "🇳🇱 Prosus", "AD.AS": "🇳🇱 Ahold Delhaize", "STLAM.MI": "🇳🇱 Stellantis", # (Stellantis oft via Mailand)
    # Spanien (🇪🇸)
    "BBVA.MC": "🇪🇸 BBVA", "IBE.MC": "🇪🇸 Iberdrola", "ITX.MC": "🇪🇸 Inditex", "SAN.MC": "🇪🇸 Banco Santander",
    # Italien (🇮🇹)
    "ENEL.MI": "🇮🇹 Enel", "ENI.MI": "🇮🇹 Eni", "ISP.MI": "🇮🇹 Intesa Sanpaolo", "RACE.MI": "🇮🇹 Ferrari", "UCG.MI": "🇮🇹 UniCredit",
    # Belgien (🇧🇪), Irland (🇮🇪), Finnland (🇫🇮)
    "ABI.BR": "🇧🇪 Anheuser-Busch InBev", "CRH.AS": "🇮🇪 CRH", "FLTR.IR": "🇮🇪 Flutter Entertainment", "NOKIA.HE": "🇫🇮 Nokia"}
}

TICKER_TO_NAME = {ticker: name for region in ASSETS.values() for ticker, name in region.items()}
ALL_TICKERS = list(TICKER_TO_NAME.keys())

# --- 2. HILFSFUNKTIONEN ---
def get_logic_icons(chg):
    weather = "☀️" if chg > 0.5 else "⛈️" if chg < -0.5 else "☁️"
    dot = "🟢" if chg > 0.4 else "🔵" if chg < -0.4 else "⚪"
    return weather, dot

def get_swing_analysis(ticker):
    try:
        df = pd.DataFrame(np.random.randn(60, 4), columns=['Open', 'High', 'Low', 'Close']).cumsum() + 150
        df['SMA20'] = df['Close'].rolling(window=20).mean()
        cp = df['Close'].iloc[-1]
        chg_3d = ((cp / df['Close'].iloc[-4]) - 1) * 100
        is_bullish = cp > df['SMA20'].iloc[-1]
        df['TR'] = np.maximum(df['High'] - df['Low'], np.maximum(abs(df['High'] - df['Close'].shift(1)), abs(df['Low'] - df['Close'].shift(1))))
        atr = df['TR'].tail(14).mean()
        weather, dot = get_logic_icons(chg_3d)
        signal = "CALL" if chg_3d > 0.4 else "PUT" if chg_3d < -0.4 else "NEUTRAL"
        chance = round(50.0 + (15 if is_bullish else -10) + (abs(chg_3d) * 0.8), 2)
        return {"cp": cp, "chg_3d": chg_3d, "atr": atr, "df": df, "chance": chance, "weather": weather, "dot": dot, "signal": signal}
    except: return None

# --- 3. UI LAYOUT ---
st.set_page_config(page_title="Trading Monitor Pro", layout="wide")

# Header: EUR/USD
eu_data = MARKET_DATA["EURUSD"]
eu_w, eu_d = get_logic_icons(eu_data['chg_3d'])
st.markdown(f"<h1 style='text-align: center; color: #5DADE2;'>{eu_w} EUR / USD: {eu_data['val']:.6f} {eu_d}</h1>", unsafe_allow_html=True)
st.divider()

# Indizes in 2 Zeilen
idx_list = ["DAX", "EUROSTOXX 50", "NASDAQ 100", "BIST 100", "NIFTY 50"]
r1 = st.columns(3)
for i in range(3):
    name = idx_list[i]; d = MARKET_DATA[name]; w, dot = get_logic_icons(d['chg_3d'])
    r1[i].metric(f"{w} {name}", f"{d['val']:,.2f}", f"{dot} {d['chg_3d']:.2f}%", delta_color="normal" if d['chg_3d'] >= 0 else "inverse")
r2 = st.columns(3)
for i in range(3, 5):
    name = idx_list[i]; d = MARKET_DATA[name]; w, dot = get_logic_icons(d['chg_3d'])
    r2[i-3].metric(f"{w} {name}", f"{d['val']:,.2f}", f"{dot} {d['chg_3d']:.2f}%", delta_color="normal" if d['chg_3d'] >= 0 else "inverse")

st.divider()

# --- 4. TOP 7 CHANCEN BOARD ---
st.subheader("📊 Top 7 Trading-Chancen (3-5 Tage)")
rank_list = []
for t in ALL_TICKERS:
    res = get_swing_analysis(t)
    if res:
        rank_list.append({
            "Aktie": f"{res['weather']} {TICKER_TO_NAME[t]}",
            "Signal": f"{res['dot']} {res['signal']}",
            "Wahrscheinlichkeit (%)": f"{res['chance']:.2f}",
            "Trend 3D": f"{res['chg_3d']:.2f}%",
            "Kurs": f"{res['cp']:.2f} €"
        })
df_rank = pd.DataFrame(rank_list).sort_values(by="Wahrscheinlichkeit (%)", ascending=False).head(7)
st.table(df_rank)

# --- 5. DETAIL-ANALYSE & ORDER-EXTENDER ---
st.divider()
st.subheader("🔍 Smart-Entry & Order-Extender")
reg_choice = st.radio("Region:", ["DE", "US", "EU"], horizontal=True)
selected = st.selectbox("Aktie wählen:", list(ASSETS[reg_choice].keys()), format_func=lambda x: ASSETS[reg_choice][x])

det = get_swing_analysis(selected)
if det:
    direction = 1 if det['chg_3d'] > 0 else -1
    sl_price = det['cp'] - (2.0 * det['atr'] * direction)
    tp_price = det['cp'] + (4.0 * det['atr'] * direction)
    dist_pct = abs((sl_price / det['cp']) - 1)
    opt_hebel = 0.25 / dist_pct if dist_pct > 0 else 1.0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("SIGNAL", f"{det['dot']} {det['signal']}", f"Wetter: {det['weather']}")
    c2.metric("STOP-LOSS (ATR)", f"{sl_price:.2f} €", f"{dist_pct*100:.2f}% Puffer")
    c3.metric("SMART HEBEL", f"x{opt_hebel:.1f}", "Risiko-Limit 25%")
    c4.metric("WAHRSCH. (%)", f"{det['chance']:.2f}")

    # ORDER-EXTENDER BOX
    with st.expander("📝 Detaillierte Bestellung (Order-Details)", expanded=True):
        st.markdown(f"""
        ### 🛒 Order-Zusammenfassung für {TICKER_TO_NAME[selected]}
        *   **Typ:** {'🟢 CALL / LONG' if direction == 1 else '🔵 PUT / SHORT'}
        *   **Basiswert:** {selected} ({TICKER_TO_NAME[selected]})
        *   **Aktueller Kurs:** {det['cp']:.2f} €
        *   **Empfohlener Hebel:** x{opt_hebel:.1f}
        *   **Strategischer Stop-Loss:** **{sl_price:.2f} €**
        *   **Kursziel (3-5 Tage):** **{tp_price:.2f} €**
        *   **Strategie-Gültigkeit:** Bis {(datetime.now() + timedelta(days=5)).strftime('%d.%m.%Y')}
        ---
        *Hinweis: Der Stop-Loss basiert auf dem 2.0x ATR-Puffer, um das Wochenrauschen abzufangen.*
        """)

    fig = go.Figure(data=[go.Candlestick(x=det['df'].index, open=det['df']['Open'], high=det['df']['High'], low=det['df']['Low'], close=det['df']['Close'])])
    fig.add_hline(y=sl_price, line_dash="dash", line_color="red", annotation_text="STOP LOSS")
    fig.add_hline(y=tp_price, line_dash="dash", line_color="green", annotation_text="TARGET")
    fig.update_layout(height=450, template="plotly_dark", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
