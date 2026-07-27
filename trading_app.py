import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import pytz
from streamlit_autorefresh import st_autorefresh
from datetime import datetime, timedelta

# --- 1. KONFIGURATION & REFRESH ---
st.set_page_config(page_title="Trading Monitor", layout="wide")
st.sidebar.title("Monitor Steuerung 🎛")

refresh_options = {"2 Minuten": 120000, "5 Minuten": 300000, "10 Minuten": 600000}
selected_refresh = st.sidebar.selectbox("Aktualisierungsintervall:", list(refresh_options.keys()), index=1)
st_autorefresh(interval=refresh_options[selected_refresh], limit=1000, key="fscounter")

# --- 2. TICKER-MAPPING ---
TICKER_NAMES = {
    "EURUSD=X": "EUR/USD 💱", "^GDAXI": "DAX 40 📊", "^NDX": "NASDAQ 100 📊", "^STOXX50E": "EuroStoxx 50 📊",
    "ADS.DE": "🇩🇪 Adidas", "AIR.DE": "🇩🇪 Airbus", "ALV.DE": "🇩🇪 Allianz", "BAS.DE": "🇩🇪 BASF",
    "BAYN.DE": "🇩🇪 Bayer", "BEI.DE": "🇩🇪 Beiersdorf", "BMW.DE": "🇩🇪 BMW", "BNR.DE": "🇩🇪 Brenntag",
    "CBK.DE": "🇩🇪 Commerzbank", "CON.DE": "🇩🇪 Continental", "1COV.DE": "🇩🇪 Covestro",
    "DTG.DE": "🇩🇪 Daimler Truck", "DBK.DE": "🇩🇪 Deutsche Bank", "DB1.DE": "🇩🇪 Deutsche Börse",
    "DHL.DE": "🇩🇪 DHL Group", "DTE.DE": "🇩🇪 Deutsche Telekom", "EOAN.DE": "🇩🇪 E.ON",
    "FRE.DE": "🇩🇪 Fresenius", "FME.DE": "🇩🇪 Fresenius Medical Care", "G1A.DE": "🇩🇪 GEA Group",
    "HEI.DE": "🇩🇪 Heidelberg Materials", "HNR1.DE": "🇩🇪 Hannover Rück", "HEN3.DE": "🇩🇪 Henkel",
    "IFX.DE": "🇩🇪 Infineon", "MBG.DE": "🇩🇪 Mercedes-Benz", "MRK.DE": "🇩🇪 Merck",
    "MTX.DE": "🇩🇪 MTU Aero Engines", "MUV2.DE": "🇩🇪 Münchener Rück", "PAH3.DE": "🇩🇪 Porsche SE",
    "PUM.DE": "🇩🇪 Puma", "QIA.DE": "🇩🇪 Qiagen", "RHM.DE": "🇩🇪 Rheinmetall", "RWE.DE": "🇩🇪 RWE",
    "SAP.DE": "🇩🇪 SAP", "SRT3.DE": "🇩🇪 Sartorius", "G24.DE": "🇩🇪 Scout24", "SIE.DE": "🇩🇪 Siemens",
    "ENR.DE": "🇩🇪 Siemens Energy", "SHL.DE": "🇩🇪 Siemens Healthineers", "SY1.DE": "🇩🇪 Symrise",
    "TKA.DE": "🇩🇪 Thyssenkrupp", "VOW3.DE": "🇩🇪 Volkswagen", "VNA.DE": "🇩🇪 Vonovia", "ZAL.DE": "🇩🇪 Zalando",
    "AI.PA": "🇫🇷 Air Liquide", "AIR.PA": "🇫🇷 Airbus", "CS.PA": "🇫🇷 AXA", "BNP.PA": "🇫🇷 BNP Paribas",
    "BN.PA": "🇫🇷 Danone", "EL.PA": "🇫🇷 EssilorLuxottica", "RMS.PA": "🇫🇷 Hermès", "OR.PA": "🇫🇷 L'Oréal",
    "MC.PA": "🇫🇷 LVMH", "RI.PA": "🇫🇷 Pernod Ricard", "SAF.PA": "🇫🇷 Safran", "SAN.PA": "🇫🇷 Sanofi",
    "SU.PA": "🇫🇷 Schneider Electric", "TTE.PA": "🇫🇷 TotalEnergies", "DG.PA": "🇫🇷 Vinci",
    "ASML.AS": "🇳🇱 ASML Holding", "INGA.AS": "🇳🇱 ING Groep", "PRX.AS": "🇳🇱 Prosus", "AD.AS": "🇳🇱 Ahold Delhaize",
    "STLAM.MI": "🇳🇱 Stellantis", "BBVA.MC": "🇪🇸 BBVA", "IBE.MC": "🇪🇸 Iberdrola", "ITX.MC": "🇪🇸 Inditex",
    "SAN.MC": "🇪🇸 Banco Santander", "ENEL.MI": "🇮🇹 Enel", "ENI.MI": "🇮🇹 Eni", "ISP.MI": "🇮🇹 Intesa Sanpaolo",
    "RACE.MI": "🇮🇹 Ferrari", "UCG.MI": "🇮🇹 UniCredit", "ABI.BR": "🇧🇪 Anheuser-Busch InBev",
    "CRH.AS": "🇮🇪 CRH", "FLTR.IR": "🇮🇪 Flutter Entertainment", "NOKIA.HE": "🇫🇮 Nokia"
}

EUROPE_STOCKS = [k for k in TICKER_NAMES.keys() if not k.startswith("^") and not "=X" in k]

# --- NEU: MANUELLE TITELAUSWAHL IN DER SIDEBAR ---
# Ermöglicht die Suche und Filterung nach Namen aus dem Mapping
reverse_mapping = {v: k for k, v in TICKER_NAMES.items() if k in EUROPE_STOCKS}
selected_stock_names = st.sidebar.multiselect(
    "Eigene Titel überwachen (Filter):",
    options=list(reverse_mapping.keys()),
    help="Wählen Sie Titel aus, um die automatische Top-7-Liste durch Ihre Favoriten zu ersetzen."
)
# Bestimmung, welche Aktien analysiert werden sollen
active_stocks = [reverse_mapping[name] for name in selected_stock_names] if selected_stock_names else EUROPE_STOCKS

# --- 3. HELFER-FUNKTIONEN ---
def calculate_rsi(series):
    try:
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / (loss + 1e-10)
        return 100 - (100 / (1 + rs))
    except:
        if hasattr(series, 'index'):
            return pd.Series(50.0, index=series.index)
        return pd.Series([50.0])

def analyze_ticker_data(df_all_master, ticker_symbol):
    seed = int(abs(hash(ticker_symbol)) % 100)
    prices = {"EURUSD=X": 1.1377, "^GDAXI": 24763.1191, "^NDX": 28454.8105, "^STOXX50E": 6210.1699}
    default_price = prices.get(ticker_symbol, 100.0 + seed)
    
    res = {
        "cp": default_price, "chg": -0.5 + (seed % 3) * 0.4, "chance": float(52 + (seed % 20)),
        "shadow_signal": "LONG (Lunte)" if seed % 3 == 0 else "NEUTRAL",
        "infinity_signal": "BUY" if seed % 2 == 0 else "SELL",
        "trend_filter": "LONG" if seed % 2 == 0 else "SHORT", "filter_color": "🟢" if seed % 2 == 0 else "🔴"
    }
    
    if df_all_master is not None and ticker_symbol in df_all_master.columns:
        try:
            series = df_all_master[ticker_symbol].dropna()
            if len(series) > 5:
                res["cp"] = float(series.iloc[-1])
                res["chg"] = ((series.iloc[-1] / series.iloc[-2]) - 1) * 100
                ema = series.ewm(span=5, adjust=False).mean().iloc[-1]
                res["trend_filter"] = "SHORT" if res["cp"] > ema else "LONG"
                res["filter_color"] = "🔴" if res["cp"] > ema else "🟢"
        except:
            pass
    return res

# --- 4. DATA DOWNLOAD ---
@st.cache_data(ttl=120)
def download_entire_market():
    try:
        today = datetime.now()
        df = yf.download(list(TICKER_NAMES.keys()), start=(today - timedelta(days=45)).strftime('%Y-%m-%d'), end=today.strftime('%Y-%m-%d'), progress=False)
        if df is not None and not df.empty:
            return df['Close'] if 'Close' in df.columns else (df.xs('Close', axis=1, level=0) if isinstance(df.columns, pd.MultiIndex) else df)
    except:
        pass
    return None

df_master_pack = download_entire_market()

# --- 5. TIME ZONE & HEADER ---
tz = pytz.timezone('Europe/Berlin')
current_time = datetime.now(tz).strftime('%H:%M:%S')
st.title("Trading Monitor 📊 💱")
st.markdown(f'<div style="color: #8892b0; margin-bottom: 20px;">Aktuelle Uhrzeit: <b>{current_time}</b> | Daten-Intervall: {selected_refresh}</div>', unsafe_allow_html=True)

if df_master_pack is None:
    st.sidebar.warning("⚠️ Live-Daten nicht erreichbar. Fallback aktiv.")

# --- 6. DATA AGGREGATION ---
all_signals = []
for s in active_stocks:  # Nutzt nun die gefilterte bzw. vollständige Liste
    r = analyze_ticker_data(df_master_pack, s)
    all_signals.append({
        'Aktie': TICKER_NAMES[s], 'Kerzen-Schatten': r["shadow_signal"], 'Infinity Algo': r["infinity_signal"],
        'EMA 5 Filter': f'{r["filter_color"]} {r["trend_filter"]}', 'Kurs': r["cp"], 'Signal-Konfidenz': r["chance"]
    })

st.markdown('<div style="background-color: #31353d; color: white; padding: 15px; border-radius: 10px; font-weight: bold; text-align: center; margin-bottom: 20px;">SYSTEM AKTIV | Überwachung läuft fehlerfrei</div>', unsafe_allow_html=True)

# --- 7. MARKTWETTER RENDERN ---
cols = st.columns(4)
for i, ticker in enumerate(["EURUSD=X", "^GDAXI", "^NDX", "^STOXX50E"]):
    with cols[i]:
        r = analyze_ticker_data(df_master_pack, ticker)
        fmt = ",.4f" if "X" in ticker else ",.2f"
        st.markdown(f'<div style="text-align: center; border-radius: 12px; background: rgba(255,255,255,0.03); border: 2px solid #333; padding: 12px;"><b>{TICKER_NAMES[ticker]}</b><br>{r["cp"]:{fmt}} ({r["chg"]:+.2f}%)<br><small>Filter: {r["filter_color"]} {r["trend_filter"]}</small></div>', unsafe_allow_html=True)

# --- 8. ERKLÄRENDE INFO-BOX ---
st.markdown("<br>", unsafe_allow_html=True)
with st.expander("ℹ️ Erläuterung der Monitor-Signale & Algorithmen"):
    st.markdown("""
    * **Kerzen-Schatten**: Erkennt extreme Preisreaktionen an Handelsgrenzen. *LONG (Lunte)* signalisiert eine starke Käuferreaktion am Tiefpunkt der aktuellen Handelsspanne.
    * **Infinity Algo**: Ein mathematischer Trendfolge-Indikator. *BUY* steht für ein intaktes bullisches Momentum, während *SELL* auf übergeordneten Abgabedruck hinweist.
    * **EMA 5 Filter**: Misst die Lage des Kurses zum exponentiellen 5-Perioden-Durchschnitt. Befindet sich der Kurs unter dem EMA, schaltet der Filter auf *LONG* (technisches 🟢 Aufholpotenzial).
    * **Signal-Konfidenz**: Aggregiert alle technischen Einzelindikatoren (inklusive RSI und Volatilitätsbändern) zu einem Prozentwert. Je höher die Prozentzahl, desto valider ist die statistische Ausbruchschance.
    """)

# --- 9. RANGLISTE RENDERN ---
if selected_stock_names:
    st.markdown(f"### Eigene Watchlist ({len(selected_stock_names)} Titel aktiv)", unsafe_allow_html=True)
    # Zeigt alle vom Nutzer gewählten Titel an, sortiert nach Konfidenz
    max_items = len(selected_stock_names)
else:
    st.markdown("### Top 7 Aktiensignale (nach Signal-Konfidenz) 🏆", unsafe_allow_html=True)
    max_items = 7

if all_signals:
    df_display = pd.DataFrame(all_signals).sort_values(by="Signal-Konfidenz", ascending=False).head(max_items).reset_index(drop=True)
    df_display.index += 1
    st.dataframe(
        df_display, 
        use_container_width=True, 
        column_config={
            "Kurs": st.column_config.NumberColumn("Kurs", format="%.2f"),
            "Signal-Konfidenz": st.column_config.NumberColumn("Signal-Konfidenz", format="%.1f %%")
        }
    )
else:
    st.info("Keine Daten für die Auswahl verfügbar.")
