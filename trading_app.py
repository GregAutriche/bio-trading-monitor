import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

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

# Filter für Detail-Analyse (Keine Währungen/Indizes)
STOCKS_ONLY = [k for k in TICKER_NAMES.keys() if not k.startswith("^") and not "=X" in k and k != "XU100.IS"]

# --- 3. DESIGN (DARK MODE & KONTRAST) ---
st.markdown("""
    <style>
        /* Metriken schärfer und kleiner machen */
    [data-testid="stMetricValue"] {
        font-size: 1.6rem !important; /* Etwas kleiner */
        font-weight: 800 !important;   /* Extra fett */
        color: #FFFFFF !important;    /* Reinweiß */
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.8rem !important;  /* Kleinere Labels */
        color: #8892b0 !important;    /* Dezentes Grau */
        text-transform: uppercase;
    }
    /* Kompakterer Abstand */
    div[data-testid="stMetric"] {
        padding: 5px 10px;
        background: rgba(255,255,255,0.02);
        border-radius: 8px;
    }
    """, unsafe_allow_html=True)
    .stApp { background-color: #0E1117 !important; color: #FFFFFF !important; }
    .weather-card { text-align:center; border-radius:12px; background:rgba(255,255,255,0.03); border: 2px solid #333; padding: 15px; margin-bottom: 10px; }
    .update-info { color: #8892b0; font-size: 0.85rem; margin-bottom: 20px; text-align: center; border: 1px solid #1E90FF; padding: 5px; border-radius: 5px; }
    thead tr th { background-color: #2D3748 !important; color: #FFFFFF !important; font-weight: 900 !important; border-bottom: 3px solid #1E90FF !important; }
    tbody tr td { color: #FFFFFF !important; background-color: #161B22 !important; border-bottom: 1px solid #30363D !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. ZENTRALE FUNKTION ---
@st.cache_data(ttl=60)
def get_analysis(ticker):
    try:
        df = yf.download(ticker, period="30d", interval="1h", progress=False)
        if df.empty or len(df) < 15: 
            return {"cp": 0.0, "chg": 0.0, "chance": 50, "atr": 0.0, "vol": 0, "df": df}
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        cp = float(df['Close'].iloc[-1])
        prev = float(df['Close'].iloc[-2])
        chg = ((cp / prev) - 1) * 100
        atr = (df['High'] - df['Low']).rolling(14).mean().iloc[-1]
        
        # Chance Simulation (Synchronisiert)
        returns = np.log(df['Close'] / df['Close'].shift(1)).dropna()
        np.random.seed(42)
        sim = np.random.normal(returns.mean(), returns.std(), 1000)
        chance = int((sim > 0).sum() / 10)
        
        return {"cp": cp, "chg": chg, "chance": chance, "atr": atr, "vol": int(df['Volume'].iloc[-1]), "df": df}
    except:
        return {"cp": 0.0, "chg": 0.0, "chance": 50, "atr": 0.0, "vol": 0, "df": pd.DataFrame()}

def get_style(chg):
    if chg > 0.15: return "☀️", "#00FFA3", "🟢"
    if chg < -0.15: return "⛈️", "#1E90FF", "🔵"
    return "☁️", "#8892b0", "⚪"

# --- 5. DASHBOARD AUFBAU ---
st.title("🚀 Bio-Trading Monitor Live PRO")
# Zeit-Korrektur: Aktuelle Zeit + 1 Stunde (für MEZ/Winterzeit)
from datetime import timedelta
now_fixed = (datetime.now() + timedelta(hours=1)).strftime('%H:%M:%S')

st.markdown(f"""
    <div class="update-info">
        🕒 Letztes Update: <b>{now_fixed}</b> | 
        Intervall: <b>60s</b> | 
        Status: <b>Synchronisiert</b>
    </div>
""", unsafe_allow_html=True)

# --- 5.1 INFO-EXPANDER (DOKUMENTATION) ---
with st.expander("ℹ️ Hilfe & Dokumentation: Wie werden die Werte berechnet?"):
    st.markdown("""
    ### 📊 Top 5 Aktien-Chancen
    Die Top-Listen werden bei jedem Refresh (60s) neu generiert. 
    - **Scan:** Es werden alle hinterlegten DAX 40 und NASDAQ 100 Werte (ca. 130+ Aktien) analysiert.
    - **Filter:** Die linke Tabelle zeigt nur Werte mit positivem Trend, die rechte nur mit negativem Trend.
    - **Sortierung:** Innerhalb dieser Gruppen wird nach der **statistischen Chance** (Monte-Carlo-Simulation) sortiert, nicht nach der reinen Kursänderung.
    
    ---
    
    ### 🔍 Detail-Info & Metriken
    - **KURS:** Aktueller Preis mit der prozentualen Änderung zum Vorstunden-Schlusskurs.
    - **CHANCE:** Ergebnis einer Simulation von 1.000 Pfaden basierend auf der Volatilität der letzten 30 Tage. Ein Wert über 50% signalisiert eine statistische Aufwärts-Wahrscheinlichkeit.
    - **ATR (14h):** Die *Average True Range* zeigt die durchschnittliche Schwankungsbreite der letzten 14 Stunden. Sie dient zur Bestimmung der Volatilität und zur Setzung von Stop-Loss-Marken.
    - **VOLUMEN-TREND:** Das aktuelle Volumen im Vergleich zum 20-Tage-Schnitt (120 Handelsstunden). Ein positiver Wert zeigt erhöhtes Interesse.
    ---
    ### 📈 Grafik-Beschreibung
    Das Chart kombiniert zwei wichtige Informationsebenen:
    1. **Candlesticks (Kerzen):** Zeigen Eröffnung, Schluss, Hoch und Tief pro Stunde. 
       - <span style='color:#00FFA3;'>Grün</span> = Kurs gestiegen.
       - <span style='color:#FF4B4B;'>Rot</span> = Kurs gefallen.
    2. **Volumen-Profil (Blau):** Die blauen Balken im Hintergrund nutzen die **linke Y-Achse**. Sie zeigen die Handelsaktivität.
    3. **Lückenlos-Achse:** Wochenenden und Nachtstunden werden ausgeblendet, um eine unterbrechungsfreie technische Analyse zu ermöglichen.
    """, unsafe_allow_html=True)


# 5a. MARKT-WETTER (3 ZEILEN)
WEATHER_ROWS = [
    ["EURUSD=X", "EURRUB=X"],                   # 1. Währungen
    ["^GDAXI", "^NDX"],                         # 2. Leit-Indizes
    ["^STOXX50E", "^NSEI", "XU100.IS"]          # 3. Weitere Indizes
]

for row in WEATHER_ROWS:
    cols = st.columns(len(row))
    for i, t in enumerate(row):
        res = get_analysis(t)
        icon, color, dot = get_style(res["chg"])
        prec = ".4f" if "=X" in t else ".2f"
        price_str = f"{res['cp']: ,{prec}}"
        with cols[i]:
            st.markdown(f"""
                <div class="weather-card" style="border-color:{color};">
                    <div style="display: flex; justify-content: space-between;"><small>{TICKER_NAMES.get(t,t)}</small><span>{icon}</span></div>
                    <b style="font-size:1.5rem;">{price_str}</b><br>
                    <div style="display: flex; justify-content: space-between; margin-top: 5px;">
                        <span style="color:{color};">{res['chg']:+.2f}%</span><span>{dot}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

st.divider()

# --- 5b. TOP 5 AKTIEN MIT FEHLER-ANZEIGE ---
st.subheader("📊 Top 5 Aktien-Chancen")

# 1. SCAN-VORGANG & FEHLER-TRACKING
signals = []
failed_scans = [] # Liste für nicht erreichbare Werte

with st.spinner("Analysiere Markt-Daten..."):
    for s in STOCKS_ONLY:
        r = get_analysis(s)
        if r["cp"] > 0:
            _, _, dot = get_style(r["chg"])
            signals.append({
                'Status': dot, 
                'Aktie': TICKER_NAMES.get(s,s), 
                'Trend_Val': r["chg"], 
                'Trend': f"{r['chg']:+.2f}%", 
                'Chance': r["chance"]
            })
        else:
            # Falls Kurs 0 ist, ab in die Fehlerliste (mit Klartext-Namen)
            failed_scans.append(TICKER_NAMES.get(s, s))

# 2. SCAN-STATISTIK ANZEIGEN
count_de = len([k for k in STOCKS_ONLY if k.endswith(".DE")])
count_us = len([k for k in STOCKS_ONLY if not k.endswith(".DE")])

st.markdown(f"""
    <div style="color: #8892b0; font-size: 0.9rem; margin-bottom: 5px;">
        ℹ️ Info: <b>{count_de}</b> Aktien aus DE / <b>{count_us}</b> Aktien aus US gescannt (Gesamt: {len(STOCKS_ONLY)})
    </div>
""", unsafe_allow_html=True)

# 3. NEU: ANZEIGE DER NICHT GESCANNTEN WERTE
if failed_scans:
    failed_text = ", ".join(failed_scans)
    st.markdown(f"""
        <div style="color: #FF4B4B; font-size: 0.85rem; margin-bottom: 15px; padding: 8px; border: 1px solid rgba(255,75,75,0.2); border-radius: 5px; background: rgba(255,75,75,0.05);">
            ⚠️ <b>Folgende Werte wurden aktuell nicht gescannt:</b><br>{failed_text}
        </div>
    """, unsafe_allow_html=True)

# 4. TABELLEN-AUSGABE (Rest bleibt gleich)
df_sig = pd.DataFrame(signals)
if not df_sig.empty:
    c_t1, c_t2 = st.columns(2)
    with c_t1:
        st.markdown("<h4 style='color:#00FFA3;'>Top 5 CALL (Chance)</h4>", unsafe_allow_html=True)
        calls = df_sig[df_sig['Trend_Val'] > 0].nlargest(5, 'Chance')
        st.table(calls[['Status', 'Aktie', 'Trend', 'Chance']])
    with c_t2:
        st.markdown("<h4 style='color:#1E90FF;'>Top 5 PUT (Chance)</h4>", unsafe_allow_html=True)
        puts = df_sig[df_sig['Trend_Val'] < 0].nsmallest(5, 'Chance')
        st.table(puts[['Status', 'Aktie', 'Trend', 'Chance']])



# --- 5c. DETAIL-ANALYSE (MIT TRADING-SETUP & CHART-LINIEN) ---
st.divider()

# 1. Auswahl & Überschrift
sorted_stocks = sorted(STOCKS_ONLY, key=lambda x: TICKER_NAMES.get(x, x))
sel_stock = st.selectbox("Aktie wählen:", sorted_stocks, format_func=lambda x: TICKER_NAMES.get(x, x))
st.subheader(f"🔍 Detail-Analyse: {TICKER_NAMES.get(sel_stock, sel_stock)}")

res_d = get_analysis(sel_stock)

if res_d["cp"] > 0:
    cp, atr, chance, chg = res_d["cp"], res_d["atr"], res_d["chance"], res_d["chg"]
    
    # Trading-Logik (ATR-basiert)
    risk = atr * 1.5
    reward = risk * 3.0
    if chance >= 50:
        setup_type, setup_color = "LONG (CALL)", "#00FFA3"
        target, stop = cp + reward, cp - risk
    else:
        setup_type, setup_color = "SHORT (PUT)", "#FF4B4B"
        target, stop = cp - reward, cp + risk

    # Status-Banner
    icon_d, color_d, dot_d = get_style(chg)
    st.markdown(f"""
        <div style="background: rgba(255,255,255,0.03); padding: 15px; border-radius: 12px; border-left: 5px solid {setup_color}; margin-bottom: 20px;">
            <span style="font-size: 1.5rem;">{icon_d} {dot_d}</span>
            <b style="font-size: 1.2rem; color: white; margin-left: 10px;">{setup_type} SETUP ({chance}%)</b>
        </div>
    """, unsafe_allow_html=True)

    # --- METRIKEN IN ZWEI ZEILEN ---
    
    # 1. Zeile: Markt-Basisdaten
    r1c1, r1c2, r1c3 = st.columns(3)
    r1c1.metric("KURS", f"{cp:,.2f}", f"{chg:+.2f}%")
    r1c2.metric("ATR (14h)", f"{atr:.2f}")
    r1c3.metric("VOLUMEN", f"{res_d['vol']:,.0f}")

    # 2. Zeile: Trading-Strategie
    r2c1, r2c2, r2c3 = st.columns(3)
    r2c1.metric("CHANCE", f"{chance}%", delta=f"{chance-50}%")
    r2c2.metric("ZIEL (TP)", f"{target:,.2f}", f"{(target/cp-1)*100:+.2f}%")
    r2c3.metric("STOP (SL)", f"{stop:,.2f}", f"{(stop/cp-1)*100:+.2f}%", delta_color="inverse")

    # 3. Grafik (Lückenlose Candlesticks)
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
        df_plot = res_d["df"].tail(60).copy()
        df_plot['x_label'] = df_plot.index.strftime('%d.%m %H:%M')
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Bar(x=df_plot['x_label'], y=df_plot['Volume'], name="Volumen", marker_color='#1E90FF', opacity=0.2), secondary_y=False)
        fig.add_trace(go.Candlestick(x=df_plot['x_label'], open=df_plot['Open'], high=df_plot['High'], low=df_plot['Low'], close=df_plot['Close'], name="Kurs", increasing_line_color='#00FFA3', decreasing_line_color='#FF4B4B'), secondary_y=True)
        
        # Setup-Linien im Chart
        fig.add_hline(y=target, line_dash="dash", line_color="#00FFA3", annotation_text="ZIEL", secondary_y=True)
        fig.add_hline(y=stop, line_dash="dash", line_color="#FF4B4B", annotation_text="STOP", secondary_y=True)
        
        fig.update_layout(height=500, margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False, xaxis_rangeslider_visible=False, xaxis=dict(type='category', tickangle=-45, nticks=12, showgrid=False))
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Grafik-Fehler: {e}")
else:
    st.warning("Keine Daten für dieses Symbol verfügbar.")


    # Metriken-Reihe
    col_d1, col_d2, col_d3, col_d4 = st.columns(4)
    col_d1.metric("KURS", f"{res_d['cp']:,.2f}")
    col_d2.metric("CHANCE", f"{res_d['chance']}%", delta=f"{res_d['chance']-50}%")
    col_d3.metric("ATR (14h)", f"{res_d['atr']:.2f}")
    col_d4.metric("VOLUMEN", f"{res_d['vol']:,.0f}")

    # Candlestick-Grafik (unverändert)
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
        
        df_plot = res_d["df"].tail(60).copy()
        df_plot['x_label'] = df_plot.index.strftime('%d.%m %H:%M')
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Bar(x=df_plot['x_label'], y=df_plot['Volume'], name="Volumen", marker_color='#1E90FF', opacity=0.25), secondary_y=False)
        fig.add_trace(go.Candlestick(x=df_plot['x_label'], open=df_plot['Open'], high=df_plot['High'], low=df_plot['Low'], close=df_plot['Close'], name="Kurs", increasing_line_color='#00FFA3', decreasing_line_color='#FF4B4B'), secondary_y=True)

        fig.update_layout(height=450, margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False, xaxis_rangeslider_visible=False, xaxis=dict(type='category', tickangle=-45, nticks=12, gridcolor='#333', showgrid=False))
        fig.update_yaxes(title_text="Volumen", secondary_y=False, showgrid=False, color="#8892b0")
        fig.update_yaxes(title_text="Kurs", secondary_y=True, gridcolor='#333', side="right")

        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Grafik-Fehler: {e}")
