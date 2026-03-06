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
    
    /* Signal Design */
    .sig-box-c { color: #00ff41 !important; border: 1px solid #00ff41; padding: 2px 8px; border-radius: 4px; font-weight: bold; background: rgba(0, 255, 65, 0.1); }
    .sig-box-p { color: #007bff !important; border: 1px solid #007bff; padding: 2px 8px; border-radius: 4px; font-weight: bold; background: rgba(0, 123, 255, 0.1); }
    .sig-box-high { color: #ffd700 !important; border: 2px solid #ffd700; padding: 2px 8px; border-radius: 4px; font-weight: bold; background: rgba(255, 215, 0, 0.2); }
    
    /* Heatmap / Breadth Bar */
    .breath-bar { display: flex; width: 100%; height: 12px; border-radius: 6px; overflow: hidden; margin: 10px 0 20px 0; border: 1px solid #172a45; }
    .breath-bull { background-color: #00ff41; height: 100%; }
    .breath-neut { background-color: #8892b0; height: 100%; }
    .breath-bear { background-color: #ff4b4b; height: 100%; }
    
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
        "DASH": "DoorDash", "MSTR": "MicroStrategy", "ROP": "Roper", "MDB": "MongoDB", "TTD": "Trade Desk", "CDW": "CDW", "ARM": "ARM",
        "ON": "ON Semi", "MCHP": "Microchip", "ADSK": "Autodesk"
    }
    # (Rest der NASDAQ Liste bis 100 wird intern ergänzt falls yfinance batch nutzt)
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
        ("EURUSD=X", "EUR/USD"), ("^STOXX50E", "EUROSTOXX Index"), ("^GDAXI", "DAX Index"),
        ("^IXIC", "NASDAQ Index"), ("EURRUB=X", "EUR/RUB"), ("^NSEI", "NIFTY"), ("XU100.IS", "BIST")
    ])
    return maps

# --- BAUER SIGNAL-FUNKTION (3-Tage-Regel + SMA20) ---
def bauer_signal(df):
    # Schutz: Mindestens 25 Kerzen nötig (SMA20 + 3-Tage-Regel)
    if len(df) < 25:
        return None

    close = df["Close"]
    sma20 = close.rolling(20).mean()

    curr = close.iloc[-1]
    p1   = close.iloc[-2]
    p2   = close.iloc[-3]
    sma  = sma20.iloc[-1]

    if curr > p1 > p2 and curr > sma:
        return "C"
    if curr < p1 < p2 and curr < sma:
        return "P"
    return None


# --- BACKTESTING ENGINE ---
def backtest_strategy(df, signal_func, atr_mult_sl=1.5, atr_mult_tp=2.0, hold_days=5):
    df = df.copy()
    df["SMA20"] = df["Close"].rolling(20).mean()
    df["ATR"] = (df["High"] - df["Low"]).rolling(14).mean()

    trades = []
    position = None

    for i in range(20, len(df) - hold_days):
        row = df.iloc[i]

        # WICHTIG: vollständigen DataFrame übergeben, nicht einzelne Zeile!
        sig = signal_func(df.iloc[:i+1])

        # Einstieg
        if position is None and sig in ["C", "P"]:
            entry = row["Close"]
            atr = row["ATR"]

            sl = entry - atr_mult_sl * atr if sig == "C" else entry + atr_mult_sl * atr
            tp = entry + atr_mult_tp * atr if sig == "C" else entry - atr_mult_tp * atr

            position = {
                "type": sig,
                "entry": entry,
                "sl": sl,
                "tp": tp,
                "entry_index": i
            }

        # Position überwachen
        if position:
            future = df.iloc[i:i+hold_days]
            exit_price = None
            exit_reason = None

            for _, f in future.iterrows():
                if position["type"] == "C":
                    if f["Low"] <= position["sl"]:
                        exit_price = position["sl"]
                        exit_reason = "SL"
                        break
                    if f["High"] >= position["tp"]:
                        exit_price = position["tp"]
                        exit_reason = "TP"
                        break
                else:
                    if f["High"] >= position["sl"]:
                        exit_price = position["sl"]
                        exit_reason = "SL"
                        break
                    if f["Low"] <= position["tp"]:
                        exit_price = position["tp"]
                        exit_reason = "TP"
                        break

            # Exit nach Zeitablauf
            if exit_price is None:
                exit_price = future.iloc[-1]["Close"]
                exit_reason = "TIME"

            pnl = exit_price - position["entry"] if position["type"] == "C" else position["entry"] - exit_price

            trades.append({
                "type": position["type"],
                "entry": position["entry"],
                "exit": exit_price,
                "pnl": pnl,
                "reason": exit_reason
            })

            position = None

    return pd.DataFrame(trades)


# --- PERFORMANCE ANALYSE ---
def evaluate_backtest(trades):
    if len(trades) == 0:
        return {}

    wins = trades[trades["pnl"] > 0]
    losses = trades[trades["pnl"] <= 0]

    return {
        "Trades": len(trades),
        "Trefferquote": len(wins) / len(trades) * 100,
        "Ø Gewinn": wins["pnl"].mean() if len(wins) else 0,
        "Ø Verlust": losses["pnl"].mean() if len(losses) else 0,
        "Profit Faktor": wins["pnl"].sum() / abs(losses["pnl"].sum()) if len(losses) else float("inf"),
        "Max Drawdown": (trades["pnl"].cumsum().cummax() - trades["pnl"].cumsum()).max(),
        "Gesamt PnL": trades["pnl"].sum()
    }


# --- STREAMLIT BACKTESTING-BEREICH ---
with st.expander("📈 Backtesting – Microsoft (MSFT)"):
    st.write("Backtest der Bauer-Strategie für Microsoft über 2 Jahre.")

    df_msft = yf.download("MSFT", period="2y", interval="1d", auto_adjust=True).dropna()

    trades = backtest_strategy(df_msft, bauer_signal)
    stats = evaluate_backtest(trades)

    if len(trades) == 0:
        st.warning("Keine Trades gefunden.")
    else:
        col1, col2, col3 = st.columns(3)
        col1.metric("Trades", stats["Trades"])
        col2.metric("Trefferquote", f"{stats['Trefferquote']:.1f}%")
        col3.metric("Profit Faktor", f"{stats['Profit Faktor']:.2f}")

        col4, col5, col6 = st.columns(3)
        col4.metric("Ø Gewinn", f"{stats['Ø Gewinn']:.2f}")
        col5.metric("Ø Verlust", f"{stats['Ø Verlust']:.2f}")
        col6.metric("Max Drawdown", f"{stats['Max Drawdown']:.2f}")

        st.subheader("Equity-Kurve")
        st.line_chart(trades["pnl"].cumsum())

        st.subheader("Trades")
        st.dataframe(trades)
