import streamlit as st
import pandas as pd
import numpy as np
# import finnhub as fh
# finnhub_client = finnhub.Client(api_key=api_key)
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- 1. KONFIGURATION ---
st.set_page_config(page_title="Live Swing-Monitor", layout="wide")

ASSETS = {
    "DE": {"ADS.DE": "🇩🇪 Adidas", "AIR.DE": "🇩🇪 Airbus", "ALV.DE": "🇩🇪 Allianz", "BAS.DE": "🇩🇪 BASF",
    "BAYN.DE": "🇩🇪 Bayer", "BEI.DE": "🇩🇪 Beiersdorf", "BMW.DE": "🇩🇪 BMW", "BNR.DE": "🇩🇪 Brenntag",
    "CBK.DE": "🇩🇪 Commerzbank", "CON.DE": "🇩🇪 Continental", "1COV.DE": "🇩🇪 Covestro",
    "DTG.DE": "🇩🇪 Daimler Truck", "DBK.DE": "🇩🇪 Deutsche Bank", "DB1.DE": "🇩🇪 Deutsche Börse",
    "DHL.DE": "🇩🇪 DHL Group", "DTE.DE": "🇩🇪 Deutsche Telekom", "EOAN.DE": "🇩🇪 E.ON",
    "FRE.DE": "🇩🇪 Fresenius", "FME.DE": "🇩🇪 Fresenius Medical Care", "G1A.DE": "🇩🇪 GEA Group", "HEI.DE": "🇩🇪 Heidelberg Materials", "HNR1.DE": "🇩🇪 Hannover Rück", "HEN3.DE": "🇩🇪 Henkel", "IFX.DE": "🇩🇪 Infineon", "MBG.DE": "🇩🇪 Mercedes-Benz", "MRK.DE": "🇩🇪 Merck",
    "MTX.DE": "🇩🇪 MTU Aero Engines", "MUV2.DE": "🇩🇪 Münchener Rück", "PAH3.DE": "🇩🇪 Porsche SE",
    "PUM.DE": "🇩🇪 Puma", "QIA.DE": "🇩🇪 Qiagen", "RHM.DE": "🇩🇪 Rheinmetall", "RWE.DE": "🇩🇪 RWE",
    "SAP.DE": "🇩🇪 SAP", "SRT3.DE": "🇩🇪 Sartorius", "G24.DE": "🇩🇪 Scout24", "SIE.DE": "🇩🇪 Siemens", "ENR.DE": "🇩🇪 Siemens Energy", "SHL.DE": "🇩🇪 Siemens Healthineers", "SY1.DE": "🇩🇪 Symrise",
    "TKA.DE": "🇩🇪 Thyssenkrupp", "VOW3.DE": "🇩🇪 Volkswagen", "VNA.DE": "🇩🇪 Vonovia", "ZAL.DE": "🇩🇪 Zalando"},

    "US": {"AAPL": "🇺🇸 Apple", "MSFT": "🇺🇸 Microsoft", "GOOGL": "🇺🇸 Alphabet (A)", "GOOG": "🇺🇸 Alphabet (C)",
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
    "ADI": "🇺🇸 Analog Devices", "ANSS": "🇺🇸 Ansys", "CDNS": "🇺🇸 Cadence", "CPRT": "🇺🇸 Copart", "CTAS": "🇺🇸 Cintas", "CSX": "🇺🇸 CSX Corp", "DLTR": "🇺🇸 Dollar Tree", "DXCM": "🇺🇸 DexCom", "FAST": "🇺🇸 Fastenal", "IDXX": "🇺🇸 IDEXX Labs", "KDP": "🇺🇸 Keurig Dr Pepper", "MAR": "🇺🇸 Marriott", "ODFL": "🇺🇸 Old Dominion", "PAYX": "🇺🇸 Paychex", "VRSK": "🇺🇸 Verisk"},

    "EU": # Frankreich (🇫🇷)
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
INDEX_MAP = {"^GDAXI": "DAX", "^STOXX50E": "EUROSTOXX 50", "^IXIC": "NASDAQ", "XU100.IS": "BIST 100", "^NSEI": "NIFTY 50"}

# --- 2. SICHERHEITS-FUNKTIONEN (Verhindert den ValueError) ---
def safe_float(val):
    """Extrahiert sicher einen einzelnen Float-Wert aus Series oder Arrays."""
    if isinstance(val, (pd.Series, np.ndarray, pd.DataFrame)):
        return float(val.iloc[-1]) if hasattr(val, 'iloc') else float(val[0])
    return float(val)

def get_logic_icons(chg):
    chg = safe_float(chg) # Sicherstellen, dass chg eine Zahl ist
    weather = "☀️" if chg > 0.5 else "⛈️" if chg < -0.5 else "☁️"
    dot = "🟢" if chg > 0.4 else "🔵" if chg < -0.4 else "⚪"
    return weather, dot

@st.cache_data(ttl=300)
def get_live_data(ticker, period="60d", interval="1d"):
    try:
        df = yf.download(ticker, period=period, interval=interval, progress=False)
        return df if not df.empty else None
    except: return None

def analyze_swing(ticker, df):
    cp = safe_float(df['Close'].iloc[-1])
    # 3-Tage Änderung (Swing)
    prev_3d = safe_float(df['Close'].iloc[-4])
    chg_3d = ((cp / prev_3d) - 1) * 100
    
    df['TR'] = np.maximum(df['High'] - df['Low'], np.maximum(abs(df['High'] - df['Close'].shift(1)), abs(df['Low'] - df['Close'].shift(1))))
    atr = safe_float(df['TR'].tail(14).mean())
    df['SMA20'] = df['Close'].rolling(window=20).mean()
    is_bullish = cp > safe_float(df['SMA20'].iloc[-1])
    
    weather, dot = get_logic_icons(chg_3d)
    chance = round(50.0 + (15 if is_bullish else -10) + (abs(chg_3d) * 0.8), 2)
    return {"cp": cp, "chg_3d": chg_3d, "atr": atr, "weather": weather, "dot": dot, "chance": chance, "df": df}

# --- 3. HEADER: EUR/USD ---
eurusd_df = get_live_data("EURUSD=X", period="5d")
if eurusd_df is not None:
    cp = safe_float(eurusd_df['Close'].iloc[-1])
    prev = safe_float(eurusd_df['Close'].iloc[-2])
    chg = ((cp / prev) - 1) * 100
    w, dot = get_logic_icons(chg)
    st.markdown(f"<h1 style='text-align: center; color: #5DADE2;'>{w} EUR / USD: {cp:.6f} {dot}</h1>", unsafe_allow_html=True)
st.divider()

# --- 4. INDIZES ---
st.subheader("🌍 Globale Markt-Indikation")
idx_keys = list(INDEX_MAP.keys())
r1 = st.columns(3)
for i in range(3):
    sym = idx_keys[i]; df = get_live_data(sym, period="5d")
    if df is not None:
        cp = safe_float(df['Close'].iloc[-1]); prev = safe_float(df['Close'].iloc[-2])
        chg = ((cp / prev) - 1) * 100; w, dot = get_logic_icons(chg)
        r1[i].metric(f"{w} {INDEX_MAP[sym]}", f"{cp:,.2f}", f"{dot} {chg:.2f}%", delta_color="normal" if chg >= 0 else "inverse")

r2 = st.columns(3)
for i in range(3, 5):
    sym = idx_keys[i]; df = get_live_data(sym, period="5d")
    if df is not None:
        cp = safe_float(df['Close'].iloc[-1]); prev = safe_float(df['Close'].iloc[-2])
        chg = ((cp / prev) - 1) * 100; w, dot = get_logic_icons(chg)
        r2[i-3].metric(f"{w} {INDEX_MAP[sym]}", f"{cp:,.2f}", f"{dot} {chg:.2f}%", delta_color="normal" if chg >= 0 else "inverse")

st.divider()

# --- 5. TOP 7 CHANCEN ---
rank_list = []
for t in ALL_TICKERS:
    df = get_live_data(t)
    if df is not None:
        res = analyze_swing(t, df)
        rank_list.append({"Aktie": f"{res['weather']} {TICKER_TO_NAME[t]}", "Signal": f"{res['dot']} {'CALL' if res['chg_3d'] > 0 else 'PUT'}", 
                          "Wahrscheinlichkeit (%)": f"{res['chance']:.2f}", "Trend 3D": f"{res['chg_3d']:.2f}%", "Kurs": f"{res['cp']:.2f} €"})

if rank_list:
    st.table(pd.DataFrame(rank_list).sort_values(by="Wahrscheinlichkeit (%)", ascending=False).head(7))

# --- 6. DETAIL & ORDER ---
# --- 6. DETAIL & ORDER MIT RISK MANAGEMENT ---
st.divider()
st.subheader("🎯 Trade-Planer & Risikokalkulation")

# Risiko-Parameter in der Sidebar oder direkt über dem Tool
with st.sidebar:
    st.header("🛡️ Konto-Einstellungen")
    account_size = st.number_input("Kontogröße (€)", value=10000, step=1000)
    risk_per_trade_pct = st.slider("Risiko pro Trade (%)", 0.5, 5.0, 1.0)
    max_loss_amount = account_size * (risk_per_trade_pct / 100)

reg = st.radio("Region wählen:", ["DE", "US", "EU", "BIO"], horizontal=True)
sel = st.selectbox("Asset für Detail-Analyse:", list(ASSETS[reg].keys()), format_func=lambda x: ASSETS[reg][x])

if sel in all_data:
    df_sel = all_data[sel]
    det = analyze_swing(sel, df_sel)
    
    # --- MATHEMATISCHES RISK-MANAGEMENT ---
    direction = 1 if det['chg_3d'] > 0 else -1
    
    # 1. Stop-Loss basierend auf 2x ATR (Marktrauschen)
    stop_distance = 2.0 * det['atr']
    sl_price = det['cp'] - (stop_distance * direction)
    tp_price = det['cp'] + (4.0 * det['atr'] * direction) # CRV 2:1
    
    # 2. Risiko-Metriken
    risk_pct = abs(sl_price / det['cp'] - 1) # Prozentualer Abstand zum Stop
    
    if risk_pct > 0:
        # Positionsgröße: Wieviel Euro bewegen, damit bei SL genau 'max_loss_amount' verloren geht
        pos_size_euro = max_loss_amount / risk_pct
        # Smart Hebel: Der Hebel, bei dem der SL einem Totalverlust des eingesetzten Kapitals entspräche
        smart_leverage = 1.0 / risk_pct
    else:
        pos_size_euro = 0
        smart_leverage = 1.0

    # --- UI METRIKEN ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("POSITIONSGRÖSSE", f"{pos_size_euro:,.2f} €", "Empf. Volumen")
    c2.metric("STOP-LOSS", f"{sl_price:.2f} €", f"-{risk_pct*100:.2f}% Risiko")
    c3.metric("MAX. VERLUST", f"{max_loss_amount:.2f} €", f"{risk_per_trade_pct}% vom Konto")
    c4.metric("SMART HEBEL", f"x{min(smart_leverage, 20):.1f}", "Max. empfohlen")

    # --- DETAILLIERTE BESTELLUNG (ORDER-EXTENDER) ---
    with st.expander("📝 Professionelles Risk-Shield Ticket", expanded=True):
        st.markdown(f"### 🛒 Order-Ticket: {TICKER_TO_NAME[sel]}")
        
        col_o1, col_o2 = st.columns(2)
        with col_o1:
            st.markdown("**Strategie-Details:**")
            st.write(f"🔹 **Richtung:** {'🟢 LONG / CALL' if direction == 1 else '🔵 SHORT / PUT'}")
            st.write(f"🔹 **Aktueller Kurs:** {det['cp']:.2f} €")
            st.write(f"🔹 **Stückzahl (ca.):** {int(pos_size_euro / det['cp'])} Stück")
            st.write(f"🔹 **Einsatz Kapital:** {min(pos_size_euro, account_size):,.2f} €")

        with col_o2:
            st.markdown("**Exit-Parameter:**")
            st.write(f"🛑 **Hard Stop-Loss:** {sl_price:.2f} €")
            st.write(f"🎯 **Kursziel (Take Profit):** {tp_price:.2f} €")
            st.write(f"⚖️ **CRV:** 2.0")
            st.write(f"⚡ **Hebel-Limit:** x{min(smart_leverage, 15):.1f}")

        st.markdown("---")
        # Broker-Copy Code
        order_text = f"ORDER: {TICKER_TO_NAME[sel]} | {('CALL' if direction==1 else 'PUT')} | VOL: {pos_size_euro:.0f}€ | SL: {sl_price:.2f} | TP: {tp_price:.2f}"
        st.code(order_text, language="text")
        
        if risk_pct > 0.08:
            st.warning("⚠️ Achtung: Hohe Volatilität! Der Stop-Loss ist weit entfernt. Positionsgröße strikt einhalten.")

    # --- CHARTING ---
    fig = go.Figure(data=[go.Candlestick(
        x=det['df'].index,
        open=det['df']['Open'],
        high=det['df']['High'],
        low=det['df']['Low'],
        close=det['df']['Close'],
        name="Kurs"
    )])
    
    # Stop-Loss und Take-Profit Linien
    fig.add_hline(y=sl_price, line_dash="dash", line_color="red", annotation_text="STOP-LOSS")
    fig.add_hline(y=tp_price, line_dash="dash", line_color="green", annotation_text="ZIEL (TP)")
    
    fig.update_layout(
        height=500, 
        template="plotly_dark", 
        xaxis_rangeslider_visible=False,
        margin=dict(l=10, r=10, t=10, b=10)
    )
    st.plotly_chart(fig, use_container_width=True)
