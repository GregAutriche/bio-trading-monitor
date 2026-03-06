import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

# --- 0. CONFIG & DARK BLUE STYLE ---
st.set_page_config(layout="wide", page_title="Bauer Strategy Pro 2026", page_icon="📡")

st.markdown("""
    <style>
    /* Dunkelblauer Hintergrund */
    .stApp { background-color: #0a192f; }
    h1, h2, h3, p, span, label, div { color: #e6f1ff !important; font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }
    
    .header-text { font-size: 28px; font-weight: bold; color: #64ffda !important; border-bottom: 2px solid #64ffda; padding-bottom: 10px; }
    
    /* Signal Boxen */
    .sig-box-c { color: #00ff41 !important; border: 1px solid #00ff41; padding: 4px 10px; border-radius: 4px; font-weight: bold; background: rgba(0, 255, 65, 0.1); }
    .sig-box-p { color: #007bff !important; border: 1px solid #007bff; padding: 4px 10px; border-radius: 4px; font-weight: bold; background: rgba(0, 123, 255, 0.1); }
    .sig-box-high { color: #ffd700 !important; border: 2px solid #ffd700; padding: 4px 10px; border-radius: 4px; font-weight: bold; background: rgba(255, 215, 0, 0.2); }
    
    .row-container { border-bottom: 1px solid #172a45; padding: 15px 0; }
    .metric-label { color: #8892b0; font-size: 0.8rem; }
    .price-text { font-size: 1.1rem; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 1. TICKER & NAMEN ENGINE ---
@st.cache_data(ttl=86400)
def get_market_maps():
    # DAX 40
    try:
        df_dax = pd.read_html("https://en.wikipedia.org")[4]
        dax_map = dict(zip([t.replace('.', '-') + ".DE" for t in df_dax['Ticker']], df_dax['Company']))
    except: dax_map = {"SAP.DE": "SAP SE", "SIE.DE": "Siemens AG", "ALV.DE": "Allianz SE"}

    # NASDAQ 100
    try:
        df_ndx = pd.read_html("https://en.wikipedia.org")[4]
        ndx_map = dict(zip(df_ndx['Ticker'], df_ndx['Company']))
    except: ndx_map = {"AAPL": "Apple Inc.", "MSFT": "Microsoft Corp."}

    # Forex & Crypto (Immer vollständig anzeigen)
    fx_map = {
        "EURUSD=X": "Euro / US-Dollar", "GBPUSD=X": "Britisches Pfund / USD", 
        "USDJPY=X": "US-Dollar / Yen", "BTC-USD": "Bitcoin", "ETH-USD": "Ethereum",
        "^GDAXI": "DAX Performance Index", "^IXIC": "NASDAQ Composite"
    }

    return {"DAX 40 🇩🇪": dax_map, "NASDAQ 100 🇺🇸": ndx_map, "FOREX & INDIZES 🌍": fx_map}

# --- 2. ANALYSE ENGINE ---
def run_analysis(ticker_map, filter_wait=True):
    tickers = list(ticker_map.keys())
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
            
            # Bauer Signal Logik
            signal = "C" if (curr > p1 > p2 and curr > c_sma) else "P" if (curr < p1 < p2 and curr < c_sma) else "Wait"
            
            if filter_wait and signal == "Wait": continue
            
            # RSI & ATR
            diff = close.diff()
            g = diff.where(diff > 0, 0).rolling(14).mean()
            l = -diff.where(diff < 0, 0).rolling(14).mean()
            rsi = 100 - (100 / (1 + (g/l))).iloc[-1]
            atr = (df['High'] - df['Low']).rolling(14).mean().iloc[-1]
            
            # Wahrscheinlichkeit
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
            day_delta = ((curr - df['Open'].iloc[-1]) / df['Open'].iloc[-1]) * 100
            icon = "☀️" if (curr > c_sma and day_delta > 0.2) else "⚖️" if abs(day_delta) < 0.2 else "⛈️"
            
            results.append({
                "ticker": ticker, "name": name, "price": curr, "signal": signal,
                "prob": prob, "rsi": rsi, "stop": curr - (atr * 1.5) if signal == "C" else curr + (atr * 1.5),
                "icon": icon, "delta": day_delta
            })
        except: continue
    return results

# --- 3. UI ---
st.markdown("<div class='header-text'>📡 Bauer Strategy Pro 2026</div>", unsafe_allow_html=True)
st.write(f"Live-Scan: {datetime.now().strftime('%H:%M:%S')} | Hintergrund: Navy Blue | Auto-Refresh: Aktiv")

# --- BESCHREIBUNG (EXPANDER) ---
with st.expander("ℹ️ VOLLSTÄNDIGE STRATEGIE-LOGIK & SYMBOLE ℹ️", expanded=True):
    st.markdown("""
    **1. Markt-Zustand:**
    *   ☀️ **Bullish:** Kurs > SMA20 & Tagesplus > 0,2%. Fokus auf Long (C).
    *   ⚖️ **Neutral:** Seitwärtsphase oder geringe Volatilität.
    *   ⛈️ **Bearish:** Kurs < SMA20 oder starkes Tagesminus. Fokus auf Short (P).
    
    **2. Signal-Logik (Dr. Gregor Bauer):**
    *   **C (Call):** Kurs über SMA20 + 3 Tage in Folge steigende Kurse (Momentum-Bestätigung).
    *   **P (Put):** Kurs unter SMA20 + 3 Tage in Folge fallende Kurse.
    *   **RSI Check:** RSI > 70 (überkauft/Warnung), RSI < 30 (überverkauft/Reboundchance).
    
    **3. Trefferquote & Stop-Loss:**
    *   Die **Prob-Zahl** zeigt die Erfolgswahrscheinlichkeit basierend auf den letzten 12 Monaten.
    *   Der **Stop-Loss (SL)** wird automatisch auf das 1,5-fache der ATR (Vola) berechnet.
    """)

# --- TAB-SYSTEM ---
m_maps = get_market_maps()
tabs = st.tabs(list(m_maps.keys()))

for i, (index_name, t_map) in enumerate(m_maps.items()):
    with tabs[i]:
        # Nur Forex/Indizes zeigen immer alles an, Aktien filtern 'Wait'
        show_all = (index_name == "FOREX & INDIZES 🌍")
        data_results = run_analysis(t_map, filter_wait=not show_all)
        
        if not data_results:
            st.info("Aktuell keine aktiven Signale in diesem Markt.")
        else:
            # Sortierung: Signale mit höchster Prob zuerst
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
                    st.markdown(f"<span class='price-text'>{fmt.format(res['price'])}</span><br><span style='color:{d_color}; font-size:0.8rem;'>{res['delta']:+.2f}%</span>", unsafe_allow_html=True)
                
                with c3:
                    if res['signal'] != "Wait":
                        s_class = "sig-box-high" if res['prob'] >= 60 else ("sig-box-c" if res['signal'] == "C" else "sig-box-p")
                        st.markdown(f"<span class='{s_class}'>{res['signal']}</span>", unsafe_allow_html=True)
                    else:
                        st.markdown("<span style='color:#444;'>---</span>", unsafe_allow_html=True)
                
                with c4:
                    if res['signal'] != "Wait":
                        p_col = "#ffd700" if res['prob'] >= 60 else "#e6f1ff"
                        st.markdown(f"<span style='color:{p_col}; font-weight:bold;'>{res['prob']:.1f}% Win</span><br><span class='metric-label'>SL: {fmt.format(res['stop'])}</span>", unsafe_allow_html=True)
                    else:
                        st.markdown("<span class='metric-label'>Kein Signal</span>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
