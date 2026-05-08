import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- 1. KONFIGURATION & ASSET-UNIVERSUM (Regionen: DE, US, EU) ---
ASSETS = {
    "DE": {
        "SAP.DE": "SAP", "ALV.DE": "Allianz", "SIE.DE": "Siemens", "DTE.DE": "Telekom", 
        "RHM.DE": "Rheinmetall", "IFX.DE": "Infineon", "BMW.DE": "BMW", "ADS.DE": "Adidas"
    },
    "US": {
        "AAPL": "Apple", "MSFT": "Microsoft", "NVDA": "NVIDIA", "TSLA": "Tesla", 
        "AMZN": "Amazon", "META": "Meta", "GOOGL": "Alphabet", "LLY": "Eli Lilly"
    },
    "EU": {
        "MC.PA": "LVMH", "ASML": "ASML", "AIR.PA": "Airbus", "OR.PA": "L'Oréal", 
        "NESN.SW": "Nestlé", "LIN": "Linde"
    }
}

TICKER_TO_NAME = {ticker: name for region in ASSETS.values() for ticker, name in region.items()}
ALL_TICKERS = list(TICKER_TO_NAME.keys())
INDEX_MAPPING = {"^GDAXI": "DAX", "^GSPC": "S&P 500", "^STOXX50E": "EuroStoxx 50"}

# --- 2. SWING-TRADING ANALYSE-LOGIK (3-5 Tage Fokus) ---
def get_swing_analysis(ticker):
    try:
        # Simulation von 60 Tagen (Daily Data) - In Produktion: yf.download(ticker, period='60d', interval='1d')
        dates = pd.date_range(datetime.now() - timedelta(days=90), periods=60)
        df = pd.DataFrame(np.random.randn(60, 4), index=dates, columns=['Open', 'High', 'Low', 'Close']).cumsum() + 150
        df["Volume"] = np.random.randint(100000, 1000000, size=60)

        # 1. Trend-Filter: Gleitender Durchschnitt (20 Tage)
        df['SMA20'] = df['Close'].rolling(window=20).mean()
        cp = df['Close'].iloc[-1]
        sma_val = df['SMA20'].iloc[-1]
        is_bullish = cp > sma_val
        
        # 2. Performance über 3 Tage (Trend-Dynamik)
        chg_3d = ((cp / df['Close'].iloc[-4]) - 1) * 100
        
        # 3. ATR-Berechnung für stabilen SL (14 Tage)
        df['TR'] = np.maximum(df['High'] - df['Low'], np.maximum(abs(df['High'] - df['Close'].shift(1)), abs(df['Low'] - df['Close'].shift(1))))
        atr = df['TR'].tail(14).mean()
        
        # 4. Chance-Score (Gewichtet für 3-5 Tage Halten)
        # Bonus für Trend-Konformität und stabiles Volumen
        vol_rel = df["Volume"].tail(3).mean() / df["Volume"].tail(20).mean()
        chance = 50.0 + (15 if is_bullish else -10) + (vol_rel * 3) + (abs(chg_3d) * 0.5)
        
        return {
            "cp": cp, "chg_3d": chg_3d, "atr": atr, "sma20": sma_val, "df": df, 
            "chance": round(chance, 2), "vol_rel": vol_rel, "trend": "BULLISCH" if is_bullish else "BÄRISCH"
        }
    except: return None

# --- 3. DASHBOARD UI ---
st.set_page_config(page_title="Swing-Trade Monitor", layout="wide")
st.title("📈 Swing-Trade Pro: 3-5 Tage Strategie 📉")

# 3.1 Markt-Header
idx_cols = st.columns(len(INDEX_MAPPING))
for i, (sym, name) in enumerate(INDEX_MAPPING.items()):
    idx_cols[i].metric(name, "Index-Level", f"{np.random.uniform(-1, 1):.2f}%")

st.divider()

# --- 4. TOP 7 CHANCEN BOARD (Trend-stabil) ---
st.subheader("📊 Top 7 Swing-Trade Chancen (3-5 Tage Prognose)")
rank_data = []
for t in ALL_TICKERS:
    d = get_swing_analysis(t)
    if d:
        region = next(r for r, stocks in ASSETS.items() if t in stocks)
        rank_data.append({
            "Region": region,
            "Aktie": TICKER_TO_NAME[t],
            "Trend": d['trend'],
            "Wahrscheinlichkeit": d['chance'],
            "Trend-Stärke (3D)": f"{d['chg_3d']:.2f}%",
            "Kurs": f"{d['cp']:.2f} €"
        })

df_rank = pd.DataFrame(rank_data).sort_values(by="Wahrscheinlichkeit", ascending=False).head(7)
# Styling der Tabelle
st.dataframe(df_rank, use_container_width=True, hide_index=True)

# --- 5. DETAIL-SETUP & DERIVATE-LOGIK ---
st.divider()
st.subheader("🔍 Aktions-Plan: Entry & Risiko-Management")

col_sel1, col_sel2 = st.columns([1, 3])
with col_sel1:
    reg_choice = st.radio("Marktsegment:", ["DE", "US", "EU"], horizontal=True)
with col_sel2:
    selected_ticker = st.selectbox("Einzelanalyse:", list(ASSETS[reg_choice].keys()), format_func=lambda x: ASSETS[reg_choice][x])

det = get_swing_analysis(selected_ticker)

if det:
    # Berechnung SL/TP für Swing-Trades (Weiter gefasst)
    direction = 1 if det['chg_3d'] > 0 else -1
    sl_price = det['cp'] - (2.0 * det['atr'] * direction) # 2.0x ATR für mehr Puffer
    tp_price = det['cp'] + (4.0 * det['atr'] * direction)
    dist_pct = abs((sl_price / det['cp']) - 1)
    
    # Hebel-Advisor
    opt_hebel = 0.25 / dist_pct if dist_pct > 0 else 1.0 # Max 25% Verlust im Derivat

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("AKTUELLER KURS", f"{det['cp']:.2f} €", f"{det['chg_3d']:.2f}% (3D)")
    m2.metric("TREND-BASIS (SMA20)", f"{det['sma20']:.2f} €", "Trend-Anker")
    m3.metric("STOP-LOSS (ATR)", f"{sl_price:.2f} €", f"{dist_pct*100:.2f}% Distanz")
    m4.metric("SMART HEBEL (3-5T)", f"x{opt_hebel:.1f}", "Risiko: 25%")

    # Derivate Rechner
    with st.expander("💰 Positionsgrößen-Rechner für Derivate"):
        c_r1, c_r2 = st.columns(2)
        depot = c_r1.number_input("Depotkapital (€):", value=10000)
        risk = c_r2.slider("Risiko vom Gesamtkapital (%)", 0.5, 2.0, 1.0) / 100
        
        max_loss = depot * risk
        derivat_risk_pct = dist_pct * opt_hebel
        pos_size = max_loss / derivat_risk_pct
        
        st.info(f"👉 **Handelsempfehlung:** Investiere **{pos_size:.2f} €** in ein Derivat mit Hebel **x{int(opt_hebel)}**. "
                f"Dein maximaler Verlust bei Erreichen des SL beträgt {max_loss:.2f} €.")

    # Chart mit Trend-Indikator
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=det['df'].index, open=det['df']['Open'], high=det['df']['High'], low=det['df']['Low'], close=det['df']['Close'], name="Kurs"))
    fig.add_trace(go.Scatter(x=det['df'].index, y=det['df']['SMA20'], line=dict(color='orange', width=2), name="SMA 20 (Trend)"))
    fig.add_hline(y=sl_price, line_dash="dash", line_color="red", annotation_text="STOP LOSS")
    fig.add_hline(y=tp_price, line_dash="dash", line_color="green", annotation_text="TAKE PROFIT")
    
    fig.update_layout(height=500, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig, use_container_width=True)

# 6. INFO-BOX
st.sidebar.markdown("""
### 💡 Strategie-Hinweise
*   **Haltedauer:** 3-5 Handelstage.
*   **Entry:** Wenn Wahrscheinlichkeit > 60% und Kurs > SMA20.
*   **Exit:** Automatisch bei TP/SL oder nach 5 Tagen manuell prüfen.
*   **ATR-Puffer:** Wir nutzen 2.0x ATR, um tägliche Schwankungen zu überstehen.
""")
