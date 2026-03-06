import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

# --- 0. CONFIG & SETUP ---
st.set_page_config(layout="wide", page_title="Bauer Strategy Pro 2026", page_icon="📡")

# --- 1. TICKER & NAMEN ENGINE ---
@st.cache_data(ttl=86400)
def get_index_data():
    # DAX 40 Ticker & Namen
    try:
        dax_df = pd.read_html("https://en.wikipedia.org")[4] # Meist Tabelle 4
        dax_map = dict(zip([t.replace('.', '-') + ".DE" for t in dax_df['Ticker']], dax_df['Company']))
    except: dax_map = {"SAP.DE": "SAP SE", "SIE.DE": "Siemens AG", "ADS.DE": "Adidas AG"}

    # NASDAQ 100 Ticker & Namen
    try:
        ndx_df = pd.read_html("https://en.wikipedia.org")[4]
        ndx_map = dict(zip(ndx_df['Ticker'], ndx_df['Company']))
    except: ndx_map = {"AAPL": "Apple Inc.", "MSFT": "Microsoft Corp", "NVDA": "NVIDIA Corp"}

    # EuroStoxx 50 (Statische Auswahl für Stabilität)
    estx_map = {"ASML.AS": "ASML Holding", "MC.PA": "LVMH", "OR.PA": "L'Oréal", "SAP.DE": "SAP SE", "LIN.DE": "Linde PLC"}
    
    # Forex & Crypto
    fx_map = {"EURUSD=X": "Euro / US-Dollar", "BTC-USD": "Bitcoin", "ETH-USD": "Ethereum"}

    return {"DAX 40 🇩🇪": dax_map, "NASDAQ 100 🇺🇸": ndx_map, "EURO STOXX 50 🇪🇺": estx_map, "FOREX/CRYPTO 🌍": fx_map}

# --- 2. ANALYSE LOGIK ---
def process_signals(ticker_map):
    tickers = list(ticker_map.keys())
    # Batch Download (schnell)
    data = yf.download(tickers, period="1y", interval="1d", group_by='ticker', auto_adjust=True, progress=False)
    
    final_results = []
    for ticker, full_name in ticker_map.items():
        try:
            df = data[ticker].dropna() if len(tickers) > 1 else data.dropna()
            if len(df) < 30: continue
            
            close = df['Close']
            sma20 = close.rolling(20).mean()
            
            # Bauer-Logik (C/P)
            curr, p, p2 = close.iloc[-1], close.iloc[-2], close.iloc[-3]
            c_sma = sma20.iloc[-1]
            signal = "C" if (curr > p > p2 and curr > c_sma) else "P" if (curr < p < p2 and curr < c_sma) else "Wait"
            
            # FILTER: Nur C oder P anzeigen
            if signal == "Wait": continue
            
            # RSI & ATR
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rsi_val = 100 - (100 / (1 + (gain/loss))).iloc[-1]
            atr = (df['High']-df['Low']).rolling(14).mean().iloc[-1]
            
            # Wahrscheinlichkeit (Backtest 30 Tage)
            hits, total = 0, 0
            for i in range(-35, -5):
                c_h, p_h, p2_h = close.iloc[i], close.iloc[i-1], close.iloc[i-2]
                s_h = sma20.iloc[i]
                h_sig = "C" if (c_h > p_h > p2_h and c_h > s_h) else "P" if (c_h < p_h < p2_h and c_h < s_h) else None
                if h_sig == signal:
                    total += 1
                    if (signal == "C" and close.iloc[i+3] > c_h) or (signal == "P" and close.iloc[i+3] < c_h): hits += 1
            
            prob = (hits / total * 100) if total > 0 else 50.0
            
            final_results.append({
                "ticker": ticker, "name": full_name, "price": curr, "signal": signal,
                "prob": prob, "rsi": rsi_val, "stop": curr - (atr * 1.5) if signal == "C" else curr + (atr * 1.5)
            })
        except: continue
    return final_results

# --- 3. UI RENDERING ---
st.markdown("<h2 style='color:#ffd700;'>📡 Bauer Strategy Pro 2026: Live-Signale</h2>", unsafe_allow_html=True)
st.write(f"Zentraler Scan: {datetime.now().strftime('%H:%M:%S')} (Filter: Nur aktive Signale)")

all_data_maps = get_index_data()
tabs = st.tabs(list(all_data_maps.keys()))

for i, (index_name, ticker_map) in enumerate(all_data_maps.items()):
    with tabs[i]:
        active_signals = process_signals(ticker_map)
        
        if not active_signals:
            st.info(f"Aktuell keine C/P Signale im {index_name} nach Bauer-Logik.")
        else:
            # Sortieren nach Wahrscheinlichkeit
            active_signals = sorted(active_signals, key=lambda x: x['prob'], reverse=True)
            
            for res in active_signals:
                is_fx = any(x in res['ticker'] for x in ["=", "-"])
                fmt = "{:.5f}" if is_fx else "{:.2f}"
                
                with st.container():
                    c1, c2, c3 = st.columns([2, 1, 1.5])
                    with c1:
                        st.markdown(f"**{res['name']}** ({res['ticker']})")
                        rsi_c = "#ff4b4b" if res['rsi'] > 70 else "#3fb950" if res['rsi'] < 30 else "#888"
                        st.markdown(f"<small style='color:{rsi_c}'>RSI: {res['rsi']:.1f}</small>", unsafe_allow_html=True)
                    with c2:
                        color = "#3fb950" if res['signal'] == "C" else "#007bff"
                        st.markdown(f"<h3 style='margin:0; color:{color};'>{res['signal']}</h3>", unsafe_allow_html=True)
                    with c3:
                        p_color = "#ffd700" if res['prob'] >= 60 else "#e0e0e0"
                        st.markdown(f"<b style='color:{p_color}'>{res['prob']:.1f}% Treffer</b><br><small>SL: {fmt.format(res['stop'])}</small>", unsafe_allow_html=True)
                    st.divider()
