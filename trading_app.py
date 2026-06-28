import numpy as np
import pandas as pd
import plotly.graph_objects as [cite: 12]
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
    delta = df["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / (loss + 1e-9)
    df["RSI"] = 100 - (100 / (1 + rs))
    return df


def calculate_custom_fear_greed(df):
    """Berechnet einen mathematischen Fear & Greed Score (0-100) basierend auf

    RSI, Abstand zur 200-Tage-Linie und kurzfristiger Volatilität.
    """
    if len(df) < 200:
        return 50.0  # Fallback bei zu wenig Historie

    # Komponente 1: RSI (0 bis 100)
    rsi_val = df["RSI"].iloc[-1]

    # Komponente 2: Abstand zur SMA 200 (prozentual skaliert)
    sma_200 = df["Close"].rolling(window=200).mean()
    current_close = df["Close"].iloc[-1]
    current_sma200 = sma_200.iloc[-1]
    distance_pct = ((current_close - current_sma200) / current_sma200) * 100

    # Skalierung des Abstands auf eine 0-100er Ratio (Annahme: +-15% Abweichung sind extrem)
    distance_score = np.clip((distance_pct + 15) / 30 * 100, 0, 100)

    # Kombinierter Score (50% RSI, 50% Trendabstand)
    fg_score = (rsi_val * 0.5) + (distance_score * 0.5)
    return float(np.clip(fg_score, 0, 100))


def find_elliott_pivots(df, window=7):
    """Identifiziert lokale Minima und Maxima (Pivot-Punkte)

    zur Visualisierung potenzieller Elliott-Wellen-Strukturen.
    """
    # Lokale Hochs und Tiefs bestimmen (rolling window Methode)
    df["Pivot_High"] = df["Close"][
        (df["Close"] == df["Close"].rolling(window=window, center=True).max())
    ]
    df["Pivot_Low"] = df["Close"][
        (df["Close"] == df["Close"].rolling(window=window, center=True).min())
    ]
    return df


# ==========================================
# 3. SIDEBAR / USERSIGNALE & SLIDER
# ==========================================
st.sidebar.header("🔧 Dashboard Steuerung")

# Kategorie-Auswahl
category = st.sidebar.selectbox("Kategorie wählen", list(TICKER_DICTS.keys()))
selected_label = st.sidebar.selectbox(
    "Asset auswählen", list(TICKER_DICTS[category].keys())
)
ticker = TICKER_DICTS[category][selected_label]

# Dein bewährter 20-Tage-Historie-Slider (und erweiterter Bereich für Indikatoren)
history_days = st.sidebar.slider(
    "Betrachtungszeitraum Chart (Tage)",
    min_value=5,
    max_value=120,
    value=20,
    step=5,
)

# ==========================================
# 4. DATENBESCHAFFUNG (CACHE-OPTIMIERT)
# ==========================================
@st.cache_data(ttl=3600)
def load_market_data(ticker_symbol):
    # Wir laden 1,5 Jahre, um den SMA 200 sauber berechnen zu können
    data = yf.download(ticker_symbol, period="2y")
    if data.empty:
        return pd.DataFrame()
    # Multi-Index-Spalten von yfinance bereinigen, falls vorhanden
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    data = calculate_rsi(data)
    data = find_elliott_pivots(data)
    return data


df_raw = load_market_data(ticker)

if df_raw.empty:
    st.error(
        f"Fehler beim Laden der Daten für {ticker}. Bitte überprüfe das Ticker-Symbol."
    )
else:
    # Filterung für die Anzeige basierend auf dem Slider
    df_display = df_raw.tail(history_days)

    # Aktuelle Werte extrahieren
    current_price = df_display["Close"].iloc[-1]
    previous_price = df_display["Close"].iloc[-2]
    price_chg = current_price - previous_price
    price_chg_pct = (price_chg / previous_price) * 100

    # ==========================================
    # 5. METRIKEN & FEAR AND GREED KPI
    # ==========================================
    fg_index = calculate_custom_fear_greed(df_raw)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            label=f"Aktueller Kurs ({selected_label})",
            value=f"{current_price:,.2f}",
            delta=f"{price_chg_pct:+.2f}%",
        )

    with col2:
        # Auswertung nach deiner 10/90-Regel
        if fg_index > 90:
            status = "🔥 Extrem hoch (Gier)"
            color = "inverse"
        elif fg_index < 10:
            status = "❄️ Extrem tief (Angst)"
            color = "normal"
        else:
            status = "⚖️ Normalbereich"
            color = "off"

        st.metric(
            label="Fear & Greed Sentiment-Score",
            value=f"{fg_index:.1f} %",
            delta=status,
            delta_color=color,
        )

    with col3:
        # Windschatten-Trading Status
        # Logik: Zieht der Kurzfrist-Trend (z.B. RSI steigt) im Windschatten des Haupttrends an?
        rsi_now = df_raw["RSI"].iloc[-1]
        rsi_prev = df_raw["RSI"].iloc[-2]
        if rsi_now > rsi_prev and current_price > df_raw["Close"].rolling(20).mean().iloc[-1]:
            ws_status = "🟩 Signal: Aktiver Windschatten (Kaufimpuls)"
        else:
            ws_status = "⬛ Kein Windschatten-Momentum"
        st.info(f"**Windschatten-Taktik:**\n{ws_status}")

    # ==========================================
    # 6. CHART-VISUALISIERUNG (ELLIOTT-WELLEN & CHART)
    # ==========================================
    st.subheader(f"📈 Chart-Analyse: {selected_label} (Letzte {history_days} Handelstage)")

    fig = graph_objects.Figure()

    # Hauptkurs-Linie
    fig.add_trace(
        graph_objects.Scatter(
            x=df_display.index,
            y=df_display["Close"],
            mode="lines",
            name="Schlusskurs",
            line=dict(color="#1f77b4", width=2),
        )
    )

    # Elliott-Wellen: Pivot Hochs einzeichnen
    high_pivots = df_display[df_display["Pivot_High"].notna()]
    fig.add_trace(
        graph_objects.Scatter(
            x=high_pivots.index,
            y=high_pivots["Pivot_High"],
            mode="markers+text",
            name="Elliott-Welle (Hoch)",
            marker=dict(color="red", size=10, symbol="triangle-up"),
            text=["▲ High"] * len(high_pivots),
            textposition="top center",
        )
    )

    # Elliott-Wellen: Pivot Tiefs einzeichnen
    low_pivots = df_display[df_display["Pivot_Low"].notna()]
    fig.add_trace(
        graph_objects.Scatter(
            x=low_pivots.index,
            y=low_pivots["Pivot_Low"],
            mode="markers+text",
            name="Elliott-Welle (Tief)",
            marker=dict(color="green", size=10, symbol="triangle-down"),
            text=["▼ Low"] * len(low_pivots),
            textposition="bottom center",
        )
    )

    # Layout-Optimierungen
    fig.update_layout(
        template="plotly_dark",
        xaxis_title="Datum",
        yaxis_title="Kurs",
        margin=dict(l=20, r=20, t=20, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    st.plotly_chart(fig, use_container_width=True)

    # ==========================================
    # 7. DASHBOARD DETAILANZEIGE & REGELWERK
    # ==========================================
    expander = st.expander("📊 Daten-Tabelle & Rohwerte einsehen")
    with expander:
        st.dataframe(
            df_display[
                ["Close", "RSI", "Pivot_High", "Pivot_Low"]
            ].tail(10)
        )
