import os
import sys
import math

# --- 1. MATPLOTLIB FIX (Backend für Cloud-Stabilität) ---
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt

# --- AUTO-INSTALLER (Fix für Fehlermeldung 2/2) ---
def install_and_import(package):
    try:
        __import__(package.replace('-', '_'))
    except ImportError:
        os.system(f"{sys.executable} -m pip install {package}")

install_and_import('streamlit-autorefresh')
install_and_import('lxml') # Behebt 'Missing dependency lxml'
install_and_import('html5lib')

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
from zoneinfo import ZoneInfo
from concurrent.futures import ThreadPoolExecutor
import base64
import io
from streamlit_autorefresh import st_autorefresh

# --- 2. SETUP & REFRESH (60 Sek) ---
now = datetime.now(ZoneInfo("Europe/Berlin"))
st.write(f"Update: {now.strftime('%H:%M:%S')} | Auto-Refresh: 60s")
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

# --- 3. CORE FUNCTIONS ---
def create_sparkline(data, color):
    fig, ax = plt.subplots(figsize=(2.5, 0.6), dpi=70)
    ax.plot(data.values, color=color, linewidth=2.5)
    ax.axis('off')
    buf = io.BytesIO()
    fig.savefig(buf, format='png', transparent=True, bbox_inches='tight', pad_inches=0)
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode()

@st.cache_data(ttl=300)
def fetch_data(ticker):
    try:
        # --- Daten laden ---
        t_obj = yf.Ticker(ticker)
        df = t_obj.history(period="1y", interval="1d", auto_adjust=True)

        if df.empty or len(df) < 40:
            return None

        # --- Indikatoren vorbereiten ---
        close = df["Close"]
        high = df["High"]
        low = df["Low"]

        # SMA20
        sma20 = close.rolling(20).mean()

        # RSI
        delta = close.diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / (loss + 1e-9)
        rsi = 100 - (100 / (1 + rs))

        # ATR
        tr = pd.concat([
            high - low,
            (high - close.shift()).abs(),
            (low - close.shift()).abs()
        ], axis=1).max(axis=1)
        atr = tr.rolling(14).mean()

        # ADX
        up_move = high.diff()
        down_move = -low.diff()
        plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0)
        minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0)

        atr_smooth = tr.rolling(14).mean()
        plus_di = 100 * (pd.Series(plus_dm).rolling(14).sum() / atr_smooth)
        minus_di = 100 * (pd.Series(minus_dm).rolling(14).sum() / atr_smooth)
        dx = (abs(plus_di - minus_di) / (plus_di + minus_di + 1e-9)) * 100
        adx = dx.rolling(14).mean()

        # --- Aktuelle Werte ---
        curr = float(close.iloc[-1])
        prev = close.iloc[-2]
        prev2 = close.iloc[-3]

        sma_curr = sma20.iloc[-1]
        rsi_curr = rsi.iloc[-1]
        adx_curr = adx.iloc[-1]
        atr_curr = atr.iloc[-1]

        # Tagesveränderung
        daily_delta = ((curr - df["Open"].iloc[-1]) / df["Open"].iloc[-1]) * 100

        # --- Signal berechnen ---
        signal = generate_signal(df)

        # --- Stop-Loss ---
        if signal == "C":
            stop = curr - atr_curr * 1.5
        elif signal == "P":
            stop = curr + atr_curr * 1.5
        else:
            stop = 0

        # --- Sparkline ---
        spark_img = create_sparkline(
            close.tail(20),
            "#3fb950" if curr >= prev else "#007bff"
        )

        # --- Icon ---
        icon = (
            "☀️" if (curr > sma_curr and daily_delta > 0.3)
            else "⚖️" if abs(daily_delta) < 0.3
            else "⛈️"
        )

        # --- Backtest (Top 3) ---
        # Nur wenn Signal existiert
        prob = 50.0
        if signal in ["C", "P"]:
            signals = []
            for i in range(40, len(df)):
                sig = generate_signal(df.iloc[:i])
                if sig in ["C", "P"]:
                    signals.append((i, sig))

            if len(signals) > 0:
                stats = backtest_strategy(df, signals)
                if stats:
                    prob = max(10, min(90, stats["winrate"]))  # stabilisiert UI

        # --- Output ---
        return {
            "name": t_obj.fast_info.get("shortName", ticker),
            "ticker": ticker,
            "price": curr,
            "delta": daily_delta,
            "signal": signal,
            "stop": stop,
            "prob": prob,
            "rsi": rsi_curr,
            "adx": adx_curr,
            "spark": spark_img,
            "icon": icon
        }

    except Exception as e:
        print(f"Fehler bei {ticker}: {e}")
        return None

def render_row(res):
    fmt = "{:.6f}" if "=" in res['ticker'] else "{:.2f}"
    st.markdown("<div class='row-container'>", unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns([1.2, 0.6, 0.8, 0.5, 1.1])
    with c1: st.markdown(f"**{res['name']}**<br><small>{fmt.format(res['price'])}</small>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div style='text-align:center;'>{res['icon']}<br><span style='color:{'#3fb950' if res['delta']>=0 else '#007bff'};'>{res['delta']:+.2f}%</span></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f'<img src="data:image/png;base64,{res["spark"]}" width="100">', unsafe_allow_html=True)
        st.markdown(f"<span class='indicator-label'>RSI: {res['rsi']:.1f} | ADX: {res['adx']:.1f}</span>", unsafe_allow_html=True)
    with c4:
        if res['signal'] != "Wait":
            cls = "sig-box-high" if res['prob'] >= 60 else ("sig-box-c" if res['signal']=="C" else "sig-box-p")
            st.markdown(f"<br><span class='{cls}'>{res['signal']}</span>", unsafe_allow_html=True)
    with c5:
        if res['stop'] != 0:
            st.markdown(f"<small>SL ({res['prob']:.1f}%)</small><br><b>{fmt.format(res['stop'])}</b>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- 4. UI MAIN ---


with st.expander("ℹ️ Ausführlicher Strategie-Leitfaden & Markt-Logik ℹ️", expanded=False):
    st.markdown("""
    ### 📡 System-Logik Pro 2026
    Dieser Monitor analysiert Märkte basierend auf Dr. Gregor Bauers Trend- und Momentum-Strategie.
    """)

# --- 5. MACRO SECTION ---
st.markdown("<div class='header-text'>🌍 Macro + Indices 🌍</div>", unsafe_allow_html=True)
macro_list = ["EURUSD=X", "^GDAXI", "^STOXX50E", "^IXIC", "XU100.IS", "^NSEI"]
with ThreadPoolExecutor(max_workers=10) as ex:
    m_res = [r for r in ex.map(fetch_data, macro_list) if r]
    for r in m_res: render_row(r)

# --- 6. SCREENER (DAX, EuroStoxx, IBEX, NASDAQ, BIST, NIFTY) ---
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
    try:
        if market_choice == "Nasdaq 100":
            df = pd.read_html('https://en.wikipedia.org')[4]
            return sorted(df['Ticker'].unique().tolist())
        elif market_choice == "DAX 40":
            df = pd.read_html('https://en.wikipedia.org')[4]
            return sorted(df['Ticker'].tolist())
        elif market_choice == "IBEX 35":
            df = pd.read_html('https://en.wikipedia.org')[1]
            return [t + ".MC" for t in df['Ticker'].tolist()]
        return fallbacks.get(market_choice, ["AAPL"])
    except:
        return fallbacks.get(market_choice, ["AAPL"])

st.markdown("<br><div class='header-text'>🔭 Markt Screener 🔭</div>", unsafe_allow_html=True)
if 'scan_active' not in st.session_state: st.session_state.scan_active = False

with st.expander("Index-Auswahl & Scan Steuerung", expanded=True):
    choice = st.radio("Markt:", ["DAX 40", "EuroStoxx 50", "IBEX 35", "Nasdaq 100", "BIST 100", "NIFTY 50"], horizontal=True)
    if st.button("🚀 Scan Start/Stop", use_container_width=True):
        st.session_state.scan_active = not st.session_state.scan_active

if st.session_state.scan_active:
    tickers = get_live_tickers(choice)
    tickers = list(dict.fromkeys(tickers)) 
    
    with ThreadPoolExecutor(max_workers=30) as ex:
        results = [r for r in ex.map(fetch_data, tickers) if r]
    
    all_sigs = [r for r in results if r['signal'] in ["C", "P"]]
    sorted_sigs = sorted(all_sigs, key=lambda x: -x['prob'])
    top_3_tickers = [r['ticker'] for r in sorted_sigs[:3]]
    
    # Hauptliste: Nur Signale (C/P) UND Prob >= 45% (außer Top 3)
    hits = [r for r in sorted_sigs if r['prob'] >= 45 or r['ticker'] in top_3_tickers]

    if hits:
        st.info(f"Scan bereit: {len(results)} geprüft. {len(hits)} relevante Signale gefunden.")
        for r in hits: render_row(r)
    else:
        st.warning("Keine relevanten Signale aktuell verfügbar.")

# --- 7. DYNAMISCHES BACKTESTING (Top 3) ---
st.markdown("---")
top_results = []
if st.session_state.scan_active and 'results' in locals() and results:
    valid_hits = [r for r in results if r['signal'] in ["C", "P"]]
    if valid_hits: 
        top_results = sorted(valid_hits, key=lambda x: (-x['prob'], -x['adx']))[:3]

with st.expander(f"📈 Top-Signale Analyse", expanded=True):
    if top_results:
        for i, res in enumerate(top_results):
            sig_class = "sig-box-high" if res["prob"] >= 60 else ("sig-box-c" if res["signal"]=="C" else "sig-box-p")
            
            # Zeile 1: Signal | Name | Preis | SL
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
            
            # Zeile 2: Metriken (Nach links unter den Namen geschoben)
            prob_color = "#ffd700" if res['prob'] >= 60 else "#e0e0e0"
            metrics_html = f"""
            <div style="display: flex; gap: 30px; margin-left: 50px; margin-bottom: 10px; font-family: monospace; font-size: 0.7rem; color: #888;">
                <div>Wahrsch: <span style="color: {prob_color}; font-weight: bold;">{res['prob']:.1f}%</span></div>
                <div>Trend (ADX): <span style="color: #e0e0e0;">{res['adx']:.1f}</span></div>
                <div>Momentum (RSI): <span style="color: #e0e0e0;">{res['rsi']:.1f}</span></div>
            </div>
            """
            st.markdown(metrics_html, unsafe_allow_html=True)
            if i < len(top_results) - 1: st.markdown("<hr style='margin: 5px 0; border: 0; border-top: 1px solid #333; opacity: 0.2;'>", unsafe_allow_html=True)
    else:
        st.info("Warte auf Signale...")






