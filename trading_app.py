import os
import sys

# --- AUTO-INSTALLER ---
def install_and_import(package):
    try:
        __import__(package.replace('-', '_'))
    except ImportError:
        os.system(f"{sys.executable} -m pip install {package}")

install_and_import('streamlit-autorefresh')
install_and_import('lxml')
install_and_import('html5lib')

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# --- SETUP & REFRESH ---
st_autorefresh(interval=60000, key="datarefresh")
st.set_page_config(layout="wide", page_title="Strategy", page_icon="📡")

# --- STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #050a0f; }
    h1, h2, h3, p, span, label, div { color: #e0e0e0 !important; font-family: 'Courier New', Courier, monospace; }
    .header-text { font-size: 24px; font-weight: bold; margin-bottom: 5px; display: flex; align-items: center; gap: 10px; }
    .sig-box-p { color: #007bff !important; border: 1px solid #007bff !important; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
    .sig-box-c { color: #3fb950 !important; border: 1px solid #3fb950 !important; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
    .sig-box-high { color: #ffd700 !important; border: 1px solid #ffd700 !important; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
    .indicator-label { color: #888; font-size: 0.75rem; margin-top: 2px; }
    .row-container { border-bottom: 1px solid #1a202c; padding: 12px 0; width: 100%; }
    .scan-info { color: #ffd700; font-style: italic; font-size: 0.9rem; margin-bottom: 10px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- CORE FUNCTIONS ---

def sparkline_svg(series, color="#3fb950"):
    values = list(series.values)
    if len(values) < 2:
        return ""
    min_v, max_v = min(values), max(values)
    span = max_v - min_v if max_v != min_v else 1.0
    norm = [(v - min_v) / span for v in values]
    points = " ".join(f"{i},{1 - v}" for i, v in enumerate(norm))
    width = max(len(values) - 1, 1)
    svg = f"""
    <svg width="120" height="30" viewBox="0 0 {width} 1" xmlns="http://www.w3.org/2000/svg">
        <polyline fill="none" stroke="{color}" stroke-width="0.08" points="{points}" />
    </svg>
    """
    return svg

@st.cache_data(ttl=300)
def fetch_batch_data(tickers):
    if isinstance(tickers, str):
        tickers = [tickers]
    try:
        data = yf.download(
            tickers=tickers,
            period="1y",
            interval="1d",
            auto_adjust=True,
            group_by='ticker',
            threads=True
        )
    except Exception:
        return {}
    result = {}
    if isinstance(data.columns, pd.MultiIndex):
        for t in tickers:
            try:
                if t in data.columns.get_level_values(0):
                    df_t = data.xs(t, axis=1, level=0).dropna()
                    if not df_t.empty:
                        result[t] = df_t
            except Exception:
                continue
    else:
        df_t = data.dropna()
        if not df_t.empty and len(tickers) == 1:
            result[tickers[0]] = df_t
    return result

@st.cache_data(ttl=3600)
def get_name_for_ticker(ticker):
    try:
        t_obj = yf.Ticker(ticker)
        name = t_obj.info.get('shortName') or ticker
        return name
    except Exception:
        return ticker

# --- MONTE-CARLO / REGIME-LOGIK (nur für Top-Signale) ---

def hurst_exponent(ts):
    lags = range(2, 20)
    tau = [np.sqrt(np.std(np.subtract(ts[lag:], ts[:-lag]))) for lag in lags]
    poly = np.polyfit(np.log(lags), np.log(tau), 1)
    return poly[0] * 2.0

def detect_regimes(df):
    df = df.copy()
    df["ret"] = df["Close"].pct_change()
    df["atr"] = (df["High"] - df["Low"]).rolling(14).mean()

    hurst = hurst_exponent(df["Close"].dropna())

    if hurst > 0.55:
        regime = "trend"
    elif hurst < 0.45:
        regime = "meanrev"
    else:
        regime = "neutral"

    if df["ret"].rolling(5).sum().iloc[-1] < -0.05:
        regime = "crash"

    if df["atr"].iloc[-1] > df["atr"].rolling(200).mean().iloc[-1] * 1.5:
        regime = "volcluster"

    return regime

def bootstrap_market(df, block_size=20, length=252):
    prices = df["Close"].values
    n = len(prices)
    if n <= block_size:
        return prices
    blocks = []
    while len(blocks) * block_size < length:
        start = np.random.randint(0, n - block_size)
        block = prices[start:start + block_size]
        blocks.append(block)
    synthetic = np.concatenate(blocks)[:length]
    return synthetic

def simulate_strategy_on_path(prices):
    df = pd.DataFrame({"Close": prices})
    df["prev"] = df["Close"].shift(1)
    df["prev2"] = df["Close"].shift(2)
    df["sma20"] = df["Close"].rolling(20).mean()

    df["signal_C"] = (df["Close"] > df["prev"]) & (df["prev"] > df["prev2"]) & (df["Close"] > df["sma20"])
    df["signal_P"] = (df["Close"] < df["prev"]) & (df["prev"] < df["prev2"]) & (df["Close"] < df["sma20"])

    df["ret"] = df["Close"].pct_change()

    long_ret = df["ret"].where(df["signal_C"], 0)
    short_ret = -df["ret"].where(df["signal_P"], 0)

    equity = (1 + long_ret + short_ret).cumprod()
    return equity

def monte_carlo_regime_simulation(df, sims=500, block_size=20, length=252):
    regime = detect_regimes(df)
    results = []
    max_dds = []

    for _ in range(sims):
        synthetic = bootstrap_market(df, block_size=block_size, length=length)
        equity = simulate_strategy_on_path(synthetic)
        results.append(equity.iloc[-1])
        dd = (equity / equity.cummax() - 1).min()
        max_dds.append(dd)

    results = np.array(results)
    max_dds = np.array(max_dds)

    return {
        "regime": regime,
        "median_equity": float(np.median(results)),
        "worst_equity": float(np.min(results)),
        "best_equity": float(np.max(results)),
        "VaR_5": float(np.percentile(results, 5)),
        "maxdd_median": float(np.median(max_dds)),
        "maxdd_worst": float(np.min(max_dds)),
        "survival_prob": float(np.mean(results > 0.8)),
    }

def compute_signal_from_df(ticker, df):
    try:
        if df is None or df.empty or len(df) < 35:
            return None

        delta_p = df['Close'].diff()
        gain = delta_p.where(delta_p > 0, 0).rolling(window=14).mean()
        loss = (-delta_p.where(delta_p < 0, 0)).rolling(window=14).mean()
        rs = gain / (loss + 1e-9)
        rsi = 100 - (100 / (1 + rs))

        tr = pd.concat([
            df['High'] - df['Low'],
            (df['High'] - df['Close'].shift()).abs(),
            (df['Low'] - df['Close'].shift()).abs()
        ], axis=1).max(axis=1)
        atr = tr.rolling(window=14).mean().iloc[-1]
        adx = ((df['High'].diff().abs() - df['Low'].diff().abs()).abs() / (tr + 1e-9)).rolling(window=14).mean().iloc[-1] * 100

        curr = float(df['Close'].iloc[-1])
        prev, prev2 = df['Close'].iloc[-2], df['Close'].iloc[-3]
        sma20 = df['Close'].rolling(window=20).mean().iloc[-1]
        daily_delta = ((curr - df['Open'].iloc[-1]) / df['Open'].iloc[-1]) * 100

        if curr > prev > prev2 and curr > sma20:
            signal = "C"
        elif curr < prev < prev2 and curr < sma20:
            signal = "P"
        else:
            signal = "Wait"

        bt_df = df.tail(100).copy()
        bt_df['SMA20'] = bt_df['Close'].rolling(window=20).mean()
        hits, sigs = 0, 0
        for i in range(20, len(bt_df) - 3):
            c_h, p_h, p2_h = bt_df['Close'].iloc[i], bt_df['Close'].iloc[i-1], bt_df['Close'].iloc[i-2]
            if signal == "C" and (c_h > p_h > p2_h and c_h > bt_df['SMA20'].iloc[i]):
                sigs += 1
                if bt_df['Close'].iloc[i+3] > c_h:
                    hits += 1
            elif signal == "P" and (c_h < p_h < p2_h and c_h < bt_df['SMA20'].iloc[i]):
                sigs += 1
                if bt_df['Close'].iloc[i+3] < c_h:
                    hits += 1
        prob = (hits / sigs * 100) if sigs > 0 else 50.0

        spark = sparkline_svg(
            df['Close'].tail(20),
            "#3fb950" if curr >= df['Close'].iloc[-2] else "#007bff"
        )
        icon = "☀️" if (curr > sma20 and daily_delta > 0.3) else "⚖️" if abs(daily_delta) < 0.3 else "⛈️"

        name = get_name_for_ticker(ticker)

        return {
            "name": name,
            "ticker": ticker,
            "price": curr,
            "delta": daily_delta,
            "signal": signal,
            "stop": curr - (atr * 1.5) if signal == "C" else curr + (atr * 1.5) if signal == "P" else 0,
            "prob": prob,
            "rsi": rsi.iloc[-1],
            "adx": adx,
            "spark": spark,
            "icon": icon
        }
    except Exception:
        return None

def render_row(res):
    fmt = "{:.6f}" if "=" in res['ticker'] else "{:.2f}"
    st.markdown("<div class='row-container'>", unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns([1.2, 0.6, 0.8, 0.5, 1.1])
    with c1:
        st.markdown(
            f"**{res['name']}**<br><small>{fmt.format(res['price'])}</small>",
            unsafe_allow_html=True
        )
    with c2:
        st.markdown(
            f"<div style='text-align:center;'>{res['icon']}<br>"
            f"<span style='color:{'#3fb950' if res['delta']>=0 else '#007bff'};'>{res['delta']:+.2f}%</span></div>",
            unsafe_allow_html=True
        )
    with c3:
        st.markdown(res["spark"], unsafe_allow_html=True)
        st.markdown(
            f"<span class='indicator-label'>RSI: {res['rsi']:.1f} | ADX: {res['adx']:.1f}</span>",
            unsafe_allow_html=True
        )
    with c4:
        if res['signal'] != "Wait":
            cls = "sig-box-high" if res['prob'] >= 60 else ("sig-box-c" if res['signal'] == "C" else "sig-box-p")
            st.markdown(f"<br><span class='{cls}'>{res['signal']}</span>", unsafe_allow_html=True)
    with c5:
        if res['stop'] != 0:
            st.markdown(
                f"<small>SL ({res['prob']:.1f}%)</small><br><b>{fmt.format(res['stop'])}</b>",
                unsafe_allow_html=True
            )
    st.markdown("</div>", unsafe_allow_html=True)

# --- UI MAIN ---

st.markdown("<div class='header-text'>📡 Momentum Strategie 📡</div>", unsafe_allow_html=True)
st.write(f"Update: {datetime.now().strftime('%H:%M:%S')} | Auto-Refresh: 60s")

with st.expander("📘 Ausführlicher Strategie‑Leitfaden & Markt‑Logik 📘", expanded=False):
    st.markdown("""
    ## 🧭 Überblick des Momentum‑Monitors 🧭

    Der Momentum‑Monitor ist ein professionelles Analyse‑Dashboard, das Aktien‑ und Marktbewegungen in Echtzeit bewertet. 
    Er kombiniert technische Analyse, Trend‑Erkennung, statistische Risiko‑Modelle und visuelle Darstellung in einem 
    einzigen, leistungsstarken System. Die Architektur ist so optimiert, dass sie schnell, stabil, übersichtlich und 
    wissenschaftlich fundiert arbeitet.

    ---

    ## 🎯 Ziel des Systems 🎯
    Der Monitor wurde entwickelt, um:
    - Markttrends frühzeitig zu erkennen  
    - Momentum‑Signale (Long/Short) zu identifizieren  
    - Trendstärke und Marktqualität zu bewerten  
    - Risiko und Drawdown‑Gefahr einzuschätzen  
    - die besten Chancen pro Markt herauszufiltern  
    - synthetische Zukunftsszenarien zu simulieren (Monte‑Carlo)  

      Er eignet sich für Trader, quantitative Analysten,
      Portfolio‑Manager und systematische Strategien.
    ---
    ## ⚙️ Technische Basis ⚙️
    Das Dashboard nutzt moderne Technologien:
    - **Streamlit** für UI, Layout und Auto‑Refresh  
    - **yfinance (Batch‑Download)** für schnelle Kursdaten  
    - **SVG‑Sparklines** für extrem schnelle Mini‑Charts  
    - **Caching** für minimale Ladezeiten  
    - **NumPy / Pandas** für technische Indikatoren  
    - **Monte‑Carlo‑Simulation** für Risiko‑Analyse  

    ---

    ## 🌍 Macro + Indices 🌍
    Dieser Bereich zeigt die wichtigsten Märkte:
    . EUR/USD  
    . DAX, EuroStoxx, Nasdaq  
    - BIST  
    - NIFTY  

    Für jeden Index werden angezeigt:
    - aktueller Preis  
    - Tagesveränderung  
    - Sparkline (20‑Tage‑Verlauf)  
    - RSI & ADX  
    - Momentum‑Signal (C/P/Wait)  
    - Stop‑Loss  
    - Trend‑Icon (☀️ ⚖️ ⛈️)

    Dieser Abschnitt dient als Marktüberblick, um bullische, neutrale oder riskante Marktphasen zu erkennen.

    ---

    ## 🔭 Markt‑Screener 🔭
    Der Nutzer wählt einen Markt (z. B. DAX, Nasdaq, NIFTY).  
    Der Screener:
    - lädt alle Aktien des Index in einem einzigen Batch  
    - berechnet Momentum‑Signale  
    - filtert die besten Chancen  
    - zeigt nur relevante Treffer an  

    Angezeigt werden:
    - Name  
    - Preis  
    - Tagesveränderung  
    - Sparkline  
    - RSI / ADX  
    - Signal (C/P/Wait)  
    - Stop‑Loss  
    - Trend‑Icon  

    Der Screener ist extrem schnell, da:
    - keine Monte‑Carlo‑Simulationen ausgeführt werden  
    - SVG statt PNG genutzt wird  
    - Batch‑Daten geladen werden  
    - Caching aktiv ist  

    ---

    ## ⭐ Top‑Signale Analyse ⭐
    Die besten 3 Signale des gesamten Scans werden ausgewählt – basierend auf:
    - Signalqualität  
    - Wahrscheinlichkeit  
    - Trendstärke (ADX)  

    Für diese Top‑Signale wird zusätzlich eine **Monte‑Carlo‑Simulation** durchgeführt.

    ---

    ## 🎲 Monte‑Carlo Risikoanalyse 🎲
    Die Monte‑Carlo‑Simulation erzeugt synthetische Marktverläufe und testet die Strategie unter:
    - Trend‑Phasen  
    - Mean‑Reversion  
    - Crash‑Phasen  
    - Volatilitäts‑Clustern  

    Angezeigt werden:
    - Marktregime  
    - Median‑Ergebnis  
    - Worst‑Case‑Ergebnis  
    - Value‑at‑Risk (5%)  
    - Median‑Drawdown  
    - Worst‑Drawdown  
    - Überlebenswahrscheinlichkeit  

    Diese Analyse zeigt:
    - wie robust ein Signal wirklich ist  
    - wie schlimm der Worst‑Case werden kann  
    - wie hoch die Chance auf langfristigen Erfolg ist  
    """)


# --- MACRO SECTION ---

st.markdown("<div class='header-text'>🌍 Macro + Indices 🌍</div>", unsafe_allow_html=True)
macro_list = ["EURUSD=X", "^GDAXI", "^STOXX50E", "^IXIC", "XU100.IS", "^NSEI"]

macro_data = fetch_batch_data(macro_list)
m_res = []
for t in macro_list:
    # Einzelabfrage pro Ticker mit kurzem Cache
    @st.cache_data(ttl=300, show_spinner=False)
    def fetch_single_ticker(ticker):
        try:
            return yf.download(ticker, period="1y", interval="1d", auto_adjust=True, threads=False, timeout=5)
        except:
            return None

    df_t = fetch_single_ticker(t)
    
    if df_t is not None and not df_t.empty:
        res = compute_signal_from_df(t, df_t)
        if res:
            render_row(res)
    else:
        # Platzhalter, damit das Layout nicht springt, falls ein Ticker klemmt
        st.markdown(f"<small style='color: #444;'>⌛ Lade {t}...</small>", unsafe_allow_html=True)

# --- SCREENER ---

@st.cache_data(ttl=86400)
def get_live_tickers(market_choice):
    fallbacks = {
        "DAX 40": ["ADS.DE", "AIR.DE", "ALV.DE", "BAS.DE", "BAYN.DE", "BMW.DE", "CON.DE", "1COV.DE", "DTG.DE", "DTE.DE", "DBK.DE", "DB1.DE", "DHL.DE", "EON.DE", "FRE.DE", "FME.DE", "HEI.DE", "HEN3.DE", "IFX.DE", "MBG.DE", "MRK.DE", "MTX.DE", "MUV2.DE", "PUM.DE", "PAH3.DE", "RWE.DE", "SAP.DE", "SIE.DE", "SHL.DE", "SY1.DE", "TKA.DE", "VOW3.DE", "VNA.DE", "ZAL.DE", "BEI.DE", "CBK.DE", "RHM.DE", "SRT3.DE", "ENR.DE", "QIA.DE"],
        "EuroStoxx 50": ["ASML.AS", "MC.PA", "OR.PA", "SAP.DE", "TTE.PA", "SIE.DE", "AIR.PA", "SAN.MC", "ITX.MC", "CS.PA", "BNP.PA", "IBE.MC", "SU.PA", "ADYEN.AS", "EL.PA", "BAS.DE", "RMS.PA", "ABI.BR", "ENI.MI", "BBVA.MC", "SAF.PA", "KER.PA", "MBG.DE", "BMW.DE", "CRH.IE", "VIV.PA", "AD.AS", "BN.PA", "DTE.DE", "BAYN.DE", "ISP.MI", "MUV2.DE", "ENEL.MI", "ALV.DE", "SAN.PA", "IFX.DE", "AI.PA", "DG.PA", "VOW3.DE", "STLAM.MI"],
        "IBEX 35": ["ANA.MC", "ACX.MC", "ACS.MC", "AENA.MC", "AMS.MC", "MTS.MC", "SAB.MC", "SAN.MC", "BKT.MC", "BBVA.MC", "CABK.MC", "CLNX.MC", "COL.MC", "ENG.MC", "ELE.MC", "FER.MC", "FDR.MC", "GRF.MC", "IAG.MC", "IBE.MC", "IDR.MC", "ITX.MC", "LOG.MC", "MAP.MC", "MEL.MC", "MRL.MC", "NTGY.MC", "PUIG.MC", "RED.MC", "REP.MC", "ROVI.MC", "SCYR.MC", "SLR.MC", "TEF.MC", "UNI.MC"],
        "Nasdaq 100": ["AAPL", "MSFT", "NVDA", "AMZN", "TSLA", "GOOGL", "META", "AVGO", "COST", "NFLX", "ADBE", "AMD", "PEP", "INTC", "CSCO", "TMUS", "TXN", "QCOM", "AMAT", "ISRG", "AMGN", "HON", "SBUX", "BKNG", "GILD", "INTU", "MDLZ", "VRTX", "ADI", "REGN", "PYPL", "PANW", "SNPS", "LRCX", "KLAC", "CDNS", "MELI", "CSX", "MAR", "ORLY", "CTAS", "ROP", "NXPI", "MNST", "KDP", "ADSK", "TEAM", "LULU", "AEP", "BKR", "CPRT", "DXCM", "EXC", "FAST", "FTNT", "KHC", "MCHP", "ODFL", "PAYX", "PCAR", "PDD", "WDAY", "XEL", "ZS", "ABNB", "ANSS", "ASML", "AZN", "BIIB", "CEG", "CHTR", "DDOG", "DLTR", "FANG", "GEHC", "IDXX", "ILMN", "LCID", "MDB", "MRVL", "ON", "ROST", "SIRI", "VRSK", "WBD", "CTSH", "CDW", "WBA", "ALGN", "EBAY", "ENPH", "JD"],
        "BIST 100": ["AEFES.IS", "AGHOL.IS", "AKBNK.IS", "AKCNS.IS", "AKSA.IS", "AKSEN.IS", "ALARK.IS", "ALBRK.IS", "ALFAS.IS", "ARCLK.IS", "ASELS.IS", "ASTOR.IS", "ASUZU.IS", "AYDEM.IS", "BAGFS.IS", "BERA.IS", "BIENP.IS", "BIMAS.IS", "BRMEN.IS", "BRSAN.IS", "BRYAT.IS", "BUCIM.IS", "CANTE.IS", "CCOLA.IS", "CIMSA.IS", "CWENE.IS", "DOAS.IS", "DOHOL.IS", "EGEEN.IS", "EKGYO.IS", "ENJSA.IS", "ENKAI.IS", "EREGL.IS", "EUPWR.IS", "FROTO.IS", "GARAN.IS", "GENIL.IS", "GESAN.IS", "GUBRF.IS", "GWIND.IS", "HALKB.IS", "HEKTS.IS", "IPEKE.IS", "ISCTR.IS", "ISDMR.IS", "ISGYO.IS", "ISMEN.IS", "IZMDC.IS", "KARDM.IS", "KAYSE.IS", "KCHOL.IS", "KENT.IS", "KONTR.IS", "KORDS.IS", "KOZAA.IS", "KOZAL.IS", "KRDMD.IS", "MAVI.IS", "MGROS.IS", "MIATK.IS", "ODAS.IS", "OTKAR.IS", "OYAKC.IS", "PENTA.IS", "PETKM.IS", "PGSUS.IS", "QUAGR.IS", "SAHOL.IS", "SASA.IS", "SAYAS.IS", "SDTTR.IS", "SISE.IS", "SKBNK.IS", "SMRTG.IS", "SOKM.IS", "TARKN.IS", "TAVHL.IS", "TCELL.IS", "THYAO.IS", "TKFEN.IS", "TKNSA.IS", "TMSN.IS", "TOASO.IS", "TSKB.IS", "TTKOM.IS", "TTRAK.IS", "TUPRS.IS", "TURSG.IS", "ULKER.IS", "VAKBN.IS", "VESBE.IS", "VESTL.IS", "YEOTK.IS", "YKBNK.IS", "YYLGD.IS", "ZOREN.IS"],
        "NIFTY 50": ["ADANIENT.NS", "ADANIPORTS.NS", "APOLLOHOSP.NS", "ASIANPAINT.NS", "AXISBANK.NS", "BAJAJ-AUTO.NS", "BAJFINANCE.NS", "BAJAJFINSV.NS", "BPCL.NS", "BHARTIARTL.NS", "BRITANNIA.NS", "CIPLA.NS", "COALINDIA.NS", "DIVISLAB.NS", "DRREDDY.NS", "EICHERMOT.NS", "GRASIM.NS", "HCLTECH.NS", "HDFCBANK.NS", "HDFCLIFE.NS", "HEROMOTOCO.NS", "HINDALCO.NS", "HINDUNILVR.NS", "ICICIBANK.NS", "ITC.NS", "INDUSINDBK.NS", "INFY.NS", "JSWSTEEL.NS", "KOTAKBANK.NS", "LT.NS", "LTIM.NS", "M&M.NS", "MARUTI.NS", "NESTLEIND.NS", "NTPC.NS", "ONGC.NS", "POWERGRID.NS", "RELIANCE.NS", "SBILIFE.NS", "SBIN.NS", "SUNPHARMA.NS", "TCS.NS", "TATACONSUM.NS", "TATAMOTORS.NS", "TATASTEEL.NS", "TECHM.NS", "TITAN.NS", "ULTRACEMCO.NS", "UPL.NS", "WIPRO.NS"]
    }
    return fallbacks.get(market_choice, ["AAPL"])

st.markdown("<br><div class='header-text'>🔭 Markt Screener 🔭</div>", unsafe_allow_html=True)
if 'scan_active' not in st.session_state:
    st.session_state.scan_active = False

with st.expander("Index-Auswahl & Scan Steuerung", expanded=True):
    choice = st.radio("Markt:", ["DAX 40", "EuroStoxx 50", "IBEX 35", "Nasdaq 100", "BIST 100", "NIFTY 50"], horizontal=True)
    if st.button("🚀 Scan Start/Stop", use_container_width=True):
        st.session_state.scan_active = not st.session_state.scan_active

results = []

if st.session_state.scan_active:
    tickers = list(dict.fromkeys(get_live_tickers(choice)))
    batch = fetch_batch_data(tickers)

    for t in tickers:
        df_t = batch.get(t)
        if df_t is None:
            continue
        res = compute_signal_from_df(t, df_t)
        if res:
            results.append(res)

    all_sigs = [r for r in results if r['signal'] in ["C", "P"]]
    sorted_sigs = sorted(all_sigs, key=lambda x: -x['prob'])
    top_3_tickers = [r['ticker'] for r in sorted_sigs[:3]]

    hits = [r for r in sorted_sigs if r['prob'] >= 45 or r['ticker'] in top_3_tickers]

    if hits:
        st.info(f"Scan bereit: {len(results)} geprüft. {len(hits)} relevante Signale gefunden.")
        for r in hits:
            render_row(r)
    else:
        st.warning("Keine relevanten Signale aktuell verfügbar.")

# --- TOP-SIGNALE + MONTE-CARLO ---

st.markdown("---")
top_results = []
if st.session_state.scan_active and results:
    valid_hits = [r for r in results if r['signal'] in ["C", "P"]]
    if valid_hits:
        top_results = sorted(valid_hits, key=lambda x: (-x['prob'], -x['adx']))[:3]

with st.expander("📈 Top-Signale Analyse", expanded=True):
    if top_results:
        for i, res in enumerate(top_results):
            sig_class = "sig-box-high" if res["prob"] >= 60 else ("sig-box-c" if res["signal"] == "C" else "sig-box-p")

            html_line = f"""
            <div style="display: flex; align-items: center; justify-content: space-between; width: 100%; margin-top: 10px;">
                <div class="{sig_class}" style="flex: 0 0 35px; text-align: center; font-size: 0.85rem; padding: 2px;">{res['signal']}</div>
                <div style="flex: 1; font-size: 0.85rem; color: #eee; padding: 0 15px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{res['name']}</div>
                <div style="flex: 0 0 180px; text-align: right; white-space: nowrap;">
                    <span style="font-size: 1.4rem; font-weight: bold; color: #fff;">{res['price']:.2f}</span>
                    <span style="font-size: 0.85rem; color: #ff4b4b; margin-left: 10px;">SL ({res['stop']:.2f})</span>
                </div>
            </div>
            """
            st.markdown(html_line, unsafe_allow_html=True)

            prob_color = "#ffd700" if res['prob'] >= 60 else "#e0e0e0"
            metrics_html = f"""
            <div style="display: flex; gap: 30px; margin-left: 50px; margin-bottom: 6px; font-family: monospace; font-size: 0.7rem; color: #888;">
                <div>Wahrsch: <span style="color: {prob_color}; font-weight: bold;">{res['prob']:.1f}%</span></div>
                <div>Trend (ADX): <span style="color: #e0e0e0;">{res['adx']:.1f}</span></div>
                <div>Momentum (RSI): <span style="color: #e0e0e0;">{res['rsi']:.1f}</span></div>
            </div>
            """
            st.markdown(metrics_html, unsafe_allow_html=True)

            # Monte-Carlo nur hier, on-demand
            with st.spinner(f"Monte-Carlo für {res['ticker']}..."):
                df_mc_map = fetch_batch_data(res['ticker'])
                df_mc = df_mc_map.get(res['ticker'])
                mc = monte_carlo_regime_simulation(df_mc) if df_mc is not None else None

            if mc:
                mc_html = f"""
                <div style="margin-left: 50px; margin-bottom: 10px; font-family: monospace; font-size: 0.7rem; color: #aaa;">
                    <div>Regime: <span style="color:#ffd700;">{mc['regime']}</span></div>
                    <div>Median Equity: <span style="color:#e0e0e0;">{mc['median_equity']:.2f}</span></div>
                    <div>Worst Equity: <span style="color:#ff4b4b;">{mc['worst_equity']:.2f}</span></div>
                    <div>VaR 5%: <span style="color:#ff9f43;">{mc['VaR_5']:.2f}</span></div>
                    <div>Median MaxDD: <span style="color:#e0e0e0;">{mc['maxdd_median']*100:.1f}%</span></div>
                    <div>Worst MaxDD: <span style="color:#ff4b4b;">{mc['maxdd_worst']*100:.1f}%</span></div>
                    <div>Survival: <span style="color:#3fb950;">{mc['survival_prob']*100:.1f}%</span></div>
                </div>
                """
                st.markdown(mc_html, unsafe_allow_html=True)

            if i < len(top_results) - 1:
                st.markdown(
                    "<hr style='margin: 5px 0; border: 0; border-top: 1px solid #333; opacity: 0.2;'>",
                    unsafe_allow_html=True
                )
    else:
        st.info("Warte auf Signale...")





