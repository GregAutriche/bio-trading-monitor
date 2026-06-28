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

    # Eventuell doppelt erzeugte Spalten eliminieren
    data = data.loc[:, ~data.columns.duplicated()]

    # Technische Indikatoren berechnen
    data = calculate_rsi(data)
    data = find_elliott_pivots(data)
    return data


df_raw = load_market_data(ticker)

# ==========================================
# 5. PLAUSIBILITÄTS-CHECK & LOGIK-AUSFÜHRUNG
# ==========================================
if df_raw.empty or "Close" not in df_raw.columns:
    st.error(
        f"🚨 Keine validen Kursdaten für '{selected_label}' ({ticker}) empfangen. Bitte überprüfe das Symbol."
    )
elif len(df_raw) < 2:
    st.warning(
        f"⚠️ Zu wenige historische Zeilen für '{selected_label}' vorhanden."
    )
else:
    df_display = df_raw.tail(history_days)

    if len(df_display) < 2:
        st.info(
            "Bitte erhöhe den 'Betrachtungszeitraum Chart' in der Sidebar."
        )
    else:
        # Werte sicher als native Typen extrahieren
        close_display = df_display["Close"].squeeze()
        current_price = float(close_display.iloc[-1])
        previous_price = float(close_display.iloc[-2])

        price_chg = current_price - previous_price
        price_chg_pct = (price_chg / previous_price) * 100

        fg_index = calculate_custom_fear_greed(df_raw)

        # UI Spalten aufbauen
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                label=f"Aktueller Kurs ({selected_label})",
                value=f"{current_price:,.2f}",
                delta=f"{price_chg_pct:+.2f}%",
            )

        with col2:
            # Anwendung deiner festgelegten 10/90-Regel für das Sentiment
            if fg_index > 90:
                status_text = "🔥 Extrem hoch (Gier)"
            elif fg_index < 10:
                status_text = "❄️ Extrem tief (Angst)"
            else:
                status_text = "⚖️ Normalbereich"

            # Hier nutzen wir das Label für den Statustext, um den TypeError im Delta zu umgehen
            st.metric(
                label=f"Fear & Greed Index ({status_text})",
                value=f"{fg_index:.1f} %",
                delta="Basis: RSI & SMA200",
                delta_color="off",
            )

        with col3:
            # Windschatten-Trading Status
            rsi_series = df_raw["RSI"].squeeze()
            close_raw_series = df_raw["Close"].squeeze()

            rsi_now = float(rsi_series.iloc[-1])
            rsi_prev = float(rsi_series.iloc[-2])
            sma_20 = float(close_raw_series.rolling(20).mean().iloc[-1])

            if rsi_now > rsi_prev and current_price > sma_20:
                ws_status = "🟩 Signal: Aktiver Windschatten (Kaufimpuls)"
            else:
                ws_status = "⬛ Kein Windschatten-Momentum"
            st.info(f"**Windschatten-Taktik:**\n{ws_status}")

        # ==========================================
        # 6. CHART-VISUALISIERUNG (PLOTLY-CHARTS)
        # ==========================================
        st.subheader(
            f"📈 Chart-Analyse: {selected_label} (Letzte {history_days} Handelstage)"
        )

        fig = go.Figure()

        # Hauptkurs-Linie
        fig.add_trace(
            go.Scatter(
                x=df_display.index,
                y=close_display,
                mode="lines",
                name="Schlusskurs",
                line=dict(color="#1f77b4", width=2),
            )
        )

        # Elliott-Wellen: Lokale Pivot-Hochs
        high_pivots = df_display[df_display["Pivot_High"].notna()]
        if not high_pivots.empty:
            fig.add_trace(
                go.Scatter(
                    x=high_pivots.index,
                    y=high_pivots["Pivot_High"].squeeze(),
                    mode="markers+text",
                    name="Elliott-Welle (Hoch)",
                    marker=dict(color="red", size=10, symbol="triangle-up"),
                    text=["▲ High"] * len(high_pivots),
                    textposition="top center",
                )
            )

        # Elliott-Wellen: Lokale Pivot-Tiefs
        low_pivots = df_display[df_display["Pivot_Low"].notna()]
        if not low_pivots.empty:
            fig.add_trace(
                go.Scatter(
                    x=low_pivots.index,
                    y=low_pivots["Pivot_Low"].squeeze(),
                    mode="markers+text",
                    name="Elliott-Welle (Tief)",
                    marker=dict(color="green", size=10, symbol="triangle-down"),
                    text=["▼ Low"] * len(low_pivots),
                    textposition="bottom center",
                )
            )

        # Layout-Styling (Dunkles Theme)
        fig.update_layout(
            template="plotly_dark",
            xaxis_title="Datum",
            yaxis_title="Kurs",
            margin=dict(l=20, r=20, t=20, b=20),
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
            ),
        )

        st.plotly_chart(fig, use_container_width=True)

        # ==========================================
        # 7. DASHBOARD DETAILANZEIGE & EXPANDER
        # ==========================================
        expander = st.expander("📊 Daten-Tabelle & Rohwerte einsehen")
        with expander:
            st.dataframe(
                df_display[["Close", "RSI", "Pivot_High", "Pivot_Low"]].tail(
                    10
                )
            )
