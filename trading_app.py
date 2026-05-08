import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

# --- 1. ERWEITERTE TICKER-LISTE (DAX & S&P 500 Fokus) ---
TICKER_NAMES = {
    # DAX 40 Auszug
    "SAP.DE": "SAP SE", "ALV.DE": "Allianz", "SIE.DE": "Siemens", "DTE.DE": "Dt. Telekom", 
    "BMW.DE": "BMW", "ADS.DE": "Adidas", "BAYN.DE": "Bayer", "BAS.DE": "BASF", 
    "VOW3.DE": "Volkswagen", "RHM.DE": "Rheinmetall",
    # S&P 500 Auszug
    "AAPL": "Apple", "MSFT": "Microsoft", "NVDA": "NVIDIA", "AMZN": "Amazon", 
    "TSLA": "Tesla", "GOOGL": "Alphabet", "META": "Meta", "BRK-B": "Berkshire",
    "JPM": "JPMorgan", "LLY": "Eli Lilly"
}
STOCKS_ONLY = list(TICKER_NAMES.keys())
INDEX_MAPPING = {"^GDAXI": "DAX", "^GSPC": "S&P 500", "EURUSD=X": "EUR/USD"}

# --- 2. LOGIK-FUNKTIONEN ---
def get_live_index_data(symbol):
    # Dummy - Hier yf.download() einsetzen
    return 18500.0, 0.45 

def get_extended_stock_analysis(ticker):
    try:
        # Dummy-Daten Generierung (für yf.download(ticker, period='1y'))
        dates = pd.date_range(datetime.now() - timedelta(days=300), periods=250)
        df = pd.DataFrame(np.random.randn(250, 4), index=dates, columns=['Open', 'High', 'Low', 'Close'])
        df = df.cumsum() + 150 
        df["Volume"] = np.random.randint(100000, 1000000, size=250)

        cp = df['Close'].iloc[-1]
        chg = ((cp / df['Close'].iloc[-2]) - 1) * 100
        h250, l250 = df['High'].max(), df['Low'].min()
        
        # ATR (14 Tage)
        df['TR'] = np.maximum(df['High'] - df['Low'], np.maximum(abs(df['High'] - df['Close'].shift(1)), abs(df['Low'] - df['Close'].shift(1))))
        atr = df['TR'].tail(14).mean()
        
        # Volumen & Chance Score
        curr_vol, avg_vol = df["Volume"].iloc[-1], df["Volume"].tail(20).mean()
        vol_rel = curr_vol / avg_vol
        chance_score = 52.00 + (vol_rel * 1.5) + (abs(chg) * 0.4)
        
        return {"cp": cp, "chg": chg, "h250": h250, "l250": l250, "atr": atr, "vol_rel": vol_rel, "df": df, "chance": chance_score}
    except: return None

# --- 3. DASHBOARD UI ---
st.set_page_config(page_title="Trading Pro Board", layout="wide")
st.title("🚀 Smart Trading Board: Chancen & Derivate 🚀")

# Header
now = datetime.now().strftime("%H:%M:%S")
st.markdown(f"🕒 Letztes Update: {now} | Status: 🟢 Live")

# Markt-Übersicht
idx_cols = st.columns(len(INDEX_MAPPING))
for i, (sym, name) in enumerate(INDEX_MAPPING.items()):
    val, chg = get_live_index_data(sym)
    idx_cols[i].metric(name, f"{val:,.2f}", f"{chg:.2f}%")

st.divider()

# --- 4. TOP 7 TRADING-CHANCEN BOARD ---
st.subheader("📊 Top 7 Markt-Chancen (Wahrscheinlichkeits-Ranking)")
rank_list = []
for t in STOCKS_ONLY:
    d = get_extended_stock_analysis(t)
    if d:
        rank_list.append({
            "Aktie": TICKER_NAMES[t],
            "Signal": "🟢 CALL" if d['chg'] > 0 else "🔴 PUT",
            "Chance (%)": round(d['chance'], 2),
            "Vol-Rel": f"{d['vol_rel']:.2f}x",
            "Kurs (€)": f"{d['cp']:.2f}"
        })

df_rank = pd.DataFrame(rank_list).sort_values(by="Chance (%)", ascending=False).head(7)
st.table(df_rank)

# --- 5. DETAIL-SETUP ---
st.divider()
st.subheader("🔍 Smart-Entry: Detail-Setup")
selected = st.selectbox("Aktie wählen:", STOCKS_ONLY, format_func=lambda x: TICKER_NAMES[x])
det = get_extended_stock_analysis(selected)

if det:
    sl_price = det['cp'] - (1.5 * det['atr'] * (1 if det['chg'] > 0 else -1))
    dist_pct = abs((sl_price / det['cp']) - 1)
    
    # Derivate Rechner & Hebel-Advisor
    opt_hebel = 0.30 / dist_pct if dist_pct > 0 else 1.0
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("KURS", f"{det['cp']:.2f} €")
    c2.metric("ATR (Vola)", f"{det['atr']:.2f}")
    c3.metric("STOP-LOSS", f"{sl_price:.2f} €")
    c4.metric("OPT. HEBEL", f"x{opt_hebel:.1f}")
    
    st.info(f"💡 **Trading-Hinweis:** Für {TICKER_NAMES[selected]} wird ein Hebel von **x{int(opt_hebel)}** empfohlen, um das Risiko beim Erreichen des ATR-Stop-Loss auf 30% des Zertifikatwertes zu begrenzen.")

    # Chart
    fig = go.Figure(data=[go.Candlestick(x=det['df'].index, open=det['df']['Open'], high=det['df']['High'], low=det['df']['Low'], close=det['df']['Close'])])
    fig.add_hline(y=sl_price, line_dash="dash", line_color="red", annotation_text="SL")
    fig.update_layout(height=450, template="plotly_dark", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
