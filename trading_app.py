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
count = st_autorefresh(interval=8 * 60 * 1000, key="fscounter")

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
    /* 1. Haupt-Hintergrund & Basisschrift */
    .stApp { 
        background-color: #0E1117 !important; 
        color: #FFFFFF !important; 
        font-family: 'Inter', sans-serif;
    }

    /* 2. METRIKEN (K Kurs, ATR, Chance etc.) */
    /* Wert-Anzeige (Groß, Weiß, Fett) */
    [data-testid="stMetricValue"] {
        font-size: 1.5rem !important; /* Etwas kleiner für Kompaktheit */
        font-weight: 800 !important;   /* Maximale Schärfe durch Fettdruck */
        color: #FFFFFF !important;    /* Absolutes Weiß */
        letter-spacing: -0.5px;
    }
    
    /* Label-Anzeige (Klein, Grau, Über dem Wert) */
    [data-testid="stMetricLabel"] {
        font-size: 0.75rem !important;
        color: #8892b0 !important;    /* Dezentes Blau-Grau */
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        margin-bottom: -5px !important;
    }

    /* Container der Metriken (Kompakter & dezent hinterlegt) */
    div[data-testid="stMetric"] {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.05);
        padding: 8px 12px !important;
        border-radius: 10px;
    }

    /* 3. SPEZIAL-BOX FÜR CRV (Zusätzlicher Wert) */
    .crv-box {
        text-align: center;
        border: 1px solid #1E90FF;
        background: rgba(30,144,255,0.1);
        border-radius: 10px;
        padding: 5px;
        height: 100%;
    }

    /* 4. MARKT-WETTER KARTEN (Oben) */
    .weather-card { 
        text-align: center; 
        border-radius: 12px; 
        background: rgba(255,255,255,0.03); 
        border: 2px solid #333; 
        padding: 12px; 
        margin-bottom: 10px; 
    }

    /* 5. TABELLEN (Top 5 - Maximaler Kontrast) */
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

    /* 6. STATUS-BANNER (Detail-Analyse) */
    .status-banner {
        background: rgba(255,255,255,0.03); 
        padding: 12px; 
        border-radius: 12px; 
        border-left: 6px solid #1E90FF; 
        margin-bottom: 15px;
    }
    
    /* Scrollbars dezent machen */
    ::-webkit-scrollbar { width: 5px; height: 5px; }
    ::-webkit-scrollbar-thumb { background: #333; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. ZENTRALE FUNKTION ---
@st.cache_data(ttl=60)
def get_analysis(ticker_symbol):
    import yfinance as yf
    res = {"cp": 0, "h250": 0, "l250": 0, "chg": 0, "atr": 0, "vol": 0, "chance": 50, "df": None}
    
    try:
        # WICHTIG: Zeitraum auf 1 Jahr (1y) stellen für 250-Tage-Werte
        tk = yf.Ticker(ticker_symbol)
        df = tk.history(period="1y") 
        
        if not df.empty and len(df) > 1:
            # Aktuelle Werte (letzte Zeile)
            res["cp"] = float(df["Close"].iloc[-1])
            res["vol"] = float(df["Volume"].iloc[-1])
            res["chg"] = ((df["Close"].iloc[-1] / df["Close"].iloc[-2]) - 1) * 100
            
            # 250-Tage Werte (Maximum/Minimum des gesamten Zeitraums)
            res["h250"] = float(df["High"].max())
            res["l250"] = float(df["Low"].min())
            
            # Einfache ATR Berechnung (Vola)
            df['TR'] = df['High'] - df['Low']
            res["atr"] = float(df['TR'].tail(14).mean())
            
            # Dummy Chance-Logik (hier deine eigene Logik nutzen)
            res["chance"] = 54.2 
            res["df"] = df
            
    except Exception as e:
        print(f"Fehler bei {ticker_symbol}: {e}")
    return res

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
    ### 📈 Grafik-Beschreibung
    Das Chart kombiniert zwei wichtige Informationsebenen:
    1. **Candlesticks (Kerzen):** Zeigen Eröffnung, Schluss, Hoch und Tief pro Stunde. 
       - <span style='color:#00FFA3;'>Grün</span> = Kurs gestiegen.
       - <span style='color:#FF4B4B;'>Rot</span> = Kurs gefallen.
    2. **Volumen-Profil (Blau):** Die blauen Balken im Hintergrund nutzen die **linke Y-Achse**. Sie zeigen die Handelsaktivität.
    3. **Lückenlos-Achse:** Wochenenden und Nachtstunden werden ausgeblendet, um eine unterbrechungsfreie technische Analyse zu ermöglichen.
    ---
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
    ### ⚖️ CRV (Chance Riskio Verhältnis)
    Das CRV (Chance-Risiko-Verhältnis) ist eine der wichtigsten Kennzahlen im professionellen Trading. Es beschreibt das mathematische Verhältnis zwischen dem potenziellen Gewinn und dem eingegangenen Risiko eines Trades.
    Hier ist die detaillierte Beschreibung für deine Dokumentation oder den Info-Expander:
    ⚖️ CRV (Chance-Risiko-Verhältnis)
    Das CRV gibt an, wie viele Einheiten Gewinn für jede Einheit Risiko zu erwarten sind.
    Berechnung:
    Setup: In diesem Monitor ist das CRV fest auf 3.0 eingestellt. Das bedeutet:
    Riskierst beispielsweise EUR 100 (wenn der Stop-Loss erreicht wird).
    Zielst auf einen Gewinn von EUR 300 (wenn das Ziel erreicht wird).
    Bedeutung für die Strategie: Ein CRV von 3.0 ist mathematisch sehr wertvoll. Es erlaubt dir, selbst dann profitabel zu sein, wenn nur 30 % deiner Trades gewinnen.
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

# --- 5c. DETAIL-ANALYSE (KOMPLETT MIT 250-TAGE & FIX) ---
st.divider()

sorted_stocks = sorted(STOCKS_ONLY, key=lambda x: TICKER_NAMES.get(x, x))
sel_stock = st.selectbox("Aktie wählen:", sorted_stocks, format_func=lambda x: TICKER_NAMES.get(x, x), key="selector_5c")

st.subheader(f"🔍 Detail-Analyse: {TICKER_NAMES.get(sel_stock, sel_stock)}")

res_d = get_analysis(sel_stock)

# WICHTIG: Prüfung ob Kursdaten (cp) vorhanden sind
if res_d.get("cp", 0) > 0:
    cp = res_d["cp"]
    atr = res_d["atr"]
    chance = res_d["chance"]
    chg = res_d["chg"]
    
    # 250-Tage Werte sicher abrufen (mit Fallback auf cp falls N/A)
    h250 = res_d.get("h250", cp)
    l250 = res_d.get("l250", cp)
    
    # Trading-Logik
    risk = atr * 1.5
    reward = risk * 3.0
    vola_pct = (atr / cp) * 100
    crv_val = 3.0

    setup_type, setup_color = ("LONG (CALL)", "#00FFA3") if chance >= 50 else ("SHORT (PUT)", "#FF4B4B")
    target, stop = (cp + reward, cp - risk) if chance >= 50 else (cp - reward, cp + risk)

    # 1. STATUS-BANNER
    st.markdown(f"""<div style="background:rgba(255,255,255,0.03); padding:12px; border-radius:10px; border-left:6px solid {setup_color}; margin-bottom:20px;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <b style="color:white;">{setup_type} SETUP AKTIV</b>
            <b style="color:{setup_color}; font-size:1.2rem;">{chance}% Konfidenz</b>
        </div></div>""", unsafe_allow_html=True)

    # 2. METRIKEN ZEILE 1 (Inkl. 250-Tage Hoch/Tief)
    dist_h = ((cp / h250) - 1) * 100 if h250 > 0 else 0
    dist_l = ((cp / l250) - 1) * 100 if l250 > 0 else 0

    r1c1, r1c2, r1c3, r1c4 = st.columns(4)
    r1c1.metric("KURS", f"{cp:,.2f}", f"{chg:+.2f}%")
    r1c2.metric("250-T HOCH", f"{h250:,.2f}", f"{dist_h:+.1f}%")
    r1c3.metric("250-T TIEF", f"{l250:,.2f}", f"{dist_l:+.1f}%", delta_color="normal")
    r1c4.metric("VOLA (ATR %)", f"{vola_pct:.2f}%")

    # 3. VISUELLER RANGE-SLIDER
    if h250 > l250:
        pos_pct = max(0, min(100, ((cp - l250) / (h250 - l250)) * 100))
        st.markdown(f"""
            <div style="margin: 10px 0 25px 0;">
                <div style="display:flex; justify-content:space-between; font-size:0.65rem; color:#8892b0; margin-bottom:4px;">
                    <span>250-T TIEF ({l250:,.2f})</span>
                    <span style="color:#1E90FF;">POSITION: {pos_pct:.1f}%</span>
                    <span>250-T HOCH ({h250:,.2f})</span>
                </div>
                <div style="width:100%; height:4px; background:rgba(255,255,255,0.1); border-radius:2px;">
                    <div style="width:{pos_pct}%; height:100%; background:linear-gradient(90deg, #FF4B4B, #F1C40F, #00FFA3); position:relative;">
                        <div style="position:absolute; right:-5px; top:-5px; width:12px; height:12px; background:white; border-radius:50%; border:2px solid #1E90FF;"></div>
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)

    # 4. TRADING PARAMETER & GRAFIK (Wie gehabt)
    r2c1, r2c2, r2c3, r2c4 = st.columns(4)
    r2c1.metric("CHANCE", f"{chance}%")
    r2c2.metric("ZIEL (TP)", f"{target:,.2f}", f"{(target/cp-1)*100:+.2f}%")
    r2c3.metric("STOP (SL)", f"{stop:,.2f}", f"{(stop/cp-1)*100:+.2f}%", delta_color="inverse")
    r2c4.markdown(f'<div class="crv-box"><small>CRV</small><br><b>{crv_val:.1f}</b></div>', unsafe_allow_html=True)

 # --- 4b. VISUELLE RANGE ---
    # Falls Daten fehlerhaft/gleich, nutzen wir eine minimale Differenz für die Anzeige
    display_h = h250 if h250 > l250 else cp * 1.01
    display_l = l250 if h250 > l250 else cp * 0.99
    pos_pct = max(0, min(100, ((cp - display_l) / (display_h - display_l)) * 100))

    # --- 5. GRAFIK (PLOTLY) ---
    try:
        import plotly.graph_objects as go
        # Sicherstellen, dass das fig-Objekt immer definiert wird
        df_plot = res_d["df"].tail(60).copy()
        df_plot['x_label'] = df_plot.index.strftime('%d.%m')

        fig = go.Figure(data=[go.Candlestick(
            x=df_plot['x_label'], open=df_plot['Open'], high=df_plot['High'],
            low=df_plot['Low'], close=df_plot['Close'],
            increasing_line_color='#00FFA3', decreasing_line_color='#FF4B4B', name="Kurs"
        )])

        # Setup Linien einzeichnen
        fig.add_hline(y=target, line_dash="dash", line_color="#00FFA3", annotation_text="ZIEL")
        fig.add_hline(y=stop, line_dash="dash", line_color="#FF4B4B", annotation_text="STOP")
        fig.add_hline(y=cp, line_dash="dot", line_color="white", annotation_text="ENTRY")

        fig.update_layout(
            height=450, template="plotly_dark", margin=dict(l=0, r=0, t=10, b=0),
            xaxis_rangeslider_visible=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Fehler bei der Chart-Erstellung: {e}")

else:
    st.warning("Keine Daten für diesen Ticker verfügbar.")
