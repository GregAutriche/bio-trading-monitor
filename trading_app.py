import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go

st.set_page_config(page_title="Market-Maker Flow Monitor", layout="wide")

# Komprimierte Asset-Auswahl, um das API-Limit von Yahoo Finance zu schonen
ASSETS = {
    "DE": {
        "ADS.DE": "Adidas", "AIR.DE": "Airbus", "ALV.DE": "Allianz", "BAS.DE": "BASF",
        "BAYN.DE": "Bayer", "BMW.DE": "BMW", "DBK.DE": "Deutsche Bank", "DTE.DE": "Deutsche Telekom",
        "RHM.DE": "Rheinmetall", "SAP.DE": "SAP", "SIE.DE": "Siemens", "VOW3.DE": "Volkswagen"
    },
    "US": {
        "AAPL": "Apple", "MSFT": "Microsoft", "GOOGL": "Alphabet", "AMZN": "Amazon", 
        "META": "Meta", "NVDA": "Nvidia", "TSLA": "Tesla", "AMD": "AMD", 
        "NFLX": "Netflix", "PLTR": "Palantir", "COST": "Costco", "WMT": "Walmart"
    },
    "EU": {
        "AI.PA": "Air Liquide", "AIR.PA": "Airbus", "BNP.PA": "BNP Paribas", "MC.PA": "LVMH", 
        "OR.PA": "L'Oréal", "TTE.PA": "TotalEnergies", "ASML.AS": "ASML Holding", "INGA.AS": "ING Groep",
        "SAN.MC": "Banco Santander", "RACE.MI": "Ferrari", "UCG.MI": "UniCredit", "NOKIA.HE": "Nokia"
    }
}

TICKER_TO_NAME = {ticker: name for region in ASSETS.values() for ticker, name in region.items()}
INDEX_MAP = {"^GDAXI": "DAX", "^STOXX50E": "EUROSTOXX 50", "^IXIC": "NASDAQ"}

# --- 2. HILFSFUNKTIONEN & SICHERHEITSELEMENTE ---
def safe_float(val):
    if isinstance(val, (pd.Series, np.ndarray, pd.DataFrame)):
        return float(val.iloc[-1]) if hasattr(val, 'iloc') else float(val)
    return float(val)

@st.cache_data(ttl=300)
def get_live_data(ticker):
    try:
        df = yf.download(ticker, period="60d", interval="1d", progress=False, multi_level_index=False)
        if df is not None and not df.empty:
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            return df
        return None
    except:
        return None

def analyze_market_maker_flow(ticker, df):
    cp = safe_float(df['Close'].iloc[-1])
    prev_3d = safe_float(df['Close'].iloc[-4])
    chg_3d = ((cp / prev_3d) - 1) * 100
    df['TR'] = np.maximum(df['High'] - df['Low'], np.maximum(abs(df['High'] - df['Close'].shift(1)), abs(df['Low'] - df['Close'].shift(1))))
    atr = safe_float(df['TR'].tail(14).mean())
    df['Vol_SMA20'] = df['Volume'].rolling(window=20).mean()
    high_volume_break = safe_float(df['Volume'].iloc[-1]) > (safe_float(df['Vol_SMA20'].iloc[-1]) * 1.3)
    liquidity_pool_high = safe_float(df['High'].tail(20).max())
    liquidity_pool_low = safe_float(df['Low'].tail(20).min())
    dist_to_low = (cp - liquidity_pool_low) / cp
    dist_to_high = (liquidity_pool_high - cp) / cp
    
    if dist_to_low < 0.02 and high_volume_break:
        direction, chance, signal_type = 1, 75.0, "Liquidity Grab (Buy)"
    elif dist_to_high < 0.02 and high_volume_break:
        direction, chance, signal_type = -1, 70.0, "Liquidity Grab (Sell)"
    else:
        direction, chance, signal_type = (1, 45.0, "Standard Order Flow") if chg_3d > 0 else (-1, 45.0, "Standard Order Flow")
    
    return {"cp": cp, "atr": atr, "chance": chance, "direction": direction, "df": df, "pool_high": liquidity_pool_high, "pool_low": liquidity_pool_low, "type": signal_type}

st.subheader("🌐 Markt-Indikation")
eurusd_df = get_live_data("EURUSD=X")
if eurusd_df is not None:
    st.metric("EUR / USD", f"{safe_float(eurusd_df['Close'].iloc[-1]):.5f}")

st.divider()

reg = st.radio("Region auswählen:", ["DE", "US", "EU"], horizontal=True)
sel = st.selectbox("Aktie analysieren:", list(ASSETS[reg].keys()), format_func=lambda x: ASSETS[reg][x])

# Das MUSS exakt hier vor Zeile 62 stehen
df_sel = get_live_data(sel)

if df_sel is not None and len(df_sel) > 20:
    det = analyze_market_maker_flow(sel, df_sel)
    direction = det['direction']
    
    # 1. Smart-Money SL/TP Platzierung
    if direction == 1:
        sl = det['pool_low'] - (0.5 * det['atr'])
        tp = det['pool_high']
    else:
        sl = det['pool_high'] + (0.5 * det['atr'])
        tp = det['pool_low']
        
    # 2. Hebel-Berechnung korrigieren (Mindestens Hebel x1.0 erzwingen)
    dist = abs((sl / det['cp']) - 1)
    opt_h = 0.15 / dist if dist > 0 else 1.0
    if opt_h < 1.0:
        opt_h = 1.0  # Verhindert Hebel unter x1
    
    # 3. UI-Spalten-Layout optimieren (Mehr Platz gegen das Abschneiden "Standar...")
    c1, c2, c3, c4 = st.columns([1.5, 1, 1, 1])
    c1.metric("SETUP TYP", det['type'])
    c2.metric("MM-STOP-LOSS", f"{sl:.2f} €")
    c3.metric("HEBEL", f"x{opt_h:.1f}")
    c4.metric("KONFIDENZ (%)", f"{det['chance']:.2f}")
    
    # 4. Visueller Hinweis im Dashboard, falls kein aktiver Grab stattfindet
    if "Standard" in det['type']:
        st.warning("ℹ️ **Keine akute Liquiditäts-Jagd:** Der Kurs befindet sich in der normalen Handelsspanne. Es liegt kein extremes Übertreibungsmuster vor. Institutionelle Positionen werden aktuell nur im normalen Trendverlauf bedient.")
    else:
        st.success(f"🎯 **Achtung, Market Maker Aktivität!** Ein {det['type']} wurde detektiert. Die Institutionellen greifen an den Zonen an.")
    
    with st.expander("📋 Detaillierte Handelsanweisung (Smart Money Execution)", expanded=True):
        st.markdown(f"### Order-Ticket: {TICKER_TO_NAME[sel]}")
        col_o1, col_o2 = st.columns(2)
        
        with col_o1:
            st.markdown("**Basis-Informationen:**")
            st.write(f"🔹 **Richtung:** {'LONG / CALL (Absorption)' if direction == 1 else 'SHORT / PUT (Distribution)'}")
            st.write(f"🔹 **Asset / Ticker:** {TICKER_TO_NAME[sel]} ({sel})")
            st.write(f"🔹 **Referenzkurs:** {det['cp']:.2f} €")
            st.write(f"🔹 **Oberer Pool (Retail-Stops):** {det['pool_high']:.2f} €")
            st.write(f"🔹 **Unterer Pool (Retail-Stops):** {det['pool_low']:.2f} €")
        
        with col_o2:
            st.markdown("**Risiko- & Derivate-Parameter:**")
            st.write(f"🎯 **Ziel-Hebel:** x{opt_h:.1f}")
            st.write(f"🛑 **Stop-Loss (Hinter Struktur):** {sl:.2f} €")
            st.write(f"🏁 **Kursziel (Gegenüberliegende Liquidität):** {tp:.2f} €")
            st.write(f"⏳ **Erwartete Haltedauer:** 2 - 5 Handelstage")
            
        st.markdown("---")
        order_text = f"ORDER: {TICKER_TO_NAME[sel]} | {('CALL_ABSORPTION' if direction==1 else 'PUT_DISTRIBUTION')} | Hebel x{opt_h:.1f} | SL: {sl:.2f} | TP: {tp:.2f}"
        st.code(order_text, language="text")
        
    # CHART GENERIERUNG
    fig = go.Figure(data=[go.Candlestick(
        x=det['df'].index, open=det['df']['Open'], high=det['df']['High'], low=det['df']['Low'], close=det['df']['Close'], name="Kurs"
    )])
    fig.add_hline(y=det['pool_high'], line_dash="solid", line_color="orange", line_width=2, annotation_text="Retail Buy Stops")
    fig.add_hline(y=det['pool_low'], line_dash="solid", line_color="orange", line_width=2, annotation_text="Retail Sell Stops")
    fig.add_hline(y=sl, line_dash="dash", line_color="red", line_width=1.5, annotation_text="Smart SL")
    fig.add_hline(y=tp, line_dash="dash", line_color="green", line_width=1.5, annotation_text="Smart TP")
    fig.update_layout(height=500, template="plotly_dark", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

else:
    st.error(f"⚠️ Keine Live-Daten für {TICKER_TO_NAME.get(sel, sel)} ({sel}) empfangen. Bitte überprüfe deine Internetverbindung.")
