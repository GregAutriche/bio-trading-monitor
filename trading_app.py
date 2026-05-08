import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- 1. ERWEITERTES ASSET-UNIVERSUM (DE, US, EU) ---
ASSETS = {
    "DE": {
        "SAP.DE": "SAP", "ALV.DE": "Allianz", "SIE.DE": "Siemens", "DTE.DE": "Telekom", 
        "BMW.DE": "BMW", "ADS.DE": "Adidas", "BAYN.DE": "Bayer", "BAS.DE": "BASF", 
        "RHM.DE": "Rheinmetall", "IFX.DE": "Infineon", "DHL.DE": "DHL Group"
    },
    "US": {
        "AAPL": "Apple", "MSFT": "Microsoft", "NVDA": "NVIDIA", "TSLA": "Tesla", 
        "AMZN": "Amazon", "META": "Meta", "GOOGL": "Alphabet", "NFLX": "Netflix",
        "JPM": "JPMorgan", "LLY": "Eli Lilly", "AVGO": "Broadcom", "COST": "Costco"
    },
    "EU": {
        "MC.PA": "LVMH (FR)", "ASML": "ASML (NL)", "NESN.SW": "Nestlé (CH)", 
        "OR.PA": "L'Oréal (FR)", "SAN.MC": "Santander (ES)", "AIR.PA": "Airbus (EU)",
        "LIN": "Linde (IE)", "NOVN.SW": "Novartis (CH)", "SAP": "SAP (EU)"
    }
}

# Flache Liste für die Suche und Analyse
TICKER_TO_NAME = {ticker: name for region in ASSETS.values() for ticker, name in region.items()}
ALL_TICKERS = list(TICKER_TO_NAME.keys())
INDEX_MAPPING = {"^GDAXI": "DAX", "^GSPC": "S&P 500", "^STOXX50E": "EuroStoxx 50"}

# --- 2. LOGIK-FUNKTIONEN ---
def get_extended_stock_analysis(ticker):
    try:
        # Dummy-Daten Simulation (Hier yf.download() nutzen)
        df = pd.DataFrame(np.random.randn(250, 4), columns=['Open', 'High', 'Low', 'Close']).cumsum() + 150
        df["Volume"] = np.random.randint(100000, 1000000, size=250)
        
        cp = df['Close'].iloc[-1]
        chg = ((cp / df['Close'].iloc[-2]) - 1) * 100
        h250, l250 = df['High'].max(), df['Low'].min()
        
        # ATR-Berechnung
        df['TR'] = np.maximum(df['High'] - df['Low'], np.maximum(abs(df['High'] - df['Close'].shift(1)), abs(df['Low'] - df['Close'].shift(1))))
        atr = df['TR'].tail(14).mean()
        
        # Volumen & Wahrscheinlichkeits-Score
        vol_rel = df["Volume"].iloc[-1] / df["Volume"].tail(20).mean()
        # Strategie-Formel: Vola + Volumen + Trend
        chance_score = 50.0 + (vol_rel * 2.0) + (abs(chg) * 0.5)
        
        return {"cp": cp, "chg": chg, "h250": h250, "l250": l250, "atr": atr, "vol_rel": vol_rel, "df": df, "chance": chance_score}
    except: return None

# --- 3. DASHBOARD UI ---
st.set_page_config(page_title="Trading Pro Board", layout="wide")
st.title("🚀 Multi-Market Trading Board: DE • US • EU 🚀")

# 3.1 MARKER-STATUS (Indices)
idx_cols = st.columns(len(INDEX_MAPPING))
for i, (sym, name) in enumerate(INDEX_MAPPING.items()):
    idx_cols[i].metric(name, "Live-Daten", f"{np.random.uniform(-1, 1):.2f}%")

st.divider()

# --- 4. TOP 7 CHANCEN (Globales Ranking) ---
st.subheader("📊 Top 7 Markt-Chancen (Wahrscheinlichkeits-Ranking)")
rank_data = []
for t in ALL_TICKERS:
    d = get_extended_stock_analysis(t)
    if d:
        region = next(r for r, stocks in ASSETS.items() if t in stocks)
        rank_data.append({
            "Region": region,
            "Aktie": TICKER_TO_NAME[t],
            "Signal": "🟢 CALL" if d['chg'] > 0 else "🔴 PUT",
            "Wahrscheinlichkeit (%)": round(d['chance'], 2),
            "Vol-Rel": f"{d['vol_rel']:.2f}x",
            "Kurs": f"{d['cp']:.2f}"
        })

df_rank = pd.DataFrame(rank_data).sort_values(by="Wahrscheinlichkeit (%)", ascending=False).head(7)
st.table(df_rank)

# --- 5. SMART-ENTRY & DERIVATE-RECHNER ---
st.divider()
st.subheader("🔍 Smart-Entry: Detail-Setup & Derivate-Risiko")

# Auswahl nach Region gefiltert
reg_choice = st.radio("Region wählen:", ["DE", "US", "EU"], horizontal=True)
selected_ticker = st.selectbox("Aktie wählen:", list(ASSETS[reg_choice].keys()), format_func=lambda x: ASSETS[reg_choice][x])

det = get_extended_stock_analysis(selected_ticker)

if det:
    # ATR-Based Stop-Loss
    direction = 1 if det['chg'] > 0 else -1
    sl_price = det['cp'] - (1.5 * det['atr'] * direction)
    dist_pct = abs((sl_price / det['cp']) - 1)
    
    # Hebel-Advisor (Limit: 30% Verlust im Derivat bei SL)
    opt_hebel = 0.30 / dist_pct if dist_pct > 0 else 1.0
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("KURS", f"{det['cp']:.2f} €", f"{det['chg']:.2f}%")
    c2.metric("ATR (14D)", f"{det['atr']:.2f}")
    c3.metric("STOP-LOSS", f"{sl_price:.2f} €", f"{dist_pct*100:.2f}% Abstand")
    c4.metric("SMART HEBEL", f"x{opt_hebel:.1f}", delta="Optimal")

    # Derivate Rechner
    with st.expander("🛡️ Derivate-Positionsrechner"):
        depot = st.number_input("Depotkapital (€):", value=10000)
        risk = st.slider("Risiko pro Trade (%)", 0.5, 3.0, 1.0) / 100
        
        max_loss_euro = depot * risk
        derivat_loss_pct = dist_pct * opt_hebel
        max_pos = max_loss_euro / derivat_loss_pct
        
        st.success(f"Empfohlener Einsatz für das Derivat: **{max_pos:.2f} €** (bei Hebel x{int(opt_hebel)})")

    # Chart
    fig = go.Figure(data=[go.Candlestick(x=det['df'].index, open=det['df']['Open'], high=det['df']['High'], low=det['df']['Low'], close=det['df']['Close'])])
    fig.add_hline(y=sl_price, line_dash="dash", line_color="red", annotation_text="SL (ATR)")
    fig.update_layout(height=400, template="plotly_dark", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

