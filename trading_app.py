import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

# --- 0. CONFIG & DARK BLUE STYLE ---
st.set_page_config(layout="wide", page_title="Bauer Strategy Pro 2026", page_icon="📡")

st.markdown("""
    <style>
    .stApp { background-color: #0a192f; }
    h1, h2, h3, p, span, label, div { color: #e6f1ff !important; font-family: 'Segoe UI', sans-serif; }
    .header-text { font-size: 28px; font-weight: bold; color: #64ffda !important; border-bottom: 2px solid #64ffda; padding-bottom: 10px; margin-bottom: 20px; }
    .sig-box-c { color: #00ff41 !important; border: 1px solid #00ff41; padding: 4px 10px; border-radius: 4px; font-weight: bold; background: rgba(0, 255, 65, 0.1); }
    .sig-box-p { color: #007bff !important; border: 1px solid #007bff; padding: 4px 10px; border-radius: 4px; font-weight: bold; background: rgba(0, 123, 255, 0.1); }
    .sig-box-high { color: #ffd700 !important; border: 2px solid #ffd700; padding: 4px 10px; border-radius: 4px; font-weight: bold; background: rgba(255, 215, 0, 0.2); }
    .row-container { border-bottom: 1px solid #172a45; padding: 15px 0; }
    .metric-label { color: #8892b0; font-size: 0.8rem; }
    </style>
    """, unsafe_allow_html=True)

# --- 1. DYNAMISCHE TICKER-QUELLEN ---
@st.cache_data(ttl=86400)
def fetch_all_market_maps():
    maps = {}
    # DAX 40
    try:
        df = pd.read_html("https://en.wikipedia.org/wiki/DAX")[4]
        maps["DAX 40 🇩🇪"] = dict(zip([t.replace('.', '-') + ".DE" for t in df['Ticker']], df['Company']))
    except: maps["DAX 40 🇩🇪"] = {"SAP.DE": "SAP SE", "SIE.DE": "Siemens AG"}

    # NASDAQ 100
    try:
        df = pd.read_html("https://en.wikipedia.org/wiki/Nasdaq-100")[4]
        maps["NASDAQ 100 🇺🇸"] = dict(zip(df['Ticker'], df['Company']))
    except: maps["NASDAQ 100 🇺🇸"] = {"AAPL": "Apple Inc.", "MSFT": "Microsoft"}

    # EURO STOXX 50
    try:
        df = pd.read_html("https://en.wikipedia.org/wiki/EURO_STOXX_50")[3]
        maps["EURO STOXX 50 🇪🇺"] = dict(zip(df['Ticker'], df['Name']))
    except: maps["EURO STOXX 50 🇪🇺"] = {"ASML.AS": "ASML", "MC.PA": "LVMH"}

    # FOREX & INDIZES (Immer vollständig)
    maps["FOREX & INDIZES 🌍"] = {
        "EURUSD=X": "Euro / US-Dollar", "GBPUSD=X": "Pfund / USD", "USDJPY=X": "Dollar / Yen",
        "BTC-USD": "Bitcoin", "ETH-USD": "Ethereum", "^GDAXI": "DAX Index", "^IXIC": "NASDAQ Index"
    }
    return maps

# --- 2. ANALYSE LOGIK ---
def run_analysis(ticker_map, filter_wait=True):
    tickers = list(ticker_map.keys())
    # Nutze Batch-Download für alle Ticker eines Index gleichzeitig
    data = yf.download(tickers, period="1y", interval="1d", group_by='ticker', auto_adjust=True, progress=False)
    
    results = []
    for ticker, name in ticker_map.items():
        try:
            df = data[ticker].dropna() if len(tickers) > 1 else data.dropna()
            if len(df) < 35: continue
            
            close = df['Close']
            sma20 = close.rolling(20).mean()
            curr, p1, p2 = close.iloc[-1], close.iloc[-2], close.iloc[-3]
            c_sma = sma20.iloc[-1]
            
            signal = "C" if (curr > p1 > p2 and curr > c_sma) else "P" if (curr < p1 < p2 and curr < c_sma) else "Wait"
            if filter_wait and signal == "Wait": continue
            
            # Indikatoren
            diff = close.diff()
            g = diff.where(diff > 0, 0).rolling(14).mean()
            l = -diff.where(diff < 0, 0).rolling(14).mean()
            rsi = 100 - (100 / (1 + (g/l))).iloc[-1]
            atr = (df['High'] - df['Low']).rolling(14).mean().iloc[-1]
            
            # Backtest Prob
            hits, total = 0, 0
            if signal != "Wait":
                for i in range(-35, -5):
                    c_h, p_h, p2_h = close.iloc[i], close.iloc[i-1], close.iloc[i-2]
                    s_h = sma20.iloc[i]
                    h_sig = "C" if (c_h > p_h > p2_h and c_h > s_h) else "P" if (c_h < p_h < p2_h and c_h < s_h) else None
                    if h_sig == signal:
                        total += 1
                        if (signal == "C" and close.iloc[i+3] > c_h) or (signal == "P" and close.iloc[i+3] < c_h): hits += 1
            
            prob = (hits / total * 100) if total > 0 else 50.0
            delta = ((curr - df['Open'].iloc[-1]) / df['Open'].iloc[-1]) * 100
            icon = "☀️" if (curr > c_sma and delta > 0.2) else "⚖️" if abs(delta) < 0.2 else "⛈️"
            
            results.append({
                "ticker": ticker, "name": name, "price": curr, "signal": signal,
                "prob": prob, "rsi": rsi, "stop": curr - (atr * 1.5) if signal == "C" else curr + (atr * 1.5),
                "icon": icon, "delta": delta
            })
        except: continue
    return results

# --- 3. UI LAYOUT ---
st.markdown("<div class='header-text'>📡 Bauer Strategy Pro 2026</div>", unsafe_allow_html=True)
st.write(f"Scan-Zeit: {datetime.now().strftime('%H:%M:%S')} | Automatische Aktualisierung aktiv")

with st.expander("ℹ️ VOLLSTÄNDIGE STRATEGIE-LOGIK & SYMBOLE ℹ️", expanded=True):
    st.markdown("""
    - **Marktzustand:** ☀️ Bullish (Kurs > SMA20), ⚖️ Neutral, ⛈️ Bearish (Kurs < SMA20).
    - **C (Call):** Kurs über SMA20 + 3 Tage steigendes Momentum.
    - **P (Put):** Kurs unter SMA20 + 3 Tage fallendes Momentum.
    - **Forex/Indizes:** Werden zur Marktübersicht **immer vollständig** angezeigt.
    - **Aktien:** Es werden nur aktive Signale (C/P) gelistet.
    """)

m_maps = fetch_all_market_maps()
tabs = st.tabs(list(m_maps.keys()))

for i, (index_name, t_map) in enumerate(m_maps.items()):
    with tabs[i]:
        # Logik: Forex zeigt ALLES, Aktien nur Signale
        is_fixed_view = ("FOREX" in index_name)
        data_results = run_analysis(t_map, filter_wait=not is_fixed_view)
        
        if not data_results:
            st.info("Aktuell keine aktiven C/P Signale in dieser Auswahl.")
        else:
            # Sortierung: Aktive Signale zuerst
            data_results = sorted(data_results, key=lambda x: (x['signal'] == "Wait", -x['prob']))
            
            for res in data_results:
                is_fx = any(x in res['ticker'] for x in ["=", "-", "^"])
                fmt = "{:.5f}" if is_fx else "{:.2f}"
                
                st.markdown("<div class='row-container'>", unsafe_allow_html=True)
                c1, c2, c3, c4 = st.columns([2, 1, 0.8, 1.2])
                with c1:
                    st.markdown(f"**{res['name']}** <small>({res['ticker']})</small> {res['icon']}", unsafe_allow_html=True)
                    rsi_color = "#ff4b4b" if res['rsi'] > 70 else "#00ff41" if res['rsi'] < 30 else "#8892b0"
                    st.markdown(f"<span class='metric-label'>RSI: <b style='color:{rsi_color}'>{res['rsi']:.1f}</b></span>", unsafe_allow_html=True)
                with c2:
                    d_color = "#00ff41" if res['delta'] >= 0 else "#ff4b4b"
                    st.markdown(f"**{fmt.format(res['price'])}**<br><span style='color:{d_color}; font-size:0.8rem;'>{res['delta']:+.2f}%</span>", unsafe_allow_html=True)
                with c3:
                    if res['signal'] != "Wait":
                        s_cls = "sig-box-high" if res['prob'] >= 60 else ("sig-box-c" if res['signal'] == "C" else "sig-box-p")
                        st.markdown(f"<span class='{s_cls}'>{res['signal']}</span>", unsafe_allow_html=True)
                    else: st.markdown("<span style='color:#444;'>---</span>", unsafe_allow_html=True)
                with c4:
                    if res['signal'] != "Wait":
                        st.markdown(f"**{res['prob']:.1f}% Win**<br><span class='metric-label'>SL: {fmt.format(res['stop'])}</span>", unsafe_allow_html=True)
                    else: st.markdown("<span class='metric-label'>Monitoring</span>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
