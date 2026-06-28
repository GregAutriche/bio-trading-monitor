import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

# ==========================================
# 1. INITIALISIERUNG & SETUP
# ==========================================
st.set_page_config(
    page_title="Börsen Wetter Dashboard", page_icon="🌦️", layout="wide"
)
st.title("🌦️ Börsen Wetter & Trading Dashboard")

# Ausgelagerte Ticker-Konfiguration (inkl. Osteuropa-Suffixe)
TICKER_DICTS = {
    "Indizes / Champions": {
        "DAX": "^GDAXI",
        "Nasdaq 100": "^NDX",
        "S&P 500": "^GSPC",
        "Euro Stoxx 50": "^STOXX50E",
    },
    "Bulgarien & Ungarn": {
        "OTP Bank (Ungarn)": "OTP.BU",
        "MOL (Ungarn)": "MOL.BU",
        "Richter Gedeon (Ungarn)": "RICHT.BU",
        "Sopharma (Bulgarien)": "SOPH.SO",
        "Eurohold (Bulgarien)": "EUBG.SO",
    },
}

# ==========================================
# 2. MATHEMATISCHE & ANALYTISCHE FUNKTIONEN
# ==========================================


def calculate_rsi(df, window=14):
    """Berechnet den Standard Relative Strength Index (RSI)."""
    if "Close" not in df.columns or len(df) < window:
        df["RSI"] = 50.0
        return df

    # Sicherstellen, dass es sich um eine eindimensionale Reihe handelt
    close_series = df["Close"].squeeze()
    if isinstance(close_series, pd.DataFrame):
        close_series = close_series.iloc[:, 0]

    delta = close_series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / (loss + 1e-9)
    df["RSI"] = 100 - (100 / (1 + rs))
    df["RSI"] = df["RSI"].fillna(50.0)
    return df


def calculate_custom_fear_greed(df):
    """Berechnet einen mathematischen Fear & Greed Score (0-100) basierend auf

    RSI, Abstand zur 200-Tage-Linie und deiner 10/90-Regel.
    """
    if "Close" not in df.columns or len(df) < 200:
        return 50.0

    close_series = df["Close"].squeeze()
    if isinstance(close_series, pd.DataFrame):
        close_series = close_series.iloc[:, 0]

    rsi_series = df["RSI"].squeeze()
    if isinstance(rsi_series, pd.DataFrame):
        rsi_series = rsi_series.iloc[:, 0]

    # Komponente 1: RSI
    rsi_val = float(rsi_series.iloc[-1])

    # Komponente 2: Abstand zur SMA 200
    sma_200 = close_series.rolling(window=200).mean()
    current_close = float(close_series.iloc[-1])
    current_sma200 = float(sma_200.iloc[-1])

    if current_sma200 == 0:
        distance_pct = 0
    else:
        distance_pct = ((current_close - current_sma200) / current_sma200) * 100

    # Skalierung (+-15% Abweichung repräsentieren die Extremzonen)
    distance_score = np.clip((distance_pct + 15) / 30 * 100, 0, 100)

    fg_score = (rsi_val * 0.5) + (distance_score * 0.5)
    return float(np.clip(fg_score, 0, 100))


def find_elliott_pivots(df, window=7):
    """Identifiziert lokale Minima und Maxima (Pivot-Punkte)

    zur Visualisierung potenzieller Elliott-Wellen-Strukturen.
    """
    if "Close" not in df.columns or len(df) < window:
        df["Pivot_High"] = np.nan
        df["Pivot_Low"] = np.nan
        return df

    close_series = df["Close"].squeeze()
    if isinstance(close_series, pd.DataFrame):
        close_series = close_series.iloc[:, 0]

    df["Pivot_High"] = close_series[
        (
            close_series
            == close_series.rolling(window=window, center=True).max()
        )
    ]
    df["Pivot_Low"] = close_series[
        (
            close_series
            == close_series.rolling(window=window, center=True).min()
        )
    ]
    return df


# ==========================================
# 3. SIDEBAR / USERSIGNALE & SLIDER
# ==========================================
st.sidebar.header("🔧 Dashboard Steuerung")

category = st.sidebar.selectbox("Kategorie wählen", list(TICKER_DICTS.keys()))
selected_label = st.sidebar.selectbox(
    "Asset auswählen", list(TICKER_DICTS[category].keys())
)
ticker = TICKER_DICTS[category][selected_label]

history_days = st.sidebar.slider(
    "Betrachtungszeitraum Chart (Tage)",
    min_value=5,
    max_value=120,
    value=20,
    step=5,
)

# ==========================================
# 4. DATENBESCHAFFUNG (RADIKAL BEREINIGT & KUGELSICHER)
# ==========================================


@st.cache_data(ttl=3600)
def load_market_data(ticker_symbol):
    data = yf.download(ticker_symbol, period="2y")

    if data.empty:
        return pd.DataFrame()

    # MultiIndex-Strukturen auflösen
    if isinstance(data.columns, pd.MultiIndex):
        for level in range(data.columns.nlevels):
            columns_at_level = data.columns.get_level_values(level)
            if "Close" in columns_at_level or "Adj Close" in columns_at_level:
                data.columns = columns_at_level
                break

    # Eindeutige Zuweisung der Schlusskursspalte
    if "Adj Close" in data.columns:
        data["Close"] = data["Adj Close"]
    elif "Close" in data.columns:
        pass
    else:
        # Fallback bei Kleinschreibung
        data.columns = [str(col).lower() for col in data.columns]
        if "adj close" in data.columns:
            data["Close"] = data["adj close"]
        elif "close" in data.columns:
            data["Close"] = data["close"]
        else:
            return pd.DataFrame()

    # Eventuell
