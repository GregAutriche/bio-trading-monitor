import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

# --- 1. KONFIGURATION & DUMMY DATA (Für die Lauffähigkeit) ---
TICKER_NAMES = {"AAPL": "Apple", "TSLA": "Tesla", "NVDA": "NVIDIA", "DAX": "DAX 40", "SAP": "SAP SE"}
STOCKS_ONLY = ["AAPL", "TSLA", "NVDA", "SAP"]
INDEX_MAPPING = {"^GDAXI": "DAX", "^GSPC": "S&P 500", "EURUSD=X": "EUR/USD"}

def get_live_index_data(symbol):
    # Beispielwerte - hier käme dein yfinance Call hin
    return 18500.0, 0.45 

def get_status_info(chg):
    return "🟢" if chg > 0 else "🔴"

def get_extended_stock_analysis(ticker):
    try:
        # Dummy-Daten Generierung (ersetze dies durch deine yfinance Historie)
        dates = pd.date_range(datetime.now() - timedelta(days=300), periods=250)
        df = pd.DataFrame(np.random.randn(250, 4), index=dates, columns=['Open', 'High', 'Low', 'Close'])
        df = df.cumsum() + 150 # Basispreis
        df["Volume"] = np.random.randint(100000, 1000000, size=250)

        cp = df['Close'].iloc[-1]
        chg = ((cp / df['Close'].iloc[-2]) - 1) * 100
        h250 = df['High'].max()
        l250 = df['Low'].min()
        
        # ATR Berechnung (14 Tage)
        df['TR'] = np.maximum(df['High'] - df['Low'], 
                   np.maximum(abs(df['High'] - df['Close'].shift(1)), 
                   abs(df['Low'] - df['Close'].shift(1))))
        atr = df['TR'].tail(14).mean()
        
        # Volumen-Kennzahlen
        curr_vol = df["Volume"].iloc[-1]
        avg_vol = df["Volume"].tail(20).mean()
        vol_rel = curr_vol / avg_vol
        vol_chg = ((curr_vol / df["Volume"].iloc[-2]) - 1) * 100
        
        return {
            "cp": cp, "chg": chg, "h250": h250, "l250": l250, "atr": atr,
            "vol": curr_vol, "vol_rel": vol_rel, "vol_chg": vol_chg,
            "df": df, "chance": round(52.00 + (vol_rel * 1.5) + (abs(chg) * 0.4), 2)
        }
    except: return None

# --- 2. DASHBOARD LAYOUT ---
st.set_page_config(page_title="Trading Monitor Pro", layout="wide")
st.title("🚀 Trading Monitor Pro (Derivate-Fokus) 🚀")

# Header Info
now = datetime.now().strftime("%H:%M:%S")
st.markdown(f"🕒 Letztes Update: {now} | Strategie: **ATR-Risk-Management**")

# --- 3. MARKT-ÜBERSICHT (Indices) ---
cols = st.columns(len(INDEX_MAPPING))
for i, (sym, name) in enumerate(INDEX_MAPPING.items()):
    val, chg = get_live_index_data(sym)
    cols[i].metric(name, f"{val:,.2f}", f"{chg:.2f}%")

st.divider()

# --- 4. DETAIL-ANALYSE & DERIVATE-RECHNER ---
selected = st.selectbox("Aktie zur Analyse wählen:", STOCKS_ONLY, format_func=lambda x: TICKER_NAMES[x])
det = get_extended_stock_analysis(selected)

if det:
    # BASIS-LOGIK FÜR SIGNALE
    weather = "☀️" if det['chg'] > 0.5 else "⛈️" if det['chg'] < -0.5 else "☁️"
    dot = "🟢" if det['chg'] > 0.4 else "🔵" if det['chg'] < -0.4 else "⚪"
    signal_text = "CALL" if det['chg'] > 0.4 else "PUT" if det['chg'] < -0.4 else "NEUTRAL"
    
    # SL / TP Berechnung (ATR-Basis)
    direction = 1 if det['chg'] >= 0 else -1
    sl_price = det['cp'] - (1.5 * det['atr'] * direction)
    tp_price = det['cp'] + (3.0 * det['atr'] * direction)
    distanz_pct = abs((sl_price / det['cp']) - 1)

    # REIHE 1: SIGNAL-METRIKEN
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("SIGNAL", f"{dot} {signal_text}")
    m2.metric("CHANCE", f"{det['chance']}%")
    m3.metric("KURS", f"{det['cp']:.2f} €", f"{det['chg']:.2f}%")
    m4.metric("VOL-REL", f"{det['vol_rel']:.2f}x")

    st.divider()

    # --- DERIVATE SECTION ---
    st.subheader("🛡️ Smart-Leverage & Risikomanagement")
    
    # Smart-Leverage Empfehlung
    max_derivat_loss_target = 0.30 # Ziel: Max 30% Verlust im Derivat bei SL
    opt_hebel = max_derivat_loss_target / distanz_pct if distanz_pct > 0 else 1.0
    
    st.info(f"💡 **Hebel-Empfehlung:** Basierend auf der ATR von {det['atr']:.2f} wird ein **Hebel von max. x{opt_hebel:.1f}** empfohlen, um das 30%-Verlust-Limit einzuhalten.")

    # Rechner
    c1, c2, c3 = st.columns(3)
    with c1:
        hebel = st.number_input("Gewählter Hebel:", min_value=1.0, value=float(round(opt_hebel, 1)))
    with c2:
        depot = st.number_input("Depotgröße (€):", value=10000)
    with c3:
        risk_pct = st.slider("Risiko pro Trade (%)", 0.5, 5.0, 1.0) / 100

    # Berechnung Ergebnisse
    max_loss_euro = depot * risk_pct
    derivat_verlust_pct = distanz_pct * hebel
    max_einsatz = max_loss_euro / derivat_verlust_pct if derivat_verlust_pct > 0 else 0

    r1, r2, r3 = st.columns(3)
    r1.metric("MAX. EINSATZ (€)", f"{max_einsatz:.2f} €")
    r2.metric("VERLUST BEI SL (%)", f"{(derivat_verlust_pct*100):.1f}%")
    r3.metric("STOP-LOSS (BASIS)", f"{sl_price:.2f} €")

    if derivat_verlust_pct > 0.8:
        st.error("⚠️ WARNUNG: Der Hebel ist zu hoch! Der ATR-Stop-Loss liegt zu nah am Knock-Out.")

    # --- CHART ---
    fig = make_subplots(rows=1, cols=1)
    fig.add_trace(go.Candlestick(x=det['df'].index, open=det['df']['Open'], high=det['df']['High'], low=det['df']['Low'], close=det['df']['Close'], name="Kurs"))
    fig.add_hline(y=sl_price, line_dash="dash", line_color="red", annotation_text="SL")
    fig.add_hline(y=tp_price, line_dash="dash", line_color="green", annotation_text="TP")
    fig.update_layout(height=400, template="plotly_dark", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
