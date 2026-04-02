import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

# --- 1. KONFIGURATION & REFRESH (5 MINUTEN) ---
st.set_page_config(page_title="Trading Monitor", layout="wide")
st_autorefresh(interval=5 * 60 * 1000, key="fscounter")

# --- 2. TICKER-MAPPING ---
INDEX_MAPPING = {
    "^GDAXI": "DAX 40", "^NDX": "NASDAQ 100", "EURUSD=X": "EUR/USD",
    "^STOXX50E": "EuroStoxx 50", "XU100.IS": "BIST 100", "^NSEI": "Nifty 50"
}
TICKER_NAMES = {
    "ADS.DE": "🇩🇪 Adidas", "AIR.DE": "🇩🇪 Airbus", "ALV.DE": "🇩🇪 Allianz", "BAS.DE": "🇩🇪 BASF",
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
STOCKS_ONLY = list(TICKER_NAMES.keys())

# --- 3. DESIGN (DUNKELBLAUER KONTRAST & SCHRIFTGRÖSSE) ---
st.markdown("""
    <style>
    .stApp { background-color: #0B0E14; color: #FFFFFF; }
    
    /* Metrik-Werte (Zahlen) - Optimiert gegen Abschneiden */
    [data-testid="stMetricValue"] { 
        font-size: 1.5rem !important; 
        font-weight: 800 !important; 
        color: #FFFFFF !important; 
    }
    
    /* Metrik-Labels (Überschriften) - Hellweiß */
    [data-testid="stMetricLabel"] { 
        font-size: 0.95rem !important; 
        color: #F8FAFC !important; 
        font-weight: 700 !important;
        text-transform: uppercase;
    }
    
    /* Kachel-Design */
    div[data-testid="stMetric"] { 
        background: #161B22; 
        border: 1px solid #1F2937; 
        padding: 18px !important; 
        border-radius: 12px; 
    }

    /* Tabellen-Optik */
    .stTable td { color: #FFFFFF !important; background-color: #0B0E14 !important; border: 1px solid #1F2937 !important; font-size: 1.1rem !important; }
    .stTable th { background-color: #1E90FF !important; color: #FFFFFF !important; font-weight: 900 !important; }
    .update-info { font-size: 1rem; color: #38BDF8; font-weight: bold; margin-bottom: 25px; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. ANALYSE-FUNKTIONEN ---
def get_status_info(chg):
    if chg > 0.4: return "☀️ 🟢"
    if chg < -0.4: return "⛈️ 🔵"
    return "☁️ ⚪"

@st.cache_data(ttl=290)
def get_live_index_data(symbol):
    try:
        tk = yf.Ticker(symbol)
        df = tk.history(period="2d")
        cp = df["Close"].iloc[-1]
        chg = ((cp / df["Close"].iloc[-2]) - 1) * 100
        return cp, chg
    except: return 0, 0

@st.cache_data(ttl=290)
def get_extended_stock_analysis(symbol):
    try:
        tk = yf.Ticker(symbol)
        df = tk.history(period="1y") 
        if df.empty: return None
        
        cp = df["Close"].iloc[-1]
        prev_cp = df["Close"].iloc[-2]
        chg = ((cp / prev_cp) - 1) * 100
        
        # 250 Tage Hoch / Tief
        h250 = df["High"].max()
        l250 = df["Low"].min()
        
        # ATR für SL/TP Berechnung
        df['TR'] = np.maximum(df['High'] - df['Low'], np.maximum(abs(df['High'] - df['Close'].shift(1)), abs(df['Low'] - df['Close'].shift(1))))
        atr = df['TR'].tail(14).mean()
        
        # Volumen-Kennzahlen
        curr_vol = df["Volume"].iloc[-1]
        prev_vol = df["Volume"].iloc[-2]
        avg_vol = df["Volume"].tail(20).mean()
        vol_rel = curr_vol / avg_vol
        vol_chg = ((curr_vol / prev_vol) - 1) * 100 if prev_vol > 0 else 0
        
        return {
            "cp": cp, "chg": chg, "h250": h250, "l250": l250, "atr": atr,
            "vol": curr_vol, "vol_rel": vol_rel, "vol_chg": vol_chg,
            "df": df, "chance": round(52.0000 + (vol_rel * 1.5) + (abs(chg) * 0.4), 4)
        }
    except: return None

# --- 5. DASHBOARD LAYOUT ---
st.title("🚀 Trading Monitor 🚀")

# 5.1 HEADER INFO
now = datetime.now().strftime('%H:%M:%S')
st.markdown(f'<div class="update-info">🕒 Letztes Update: {now} | Intervall: 5 Min. | Status: 🟢 Synchronisiert</div>', unsafe_allow_html=True)

# 5.2 INDICES IN 2 ZEILEN
idx_keys = list(INDEX_MAPPING.keys())
for i in range(0, 6, 3):
    cols = st.columns(3)
    for j in range(3):
        sym = idx_keys[i+j]
        val, chg = get_live_index_data(sym)
        status = get_status_info(chg)
        fmt = "{:.5f}" if "EURUSD" in sym else "{:,.0f}"
        cols[j].metric(f"{status} {INDEX_MAPPING[sym]}", fmt.format(val), f"{chg:.2f}%")
st.divider()

# 5.3 TOP MARKT-CHANCEN TABELLE
st.subheader("📊 Top 7 Markt-Chancen (Vola-Analyse)")
top_list = []
for t in STOCKS_ONLY:
    d = get_extended_stock_analysis(t)  # Nutzt deine bestehende Analyse-Funktion
    if d:
        # Wetter & Action-Icon Logik für die Aktie
        weather = "☀️" if d['chg'] > 0.5 else "⛈️" if d['chg'] < -0.5 else "☁️"
        dot = "🟢" if d['chg'] > 0.4 else "🔵" if d['chg'] < -0.4 else "⚪"
        
        # Signal Text (Call / Put / Neutral)
        signal_text = "CALL" if d['chg'] > 0.4 else "PUT" if d['chg'] < -0.4 else "NEUTRAL"
        
        top_list.append({
            "Aktie": f"{weather} {TICKER_NAMES[t]}",
            "Signal (C/P)": f"{dot} {signal_text}",
            "Chance (%)": d['chance'],
            "Kurs (€)": f"{d['cp']:.2f}",
            "Vol-Rel": f"{d['vol_rel']:.2f}x"
        })

# DataFrame erstellen
df_top = pd.DataFrame(top_list)
df_top = df_top.sort_values(by="Chance (%)", ascending=False).head(7)
# Formatierung der Chance auf 2 Nachkommastellen (wie besprochen)
df_top["Chance (%)"] = df_top["Chance (%)"].map("{:.2f}".format)

# Anzeige der Tabelle mit dem blauen Header (Design aus CSS-Teil)
st.table(df_top)

# 5.4 DETAIL-ANALYSE MIT 3 METRIK-ZEILEN
st.divider()
st.subheader("🔍 Smart-Entry: Detail-Analyse & Trading-Setup")
selected = st.selectbox("Aktie wählen:", STOCKS_ONLY, format_func=lambda x: TICKER_NAMES[x])
det = get_extended_stock_analysis(selected)

# --- SMART-ENTRY: DETAIL-ANALYSE & TRADING-SETUP (OPTIMIERT) ---
if det:
    # 1. BASIS-LOGIK FÜR SIGNALE
    weather = "☀️" if det['chg'] > 0.5 else "⛈️" if det['chg'] < -0.5 else "☁️"
    dot = "🟢" if det['chg'] > 0.4 else "🔵" if det['chg'] < -0.4 else "⚪"
    signal_text = "CALL" if det['chg'] > 0.4 else "PUT" if det['chg'] < -0.4 else "NEUTRAL"
    
    # BERECHNUNG SL / TP (ATR-BASIS)
    direction = 1 if det['chg'] >= 0 else -1
    sl_price = det['cp'] - (1.5 * det['atr'] * direction)
    tp_price = det['cp'] + (3.0 * det['atr'] * direction)
    crv = abs(tp_price - det['cp']) / abs(det['cp'] - sl_price) if abs(det['cp'] - sl_price) > 0 else 0

    # REIHE 1: HAUPT-SIGNALE (CALL/PUT, WETTER, ACTION, CHANCE)
    s1, s2, s3, s4 = st.columns(4)
    with s1: st.metric("TRADING SIGNAL", f"{dot} {signal_text}")
    with s2: st.metric("MARKT-WETTER", f"{weather}", "Langfristig")
    with s3: st.metric("ACTION STATUS", "AKTIV" if abs(det['chg']) > 0.4 else "WAIT")
    with s4: st.metric("CHANCE (%)", f"{det['chance']:.4f}", "Vola-Score")

    # REIHE 2: TRADING MARKEN (STOP-LOSS & TAKE-PROFIT)
    t1, t2, t3, t4 = st.columns(4)
    with t1: st.metric("STOP-LOSS (SL)", f"{sl_price:.2f} €", f"{((sl_price/det['cp'])-1)*100:.2f}%", delta_color="inverse")
    with t2: st.metric("TAKE-PROFIT (TP)", f"{tp_price:.2f} €", f"{((tp_price/det['cp'])-1)*100:.2f}%")
    with t3: st.metric("RISIKO PRO AKTIE", f"{abs(det['cp'] - sl_price):.2f} €", "ATR-Basis")
    with t4: st.metric("CRV (ZIEL)", f"{crv:.2f}", "Chance/Risiko")

    st.markdown("---") # Optische Trennung zu den Volumen/Jahres-Daten

    # REIHE 3: VOLUMEN-KENNZAHLEN
    v1, v2, v3, v4 = st.columns(4)
    with v1: st.metric("VOLUMEN AKTUELL", f"{det['vol']:,.0f}")
    with v2: st.metric("VOL-TREND (REL)", f"{det['vol_rel']:.2f}x", "vs. 20D Ø")
    with v3: st.metric("VOL-VERÄNDERUNG", f"{det['vol_chg']:.1f}%", "vs. Gestern")
    with v4: 
        pos_in_range = (det['cp'] - det['l250']) / (det['h250'] - det['l250']) * 100
        st.metric("LAGE IM JAHRESBAND", f"{pos_in_range:.1f}%", "0=Tief / 100=Hoch")

    # REIHE 4: 250-TAGE HOCH / TIEF & KURS
    r1, r2, r3, r4 = st.columns(4)
    with r1: st.metric("250T HOCH", f"{det['h250']:.2f} €", f"{((det['cp']/det['h250'])-1)*100:.1f}% Abstand")
    with r2: st.metric("KURS AKTUELL", f"{det['cp']:.2f} €", f"{det['chg']:.2f}%")
    with r3: st.metric("250T TIEF", f"{det['l250']:.2f} €", f"+{((det['cp']/det['l250'])-1)*100:.1f}% Abstand")
    with r4: st.metric("JAHRES-SPANNE", f"{det['h250'] - det['l250']:.2f} €", "H vs L")

    # CHART MIT HANDELSLINIEN
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.7, 0.3])
    fig.add_trace(go.Candlestick(x=det['df'].index, open=det['df']['Open'], high=det['df']['High'], low=det['df']['Low'], close=det['df']['Close'], name="Kurs"), row=1, col=1)
    
    # SL/TP Linien einzeichnen
    fig.add_hline(y=sl_price, line_dash="dash", line_color="#FF4B4B", annotation_text="SL", row=1, col=1)
    fig.add_hline(y=tp_price, line_dash="dash", line_color="#00FFA3", annotation_text="TP", row=1, col=1)
    fig.add_hline(y=det['cp'], line_dash="dot", line_color="#FFFFFF", annotation_text="ENTRY", row=1, col=1)

    v_colors = ['#00FFA3' if c >= o else '#FF4B4B' for o, c in zip(det['df']['Open'], det['df']['Close'])]
    fig.add_trace(go.Bar(x=det['df'].index, y=det['df']['Volume'], marker_color=v_colors, name="Volumen"), row=2, col=1)
    
    fig.update_layout(height=650, template="plotly_dark", xaxis_rangeslider_visible=False, paper_bgcolor='#0B0E14', plot_bgcolor='#0B0E14', showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# 5.5 AUSKLAPPBARE HILFE
with st.expander("ℹ️ Erläuterung der Analyse-Werte (Trading-Guide)"):
    st.markdown("""
    ### 📊 Volumen-Kennzahlen
    *   **VOLUMEN AKTUELL:** Anzahl der heute gehandelten Aktien. Hohes Volumen bestätigt die Stärke eines Trends.
    *   **VOL-TREND (REL):** Das aktuelle Volumen im Vergleich zum 20-Tage-Durchschnitt. Werte **> 1.0x** zeigen erhöhtes institutionelles Interesse.
    *   **VOL-VERÄNDERUNG:** Prozentualer Zuwachs des Volumens im Vergleich zum gestrigen Handelstag. Ein Sprung (> 50%) deutet oft auf News hin.
    
    ### 📈 Trend- & Kurs-Analyse
    *   **LAGE IM JAHRESBAND:** Zeigt, wo der Kurs zwischen dem 250T Tief (0%) und dem 250T Hoch (100%) steht. Werte um 50% gelten als neutraler Bereich.
    *   **250T HOCH / TIEF:** Die Extrempunkte der letzten 250 Handelstage (~1 Jahr). Der **Abstand** zeigt, wie viel "Luft" nach oben oder wie viel Puffer nach unten besteht.
    *   **JAHRES-SPANNE:** Die gesamte Handelsbreite des letzten Jahres in Euro. Hilft bei der Einschätzung der langfristigen Volatilität.
    
    ### 🛡️ Signale & Chance
    *   **SIGNAL (C/P):** Basierend auf kurzfristigen Trend-Indikatoren. **🟢 CALL** bei Aufwärtsmomentum, **🔵 PUT** bei Abwärtsdruck.
    *   **CHANCE (%):** Ein gewichteter Score aus Volumen-Power und Trend-Stärke. Werte über **55%** gelten als statistisch signifikante Trading-Gelegenheit.
    """)

