import os
import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# --- 0. AUTO-REFRESH (45 Sekunden) ---
try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    os.system('pip install streamlit-autorefresh')
    from streamlit_autorefresh import st_autorefresh

st_autorefresh(interval=45000, key="datarefresh")

# --- 1. SCREENER-LOGIK (WIKIPEDIA) ---
@st.cache_data(ttl=3600) # Cache für 1 Stunde, um Wikipedia zu schonen
def get_sp500_tickers():
    # Beispiel für DAX & NASDAQ 100 Screener
    dax_url = "https://en.wikipedia.org"
    ndx_url = "https://en.wikipedia.org/wiki/Nasdaq-100"
    
    try:
        dax = pd.read_html(dax_url)[4]['Ticker'].tolist()
        # DAX Ticker brauchen oft das Suffix .DE
        dax = [f"{t}.DE" if not t.endswith(".DE") else t for t in dax]
        
        ndx = pd.read_html(ndx_url, attrs={'id': "constituents"})[0]['Ticker'].tolist()
        return {"DAX": dax, "NASDAQ 100": ndx}
    except Exception as e:
        st.error(f"Screener-Fehler: {e}")
        return {"FOKUS": ["AAPL", "MSFT", "NVDA", "SAP.DE"]}

# --- 2. BAUER LOGIK FUNKTIONEN ---
def analyze_bauer(df):
    if len(df) < 20: return None
    curr = df['Close'].iloc[-1]
    open_t = df['Open'].iloc[-1]
    high_prev = df['High'].iloc[-2]
    sma20 = df['Close'].rolling(window=20).mean().iloc[-1]
    
    # Candlestick-Stärke
    upper_wick = df['High'].iloc[-1] - max(curr, open_t)
    is_strong = upper_wick < (abs(curr - open_t) * 0.35)
    
    # Wetter
    delta = ((curr - open_t) / open_t) * 100
    icon = "☀️" if (curr > sma20 and delta > 0.5) else "🌤️" if curr > sma20 else "⛈️" if delta < -0.5 else "☁️"
    
    # Stop (1.5x ATR)
    df['TR'] = pd.concat([df['High']-df['Low'], abs(df['High']-df['Close'].shift()), abs(df['Low']-df['Close'].shift())], axis=1).max(axis=1)
    atr = df['TR'].rolling(window=14).mean().iloc[-1]
    
    return {
        "price": curr, "open": open_t, "delta": delta, "icon": icon,
        "signal": (curr > high_prev) and is_strong and (curr > sma20),
        "stop": curr - (atr * 1.5)
    }

# --- 3. UI RENDERING ---
st.set_page_config(layout="wide", page_title="Bauer Screener 2026")
st.title("🔭 Dr. Bauer Auto-Screener 2026")
st.caption(f"Refreshed: {datetime.now().strftime('%H:%M:%S')} | Automatische Index-Analyse")

# METHODIK EXPANDER
with st.expander("📖 ANGEWANDTE LOGIK (SCREENER & ANALYSE)"):
    st.info("""
    - **Screener:** Zieht Live-Listen vom DAX & NASDAQ 100 via Wikipedia.
    - **Trendfilter:** Nur Papiere über dem SMA 20 erhalten ein positives 'Wetter'.
    - **Bauer-Signal (🚀):** Erfordert Breakout über gestriges Hoch + Kerzenschluss im oberen Drittel.
    - **Dynamischer Stop:** Berechnet 1.5 * ATR (Volatilität) als Sicherheitsabstand.
    """)

# SCREENING START
index_data = get_sp500_tickers()
selected_index = st.radio("Wähle Index zum Scannen:", list(index_data.keys()), horizontal=True)

if st.button(f"Scan {selected_index} jetzt starten"):
    with st.spinner(f"Analysiere {len(index_data[selected_index])} Werte nach Dr. Bauer..."):
        results = []
        for ticker in index_data[selected_index]:
            try:
                data = yf.Ticker(ticker).history(period="1mo")
                analysis = analyze_bauer(data)
                if analysis:
                    results.append({"Ticker": ticker, **analysis})
            except: continue
        
        # Sortierung: Signale zuerst, dann nach Performance
        df_res = pd.DataFrame(results).sort_values(by=["signal", "delta"], ascending=False)
        
        # Display
        for _, row in df_res.iterrows():
            c = st.columns([1, 1, 1, 1, 1])
            c[0].markdown(f"**{row['Ticker']}**<br><small>Start: {row['open']:.2f}</small>", unsafe_allow_html=True)
            c[1].markdown(f"## {row['icon']}")
            c[2].metric("Kurs", f"{row['price']:.2f}", f"{row['delta']:+.2f}%")
            c[3].markdown(f"## {'🚀' if row['signal'] else 'Wait'}")
            c[4].warning(f"Stop: {row['stop']:.2f}")
            st.divider()
