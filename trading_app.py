import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh

# --- 1. KONFIGURATION ---
st.set_page_config(page_title="Bio-Trading Monitor Live PRO", layout="wide")
st_autorefresh(interval=60000, limit=1000, key="fscounter")

TICKER_NAMES = {
    "EURUSD=X": "EUR/USD", "^GDAXI": "DAX Index", "AAPL": "Apple (US)", 
    "NVDA": "Nvidia (US)", "TSLA": "Tesla (US)", "SAP.DE": "SAP (DE)"
}

# --- 2. CSS DESIGN ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #E0E0E0; }
    .market-card { background: rgba(255,255,255,0.03); border-radius: 12px; padding: 15px; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 10px; }
    .metric-value { font-size: 1.2rem; font-weight: bold; color: white; }
    .news-container { height: 300px; overflow: hidden; border-left: 2px solid #1E90FF; padding-left: 10px; }
    .news-scroll { animation: scroll-up 40s linear infinite; }
    @keyframes scroll-up { 0% { transform: translateY(0); } 100% { transform: translateY(-50%); } }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNKTIONEN ---
@st.cache_data(ttl=60)
def get_data(ticker, period="60d", interval="1d"):
    try:
        d = yf.download(ticker, period=period, interval=interval, progress=False)
        if isinstance(d.columns, pd.MultiIndex): d.columns = d.columns.get_level_values(0)
        return d
    except: return pd.DataFrame()

def get_options_data(ticker_str):
    try:
        tk = yf.Ticker(ticker_str)
        if not tk.options: return None, None
        exp = tk.options[0] # Nächstes Verfallsdatum
        opt = tk.option_chain(exp)
        # Top 5 Calls/Puts nach Open Interest sortieren
        calls = opt.calls.sort_values("openInterest", ascending=False).head(5)
        puts = opt.puts.sort_values("openInterest", ascending=False).head(5)
        return calls[['strike', 'lastPrice', 'openInterest']], puts[['strike', 'lastPrice', 'openInterest']]
    except: return None, None

# --- 4. DASHBOARD ---
st.title("🚀 Bio-Trading Monitor Live PRO")

# Index & Forex Quickview
cols_m = st.columns(len(TICKER_NAMES))
for i, (t, name) in enumerate(TICKER_NAMES.items()):
    df_m = get_data(t, period="2d")
    if not df_m.empty:
        l = float(df_m['Close'].iloc[-1])
        c = ((l / df_m['Close'].iloc[-2]) - 1) * 100
        cols_m[i].markdown(f'<div class="market-card"><small>{name}</small><br><div class="metric-value">{l:,.2f}</div>'
                           f'<span style="color:{"#00FFA3" if c>0 else "#FF4B4B"}">{c:+.2f}%</span></div>', unsafe_allow_html=True)

st.divider()
c1, c2 = st.columns([2, 1])

with c1:
    st.subheader("📊 Deep-Dive & Options Scanner")
    s_tkr = st.selectbox("Symbol für Analyse:", ["AAPL", "NVDA", "TSLA", "MSFT", "SAP.DE"])
    d_s = get_data(s_tkr, interval="4h")
    
    if not d_s.empty:
        cp = float(d_s['Close'].iloc[-1])
        
        # Target & SL Inputs
        cc1, cc2 = st.columns(2)
        target_val = cc1.number_input("Kursziel:", value=float(cp*1.1), step=0.1)
        sl_val = cc2.number_input("Stop-Loss (SL):", value=float(cp*0.95), step=0.1)
        sl_dist = ((sl_val/cp)-1)*100
        
        st.markdown(f"""
            <div style="background: rgba(30,144,255,0.1); padding: 15px; border-radius: 10px; border: 1px solid #1E90FF;">
                <span style="font-size:1.5rem;">Aktuell: <b>{cp:,.2f}</b></span> | 
                <span style="font-size:1.5rem; color:#1E90FF;">Ziel: <b>{target_val:,.2f}</b> <small style="color:#FF4B4B;">({sl_dist:+.1f}% SL)</small></span>
            </div>
        """, unsafe_allow_html=True)

        # NEU: TOP 5 OPTIONS ANZEIGE
        st.write("---")
        st.write("🎯 **Top 5 Options (Next Expiration by Open Interest)**")
        calls, puts = get_options_data(s_tkr)
        if calls is not None:
            o_col1, o_col2 = st.columns(2)
            o_col1.write("🟢 **Top Calls**")
            o_col1.dataframe(calls, use_container_width=True)
            o_col2.write("🔴 **Top Puts**")
            o_col2.dataframe(puts, use_container_width=True)
        else:
            st.info("Keine Optionsdaten für dieses Symbol verfügbar.")

with c2:
    st.subheader("🗞️ Live News")
    s_obj = yf.Ticker(s_tkr)
    n_list = s_obj.news
    
    if n_list:
        news_items = ""
        for n in n_list[:10]:
            # .get() verhindert den KeyError, falls 'link' oder 'title' fehlen
            title = n.get('title', 'Kein Titel verfügbar')
            link = n.get('link', '#')
            
            news_items += f'''
                <div style="margin-bottom:10px;">
                    <a href="{link}" target="_blank" style="color:#1E90FF; text-decoration:none; font-size:0.85rem;">
                        {title[:80]}...
                    </a>
                </div>'''
        
        # News-Ticker mit Scroll-Effekt
        st.markdown(f'''
            <div class="news-container">
                <div class="news-scroll">
                    {news_items}
                    {news_items}
                </div>
            </div>
        ''', unsafe_allow_html=True)
    else:
        st.info("Keine aktuellen News gefunden.")
