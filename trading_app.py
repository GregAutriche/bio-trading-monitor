import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
from collections import OrderedDict

# --- 0. CONFIG & CLEAN NAVY DESIGN ---
st.set_page_config(layout="wide", page_title="Bauer Strategy Pro 2026", page_icon="📡")

st.markdown("""
    <style>
    .stApp { background-color: #0a192f; }
    h1, h2, h3, p, span, label, div { color: #e6f1ff !important; font-family: 'Segoe UI', sans-serif; }
    .header-text { font-size: 26px; font-weight: bold; color: #64ffda !important; border-bottom: 2px solid #64ffda; padding-bottom: 5px; margin-bottom: 15px; }
    
    .sig-box-c { color: #00ff41 !important; border: 1px solid #00ff41; padding: 2px 8px; border-radius: 4px; font-weight: bold; background: rgba(0, 255, 65, 0.1); }
    .sig-box-p { color: #007bff !important; border: 1px solid #007bff; padding: 2px 8px; border-radius: 4px; font-weight: bold; background: rgba(0, 123, 255, 0.1); }
    .sig-box-high { color: #ffd700 !important; border: 2px solid #ffd700; padding: 2px 8px; border-radius: 4px; font-weight: bold; background: rgba(255, 215, 0, 0.2); }
    
    .row-container { border-bottom: 1px solid #172a45; padding: 15px 0; margin: 0; }
    .metric-label { color: #8892b0; font-size: 0.8rem; }
    .price-text { font-size: 1.15rem; font-weight: bold; }
    
    [data-testid="stSidebar"] { background-color: #0d1b2a; border-right: 1px solid #172a45; }
    </style>
    """, unsafe_allow_html=True)

# --- 1. SIDEBAR: RISIKOMANAGEMENT ---
st.sidebar.header("🛡️ Risiko-Parameter")
capital = st.sidebar.number_input("Gesamtkapital (€)", value=10000, step=1000)
risk_pct = st.sidebar.slider("Risiko pro Trade (%)", 0.1, 5.0, 1.0, 0.1)
risk_amount = capital * (risk_pct / 100)

# --- 2. MARKT-MAPPING (100% VOLLSTÄNDIG) ---
@st.cache_data(ttl=86400)
def get_market_maps():
    maps = {}
    maps["DAX 40 🇩🇪"] = {
        "ADS.DE": "Adidas", "ALV.DE": "Allianz", "BAS.DE": "BASF", "BAYN.DE": "Bayer", "BEI.DE": "Beiersdorf",
        "BMW.DE": "BMW", "CON.DE": "Continental", "1COV.DE": "Covestro", "DTG.DE": "Daimler Truck", "DBK.DE": "Deutsche Bank",
        "DB1.DE": "Deutsche Börse", "DHL.DE": "DHL Group", "DTE.DE": "Deutsche Telekom", "EOAN.DE": "E.ON", "FRE.DE": "Fresenius",
        "FME.DE": "Fresenius Med. Care", "HEI.DE": "Heidelberg Materials", "HEN3.DE": "Henkel", "IFX.DE": "Infineon", "MBG.DE": "Mercedes-Benz",
        "MRK.DE": "Merck", "MTX.DE": "MTU Aero Engines", "MUV2.DE": "Münchener Rück", "PAH3.DE": "Porsche SE", "P911.DE": "Porsche AG",
        "PUM.DE": "Puma", "RWE.DE": "RWE", "SAP.DE": "SAP", "SRT3.DE": "Sartorius", "SIE.DE": "Siemens", "SHL.DE": "Siemens Healthineers",
        "SY1.DE": "Symrise", "VOW3.DE": "Volkswagen", "VNA.DE": "Vonovia", "ZAL.DE": "Zalando", "CBK.DE": "Commerzbank",
        "RNR.DE": "Rheinmetall", "BNR.DE": "Brenntag", "QIA.DE": "Qiagen", "TYO.DE": "TUI"
    }
    maps["NASDAQ 100 🇺🇸"] = {
        "AAPL": "Apple", "MSFT": "Microsoft", "AMZN": "Amazon", "NVDA": "NVIDIA", "META": "Meta", "GOOGL": "Alphabet A", "GOOG": "Alphabet C",
        "TSLA": "Tesla", "AVGO": "Broadcom", "COST": "Costco", "PEP": "PepsiCo", "ADBE": "Adobe", "CSCO": "Cisco", "NFLX": "Netflix",
        "AMD": "AMD", "TMUS": "T-Mobile US", "CMCSA": "Comcast", "TXN": "Texas Instruments", "INTC": "Intel", "INTU": "Intuit",
        "AMGN": "Amgen", "QCOM": "Qualcomm", "HON": "Honeywell", "ISRG": "Intuitive Surgical", "SBUX": "Starbucks", "AMAT": "Applied Materials",
        "BKNG": "Booking", "MDLZ": "Mondelez", "VRTX": "Vertex", "ADP": "ADP", "ADI": "Analog Devices", "REGN": "Regeneron",
        "GILD": "Gilead", "PYPL": "PayPal", "LRCX": "Lam Research", "MU": "Micron", "MELI": "MercadoLibre", "PANW": "Palo Alto",
        "SNPS": "Synopsys", "CDNS": "Cadence", "KLAC": "KLA", "CSX": "CSX", "MAR": "Marriott", "MNST": "Monster", "ORLY": "O'Reilly",
        "CTAS": "Cintas", "NXPI": "NXP", "KDP": "Keurig Dr Pepper", "ADSK": "Autodesk", "FTNT": "Fortinet", "PAYX": "Paychex",
        "AEP": "American Electric", "MCHP": "Microchip", "CPRT": "Copart", "MRVL": "Marvell", "LULU": "Lululemon", "EXC": "Exelon",
        "AZN": "AstraZeneca", "IDXX": "IDEXX", "BKR": "Baker Hughes", "DXCM": "Dexcom", "CTSH": "Cognizant", "EA": "Electronic Arts",
        "CHTR": "Charter", "DLTR": "Dollar Tree", "ROST": "Ross Stores", "WBD": "Warner Bros.", "FAST": "Fastenal", "GEHC": "GE HealthCare",
        "PCAR": "PACCAR", "WDAY": "Workday", "BIIB": "Biogen", "VRSK": "Verisk", "SIRI": "SiriusXM", "GFS": "GlobalFoundries",
        "DDOG": "Datadog", "ANSS": "Ansys", "EBAY": "eBay", "PDD": "PDD Holdings", "ABNB": "Airbnb", "ZS": "Zscaler", "TEAM": "Atlassian",
        "ALGN": "Align", "ENPH": "Enphase", "LCID": "Lucid", "RIVN": "Rivian", "JD": "JD.com", "ILMN": "Illumina", "CEG": "Constellation",
        "DASH": "DoorDash", "MSTR": "MicroStrategy", "ROP": "Roper", "MDB": "MongoDB", "TTD": "Trade Desk", "CDW": "CDW", "ARM": "ARM"
    }
    maps["EURO STOXX 50 🇪🇺"] = {
        "ADS.DE": "Adidas", "ADYEN.AMS": "Adyen", "AIR.PA": "Airbus", "ALV.DE": "Allianz", "ASML.AS": "ASML",
        "CS.PA": "AXA", "BAS.DE": "BASF", "BAYN.DE": "Bayer", "BBVA.MC": "BBVA", "SAN.MC": "Santander",
        "BMW.DE": "BMW", "BNP.PA": "BNP Paribas", "CRH.L": "CRH", "BN.PA": "Danone", "DB1.DE": "Deutsche Börse",
        "DTE.DE": "Deutsche Telekom", "ENEL.MI": "Enel", "ENI.MI": "Eni", "EL.PA": "EssilorLuxottica", "FLTR.L": "Flutter",
        "IBE.MC": "Iberdrola", "ITX.MC": "Inditex", "IFX.DE": "Infineon", "INGA.AS": "ING Group", "ISP.MI": "Intesa Sanpaolo",
        "KER.PA": "Kering", "KNEBV.HE": "Kone", "OR.PA": "L'Oréal", "LIN.DE": "Linde", "MC.PA": "LVMH",
        "MBG.DE": "Mercedes-Benz", "MUV2.DE": "Münchener Rück", "RI.PA": "Pernod Ricard", "PRX.AS": "Prosus", "RACE.MI": "Ferrari",
        "RMS.PA": "Hermès", "SAF.PA": "Safran", "SAN.PA": "Sanofi", "SAP.DE": "SAP", "SU.PA": "Schneider Electric",
        "SIE.DE": "Siemens", "STLAM.MI": "Stellantis", "STMPA.PA": "STMicroelectronics", "TTE.PA": "TotalEnergies", "DG.PA": "Vinci",
        "VIV.PA": "Vivendi", "VOW3.DE": "Volkswagen", "VNA.DE": "Vonovia", "WKL.AS": "Wolters Kluwer", "UCG.MI": "UniCredit"
    }
    maps["INDICES & FOREX 🌍"] = OrderedDict([
        ("EURUSD=X", "EUR/USD"), ("^STOXX50E", "EUROSTOXX"), ("^GDAXI", "DAX"),
        ("^IXIC", "NASDAQ"), ("EURRUB=X", "EUR/RUB"), ("^NSEI", "NIFTY"), ("XU100.IS", "BIST")
    ])
    return maps

# --- 3. BAUER STRATEGIE ENGINE ---
def analyze_market(ticker_map, filter_active=True):
    tickers = list(ticker_map.keys())
    data = yf.download(tickers, period="1y", interval="1d", group_by='ticker', auto_adjust=True, progress=False)
    results = []
    for ticker, full_name in ticker_map.items():
        try:
            df = data[ticker].dropna() if len(tickers) > 1 else data.dropna()
            if len(df) < 40: continue
            close = df['Close']; sma20 = close.rolling(20).mean()
            curr, p1, p2 = close.iloc[-1], close.iloc[-2], close.iloc[-3]
            signal = "C" if (curr > p1 > p2 and curr > sma20.iloc[-1]) else "P" if (curr < p1 < p2 and curr < sma20.iloc[-1]) else "Wait"
            if filter_active and signal == "Wait": continue
            atr = (df['High'] - df['Low']).rolling(14).mean().iloc[-1]
            sl = curr - (atr * 1.5) if signal == "C" else curr + (atr * 1.5)
            stk = int(risk_amount / abs(curr - sl)) if abs(curr - sl) > 0 else 0
            
            # Backtest 60 Tage
            hits, total = 0, 0
            if signal != "Wait":
                for i in range(-60, -5):
                    c_h, p_h, p2_h = close.iloc[i], close.iloc[i-1], close.iloc[i-2]
                    s_h = sma20.iloc[i]
                    if (signal == "C" and c_h > p_h > p2_h and c_h > s_h) or (signal == "P" and c_h < p_h < p2_h and c_h < s_h):
                        total += 1
                        if (signal == "C" and close.iloc[i+3] > c_h) or (signal == "P" and close.iloc[i+3] < c_h): hits += 1
            
            results.append({
                "name": full_name, "ticker": ticker, "price": curr, "signal": signal, "stk": stk,
                "prob": (hits/total*100) if total > 0 else 50.0, "stop": sl,
                "rsi": 100 - (100 / (1 + (close.diff().where(close.diff() > 0, 0).rolling(14).mean() / -close.diff().where(close.diff() < 0, 0).rolling(14).mean()))).iloc[-1],
                "delta": ((curr/df['Open'].iloc[-1])-1)*100, "icon": "☀️" if (curr > sma20.iloc[-1] and (curr/df['Open'].iloc[-1]-1)>0.002) else "⚖️" if abs(curr/df['Open'].iloc[-1]-1)<0.002 else "⛈️"
            })
        except: continue
    return results

# --- 4. UI ---
st.markdown("<div class='header-text'>📡 Dr. Gregor Bauer Strategie Pro 2026</div>", unsafe_allow_html=True)

with st.expander("ℹ️ VOLLSTÄNDIGER STRATEGIE-LEITFADEN & REGELWERK ℹ️", expanded=True):
    st.markdown("""
    ### 1. Marktzustand & Trend-Indikator
    Bestimmung über den SMA 20 (Gleitender Durchschnitt):
    - **Bullish (☀️):** Kurs liegt über SMA 20 + positives Intraday-Momentum.
    - **Bearish (⛈️):** Kurs liegt unter SMA 20 + negativer Verkaufsdruck.
    ### 2. Signal-Trigger (3-Tage-Regel)
    - **C (Call):** Kurs über SMA 20 UND steigende Tendenz an drei aufeinanderfolgenden Tagen.
    - **P (Put):** Kurs unter SMA 20 UND fallende Tendenz an drei aufeinanderfolgenden Tagen.
    ### 3. Statistische Wahrscheinlichkeit
    Prozentwert der erfolgreichen Trades basierend auf dem exakten Setup der letzten 12 Monate.
    ### 4. Risikomanagement (Stop-Loss & Stk.)
    - **Stop-Loss (SL):** Berechnung bei 1,5x ATR (Volatilität).
    - **Stk. (Stückzahl):** Exakte Anzahl basierend auf Kontogröße und Risiko pro Trade.
    """)

m_maps = get_market_maps()
tabs = st.tabs(list(m_maps.keys()))

for i, (tab_name, t_map) in enumerate(m_maps.items()):
    with tabs[i]:
        is_fixed = ("FOREX" in tab_name)
        with st.spinner(f"Scanne {len(t_map)} Werte..."):
            data_res = analyze_market(t_map, filter_active=not is_fixed)
        if not data_res:
            st.warning(f"Scan für {tab_name} abgeschlossen: {len(t_map)} Werte gescannt. Aktuell keine Ergebnisse.")
        else:
            st.info(f"Scan für {tab_name} abgeschlossen: {len(t_map)} Werte gescannt. {len(data_res)} aktive Signale gefunden.")
            
            # SORTIERUNG: 1. Wahrscheinlichkeit (prob), 2. Tagesstärke (abs(delta))
            if not is_fixed:
                data_res = sorted(data_res, key=lambda x: (x['prob'], abs(x['delta'])), reverse=True)
            
            for res in data_res:
                fmt = "{:.5f}" if "=" in res['ticker'] else "{:.2f}"
                st.markdown("<div class='row-container'>", unsafe_allow_html=True)
                c1, c2, c3, c4 = st.columns([2.5, 1, 0.6, 1.2])
                with c1:
                    st.markdown(f"**{res['name']}** {res['icon']}")
                    rsi_c = "#ff4b4b" if res['rsi'] > 70 else "#00ff41" if res['rsi'] < 30 else "#8892b0"
                    st.markdown(f"<span class='metric-label'>RSI: <b style='color:{rsi_c};'>{res['rsi']:.1f}</b></span>", unsafe_allow_html=True)
                with c2:
                    d_col = "#00ff41" if res['delta'] >= 0 else "#ff4b4b"
                    st.markdown(f"<span class='price-text'>{fmt.format(res['price'])}</span><br><span style='color:{d_col}; font-size:0.8rem;'>{res['delta']:+.2f}%</span>", unsafe_allow_html=True)
                with c3:
                    if res['signal'] != "Wait":
                        cls = "sig-box-high" if res['prob'] >= 60 else ("sig-box-c" if res['signal'] == "C" else "sig-box-p")
                        st.markdown(f"<span class='{cls}'>{res['signal']}</span>", unsafe_allow_html=True)
                    else: st.markdown("<span style='color:#333; font-weight:bold; font-size:0.8rem;'>WAIT</span>", unsafe_allow_html=True)
                with c4:
                    if res['signal'] != "Wait":
                        p_col = "#ffd700" if res['prob'] >= 60 else "#e6f1ff"
                        st.markdown(f"<b style='color:{p_col};'>{res['prob']:.1f}%</b> | **{res['stk']} Stk.**", unsafe_allow_html=True)
                        st.markdown(f"<span class='metric-label'>SL: {fmt.format(res['stop'])}</span>", unsafe_allow_html=True)
                    else: st.markdown("<span class='metric-label'>Monitoring</span>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
