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
    if len(df) < window:
        df["RSI"] = 50.0
        return df

    delta = df["Close"].diff()
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
    if len(df) < 200:
        return 50.0  # Fallback bei zu wenig Historie

    # Komponente 1: RSI (0 bis 100)
    rsi_val = float(df["RSI"].iloc[-1])

    # Komponente 2: Abstand zur SMA 200 (prozentual skaliert)
    sma_200 = df["Close"].rolling(window=200).mean()
    current_close = float(df["Close"].iloc[-1])
    current_sma200 = float(sma_200.iloc[-1])

    if current_sma200 == 0:
        distance_pct = 0
    else:
        distance_pct = ((current_close - current_sma200) / current_sma200) * 100

    # Skalierung des Abstands auf eine 0-100er Ratio (+-15% Abweichung sind Extrembereiche)
    distance_score = np.clip((distance_pct + 15) / 30 * 100, 0, 100)

    # Kombinierter Score (50% RSI, 50% Trendabstand)
    fg_score = (rsi_val * 0.5) + (distance_score * 0.5)
    return float(np.clip(fg_score, 0, 100))


def find_elliott_pivots(df, window=7):
    """Identifiziert lokale Minima und Maxima (Pivot-Punkte)

    zur Visualisierung potenzieller Elliott-Wellen-Strukturen.
    """
    if len(df) < window:
        df["Pivot_High"] = np.nan
        df["Pivot_Low"] = np.nan
        return df

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

# Historie-Slider für das Hauptfenster
history_days = st.sidebar.slider(
    "Betrachtungszeitraum Chart (Tage)",
    min_value=5,
    max_value=120,
    value=20,
    step=5,
)


# ==========================================
# 4. DATENBESCHAFFUNG (CACHE-OPTIMIERT & ABGESICHERT)
# ==========================================
@st.cache_data(ttl=3600)
def load_market_data(ticker_symbol):
    # Wir laden 2 Jahre für eine saubere Berechnung des SMA 200
    data = yf.download(ticker_symbol, period="2y")

    if data.empty:
        return pd.DataFrame()

    # Wichtig: Absicherung gegen die neue yfinance MultiIndex-Spaltenstruktur
    if isinstance(data.columns, pd.MultiIndex):
        if "Price" in data.columns.levels[0]:
            data = data.xs("Price", axis=1, level=0)
        else:
            data.columns = data.columns.get_level_values(1)

    # Technische Indikatoren berechnen
    data = calculate_rsi(data)
    data = find_elliott_pivots(data)
    return data


df_raw = load_market_data(ticker)

# ==========================================
# 5. PLAUSIBILITÄTS-CHECK & LOGIK-AUSFÜHRUNG
# ==========================================
if df_raw.empty:
    st.error(
        f"🚨 Keine Daten für '{selected_label}' ({ticker}) empfangen. Bitte überprüfe die Verbindung oder das Kürzel."
    )
elif len(df_raw) < 2:
    st.warning(
        f"⚠️ Zu wenige historische Zeilen für '{selected_label}' vorhanden, um Berechnungen anzustellen."
    )
else:
    # Ausschnitt filtern basierend auf dem Slider
    df_display = df_raw.tail(history_days)

    if len(df_display) < 2:
        st.info(
            "Bitte erhöhe den 'Betrachtungszeitraum Chart' in der Sidebar, um genügend Handelstage zu analysieren."
        )
    else:
        # Hier greifen wir nun absolut absturzsicher auf die Werte zu
        current_price = float(df_display["Close"].iloc[-1])
        previous_price = float(df_display["Close"].iloc[-2])
        price_chg = current_price - previous_price
        price_chg_pct = (price_chg / previous_price) * 100

        # Fear & Greed Sentiment ermitteln
        fg_index = calculate_custom_fear_greed(df_raw)

        # UI Spalten für die Metriken aufbauen
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                label=f"Aktueller Kurs ({selected_label})",
                value=f"{current_price:,.2f}",
                delta=f"{price_chg_pct:+.2f}%",
            )

        with col2:
            # Anwendung deiner festgelegten 10/90-Regel
            if fg_index > 90:
                status = "🔥 Extrem hoch (Gier)"
                color = "inverse"  # Rot/Orange-Warnung in Streamlit
            elif fg_index < 10:
                status = "❄️ Extrem tief (Angst)"
                color = "normal"  # Grüne Kaufzone/Angst-Indikator
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
            rsi_now = float(df_raw["RSI"].iloc[-1])
            rsi_prev = float(df_raw["RSI"].iloc[-2])
            sma_20 = float(df_raw["Close"].rolling(20).mean().iloc[-1])

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

        # Hauptkurs-Linie (Schlusskurs)
        fig.add_trace(
            go.Scatter(
                x=df_display.index,
                y=df_display["Close"],
                mode="lines",
                name="Schlusskurs",
                line=dict(color="#1f77b4", width=2),
            )
        )

        # Elliott-Wellen: Lokale Pivot-Hochs einzeichnen
        high_pivots = df_display[df_display["Pivot_High"].notna()]
        if not high_pivots.empty:
            fig.add_trace(
                go.Scatter(
                    x=high_pivots.index,
                    y=high_pivots["Pivot_High"],
                    mode="markers+text",
                    name="Elliott-Welle (Hoch)",
                    marker=dict(color="red", size=10, symbol="triangle-up"),
                    text=["▲ High"] * len(high_pivots),
                    textposition="top center",
                )
            )

        # Elliott-Wellen: Lokale Pivot-Tiefs einzeichnen
        low_pivots = df_display[df_display["Pivot_Low"].notna()]
        if not low_pivots.empty:
            fig.add_trace(
                go.Scatter(
                    x=low_pivots.index,
                    y=low_pivots["Pivot_Low"],
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
