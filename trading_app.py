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
# --- 2. SICHERHEITS-FUNKTIONEN & INDIKATOREN ---
def safe_float(val):
    """Extrahiert sicher einen einzelnen Float-Wert aus Series oder Arrays."""
    if isinstance(val, (pd.Series, np.ndarray, pd.DataFrame)):
        return float(val.iloc[-1]) if hasattr(val, 'iloc') else float(val[0])
    return float(val)

def get_logic_icons(chg):
    chg = safe_float(chg)
    weather = "☀️" if chg > 0.5 else "⛈️" if chg < -0.5 else "☁️" 
    dot = "🟢" if chg > 0.4 else "🔴" if chg < -0.4 else "⚪"
    return weather, dot

def calculate_rsi(df, periods=14):
    """Berechnet den Relative Strength Index (RSI)."""
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

@st.cache_data(ttl=300)
def get_live_data(ticker, period="60d", interval="1d"):
    try:
        df = yf.download(ticker, period=period, interval=interval, progress=False)
        return df if not df.empty else None
    except: 
        return None

def analyze_swing(ticker, df):
    cp = safe_float(df['Close'].iloc[-1])
    prev_3d = safe_float(df['Close'].iloc[-4])
    chg_3d = ((cp / prev_3d) - 1) * 100
    
    # 1. Volatilität (ATR)
    df['TR'] = np.maximum(df['High'] - df['Low'], np.maximum(abs(df['High'] - df['Close'].shift(1)), abs(df['Low'] - df['Close'].shift(1))))
    atr = safe_float(df['TR'].tail(14).mean())
    
    # 2. Trend & Momentum-Filter (SMA200 & RSI)
    df['SMA20'] = df['Close'].rolling(window=20).mean()
    df['SMA200'] = df['Close'].rolling(window=200).mean() if len(df) >= 200 else df['Close'].rolling(window=20).mean()
    df['RSI'] = calculate_rsi(df)
    
    last_rsi = safe_float(df['RSI'].iloc[-1])
    is_bullish = cp > safe_float(df['SMA20'].iloc[-1])
    market_trend_long = cp > safe_float(df['SMA200'].iloc[-1])
    
    # NEUE STRATEGIE: Swing-Trading sucht Mean Reversion (Überverkauft im Bullenmarkt)
    # Ein CALL wird generiert, wenn die Aktie im langfristigen Aufwärtstrend korrigiert (RSI < 45)
    # Ein PUT wird generiert, wenn die Aktie im langfristigen Abwärtstrend überhitzt ist (RSI > 55)
    if market_trend_long and last_rsi < 45:
        direction = 1  # CALL
        chance = 65.0 + (abs(50 - last_rsi) * 0.5)
    elif not market_trend_long and last_rsi > 55:
        direction = -1 # PUT
        chance = 60.0 + (abs(last_rsi - 50) * 0.5)
    else:
        direction = 1 if chg_3d > 0 else -1
        chance = 45.0 + (abs(chg_3d) * 0.2) # Geringere Wahrscheinlichkeit für reines Rauschen
        
    weather, dot = get_logic_icons(chg_3d)
    
    return {
        "cp": cp, "chg_3d": chg_3d, "atr": atr, "weather": weather, 
        "dot": dot, "chance": chance, "direction": direction, "df": df
    }

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
# Dynamischer Schutz gegen Index-Länge
available_indices = len(idx_keys)
for i in range(3, min(6, available_indices)):
    sym = idx_keys[i]; df = get_live_data(sym, period="5d")
    if df is not None:
        cp = safe_float(df['Close'].iloc[-1]); prev = safe_float(df['Close'].iloc[-2])
        chg = ((cp / prev) - 1) * 100; w, dot = get_logic_icons(chg)
        r2[i-3].metric(f"{w} {INDEX_MAP[sym]}", f"{cp:,.2f}", f"{dot} {chg:.2f}%", delta_color="normal" if chg >= 0 else "inverse")
st.divider()

# --- 5. TOP 7 CHANCEN ---
rank_list = []
for t in ALL_TICKERS:
    df = get_live_data(t, period="200d") 
    if df is not None and len(df) > 20:
        res = analyze_swing(t, df)
        # NEU: Hole den aktuellen RSI-Wert für die Anzeige
        last_rsi = safe_float(res['df']['RSI'].iloc[-1])
        
        rank_list.append({
            "Aktie": f"{res['weather']} {TICKER_TO_NAME[t]}", 
            "Signal": f"{res['dot']} {'CALL' if res['direction']==1 else 'PUT'}", 
            "RSI (14)": f"{last_rsi:.1f}", # NEUE SICHTBARE SPALTE
            "Wahrscheinlichkeit (%)": f"{res['chance']:.2f}", 
            "Trend 3D": f"{res['chg_3d']:.2f}%", 
            "Kurs": f"{res['cp']:.2f} €"
        })
if rank_list:
    # Sortierung nach Wahrscheinlichkeit
    st.table(pd.DataFrame(rank_list).sort_values(by="Wahrscheinlichkeit (%)", ascending=False).head(7))

# --- 6. DETAIL & ORDER ---
st.divider()
reg = st.radio("Region:", ["DE", "US", "EU"], horizontal=True)
sel = st.selectbox("Aktie:", list(ASSETS[reg].keys()), format_func=lambda x: ASSETS[reg][x])
df_sel = get_live_data(sel, period="200d")

if df_sel is not None and len(df_sel) > 20:
    det = analyze_swing(sel, df_sel)
    direction = det['direction']
    
    # Werte für die Anzeige extrahieren
    last_rsi = safe_float(det['df']['RSI'].iloc[-1])
    sma200_val = safe_float(det['df']['SMA200'].iloc[-1])
    market_trend_long = det['cp'] > sma200_val
    trend_status = "📈 Bullish (Über SMA200)" if market_trend_long else "📉 Bearish (Unter SMA200)"
    
    if direction == 1:
        sl = det['cp'] - (2.0 * det['atr'])
        tp = det['cp'] + (4.0 * det['atr']) 
    else:
        sl = det['cp'] + (2.0 * det['atr'])
        tp = det['cp'] - (4.0 * det['atr']) 
        
    dist = abs((sl / det['cp']) - 1)
    opt_h = 0.20 / dist if dist > 0 else 1.0 
    
    # NEU: Aufteilung in 5 Spalten statt 4 für maximale optische Transparenz
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("SIGNAL", f"{det['dot']} {'CALL' if direction==1 else 'PUT'}", f"Wetter: {det['weather']}")
    c2.metric("MOMENTUM (RSI)", f"{last_rsi:.1f}", "Überverkauft < 45" if direction==1 else "Überkauft > 55")
    c3.metric("STOP-LOSS", f"{sl:.2f} €", f"{dist*100:.2f}% Puffer")
    c4.metric("SMART HEBEL", f"x{opt_h:.1f}")
    c5.metric("WAHRSCH. (%)", f"{det['chance']:.2f}")
    
    with st.expander("📝 Detaillierte Handelsanweisung (Broker-Ready)", expanded=True):
        st.markdown(f"### Order-Ticket: {TICKER_TO_NAME[sel]}")
        col_o1, col_o2 = st.columns(2)
        
        with col_o1:
            st.markdown("**Basis-Informationen:**")
            st.write(f"🔹 **Richtung:** {'🟢 LONG / CALL' if direction == 1 else '🔵 SHORT / PUT'}")
            st.write(f"🔹 **Asset:** {TICKER_TO_NAME[sel]} ({sel})")
            st.write(f"🔹 **Referenzkurs:** {det['cp']:.2f} €")
            st.write(f"🔹 **Langzeittrend:** {trend_status}") # NEUE ANZEIGE IN DER NAVIGATION
        with col_o2:
            st.markdown("**Derivate-Parameter:**")
            st.write(f"🎯 **Ziel-Hebel:** x{opt_h:.1f}")
            st.write(f"🛑 **Stop-Loss (Basis):** {sl:.2f} €")
            st.write(f"🏁 **Kursziel (Basis):** {tp:.2f} €")
            st.write(f"⏳ **Haltedauer:** 3 - 5 Handelstage")
        st.markdown("---")
        
        st.info(f"""
        **Strategie-Check & Execution:**
        1. **Einstieg:** Signal basiert auf RSI ({last_rsi:.1f}) im Kontext des Langzeittrends ({trend_status}).
        2. **Risiko-Limit:** Der Hebel von x{opt_h:.1f} basiert auf der ATR-Volatilität ({det['atr']:.2f} €).
        3. **Exit-Logik:** Konsequent glattstellen bei {tp:.2f} € (Ziel) oder {sl:.2f} € (Stopp).
        """)
        
        order_text = f"ORDER: {TICKER_TO_NAME[sel]} | {('CALL' if direction==1 else 'PUT')} | Hebel x{opt_h:.1f} | SL: {sl:.2f} | TP: {tp:.2f}"
        st.code(order_text, language="text")
        
# --- AB HIER ERSETZEN: VISUALISIERUNG & TRADING-LOGBUCH ---
    with st.expander("📊 Chart-Analyse & RSI", expanded=True):
        st.write(f"**Basis:** {sel} | **Kurs:** {det['cp']:.2f} € | **Hebel:** x{opt_h:.1f}")
        
        # Subplots erstellen: Oben Candlesticks, Unten RSI
        from plotly.subplots import make_subplots
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                            vertical_spacing=0.05, row_heights=[0.7, 0.3])
        
        # 1. Candlestick-Chart (Oben)
        fig.add_trace(go.Candlestick(
            x=det['df'].index, open=det['df']['Open'], high=det['df']['High'], 
            low=det['df']['Low'], close=det['df']['Close'], name="Kurs"
        ), row=1, col=1)
        
        # Indikatoren-Linien im Hauptchart
        fig.add_trace(go.Scatter(x=det['df'].index, y=det['df']['SMA20'], name="SMA 20", line=dict(color='orange', width=1)), row=1, col=1)
        fig.add_trace(go.Scatter(x=det['df'].index, y=det['df']['SMA200'], name="SMA 200", line=dict(color='magenta', width=1.5)), row=1, col=1)
        
        # Stop-Loss und Take-Profit Linien
        fig.add_hline(y=sl, line_dash="dash", line_color="red", annotation_text="SL", row=1, col=1)
        fig.add_hline(y=tp, line_dash="dash", line_color="green", annotation_text="TP", row=1, col=1)
        
        # 2. RSI-Chart (Unten)
        fig.add_trace(go.Scatter(x=det['df'].index, y=det['df']['RSI'], name="RSI (14)", line=dict(color='cyan', width=1.5)), row=2, col=1)
        
        # RSI Schwellenwerte (30, 50, 70 oder deine Logik 45/55)
        fig.add_hline(y=70, line_dash="dot", line_color="gray", row=2, col=1)
        fig.add_hline(y=50, line_dash="dash", line_color="dimgray", row=2, col=1)
        fig.add_hline(y=30, line_dash="dot", line_color="gray", row=2, col=1)
        
        fig.update_layout(height=600, template="plotly_dark", xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

    # --- NEU: VIRTUELLES LOGBUCH & BACKTEST-SIMULATOR ---
    st.divider()
    st.subheader("📓 Virtuelles Trading-Logbuch")
    
    # Session State für das Logbuch initialisieren falls nicht vorhanden
    if 'trading_journal' not in st.session_state:
        st.session_state['trading_journal'] = []
        
    log_c1, log_c2 = st.columns([1, 2])
    
    with log_c1:
        st.markdown("**Trade zu Logbuch hinzufügen:**")
        position_size = st.number_input("Einsatz (€):", value=500, step=50)
        
        if st.button("🚀 Position simulieren & loggen"):
            new_trade = {
                "Datum": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Asset": TICKER_TO_NAME[sel],
                "Ticker": sel,
                "Typ": 'CALL (Long)' if direction == 1 else 'PUT (Short)',
                "Einstieg (€)": round(det['cp'], 2),
                "Hebel": round(opt_h, 1),
                "Stop-Loss (€)": round(sl, 2),
                "Take-Profit (€)": round(tp, 2),
                "Einsatz (€)": position_size,
                "Status": "Offen ⏳"
            }
            st.session_state['trading_journal'].append(new_trade)
            st.success(f"Erfolgreich geloggt: {TICKER_TO_NAME[sel]} {new_trade['Typ']}")

    with log_c2:
        st.markdown("**Aktive & Vergangene Simulationen:**")
        if st.session_state['trading_journal']:
            journal_df = pd.DataFrame(st.session_state['trading_journal'])
            st.dataframe(journal_df, use_container_width=True)
            
            if st.button("🗑️ Logbuch zurücksetzen"):
                st.session_state['trading_journal'] = []
                st.rerun()
        else:
            st.info("Noch keine simulierten Trades im Logbuch vorhanden. Nutze den Button links, um Starbucks oder andere Signale zu testen!")
   
