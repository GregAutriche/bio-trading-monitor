import sys
import numpy as np
import pandas as pd
import yfinance as yf

# Watchlist für das Börsen-Wetter
watchlist = ["AAPL", "OTP.BU", "A4L.SO"]

print("==================================================================", flush=True)
print(" BÖRSEN WETTER - WINDSCHATTEN STRATEGIE SCREENER                  ", flush=True)
print("==================================================================", flush=True)


def generate_fallback_data():
    """Generiert synthetische Kursdaten, falls die API blockiert oder leer ist."""
    dates = pd.date_range(end=pd.Timestamp.now(), periods=100, freq="B")
    # Simulierter Trend für ein stabiles Signal im Normalbereich
    np.random.seed(42)
    prices = 100 + np.cumsum(np.random.normal(0.5, 1.5, size=100))
    volume = np.random.normal(500000, 100000, size=100)
    # Letzten Tag künstlich pushen für ein aktives Volumen-Signal
    volume[-1] = volume[-1] * 1.5

    df = pd.DataFrame(
        {"Close": prices, "Volume": volume},
        index=dates,
    )
    return df


def calculate_windschatten_strategy(df, lookback_span=90, validity_days=6):
    """Berechnet die Windschatten-Strategie mit Sicherheits-Exits."""
    if df.empty or len(df) < max(lookback_span, 20):
        df["Kurs_Prozentzahl"] = np.nan
        df["Strategie_Aktiv"] = False
        df["Status_Grund"] = "⚠️ Ungenügende Datenhistorie."
        return df

    # 1. Windschatten-Momentum (14 Tage Rate of Change)
    df["Momentum_ROC"] = (
        (df["Close"] - df["Close"].shift(14)) / df["Close"].shift(14)
    ) * 100

    # 2. Gleitender Durchschnitt des Volumens (20 Tage)
    df["Vol_SMA"] = df["Volume"].rolling(window=20).mean()

    # 3. Position in der 90-Tage Handelsspanne (0% bis 100%)
    low_idx = df["Close"].rolling(window=lookback_span).min()
    high_idx = df["Close"].rolling(window=lookback_span).max()
    spanne = high_idx - low_idx

    df["Kurs_Prozentzahl"] = np.where(
        spanne > 0, ((df["Close"] - low_idx) / spanne) * 100, 50.0
    )

    # 4. Kriterien für ein frisches Signal
    df["Frisches_Signal"] = (
        (df["Momentum_ROC"] > 3)
        & (df["Volume"] > df["Vol_SMA"] * 1.2)
        & (df["Kurs_Prozentzahl"] >= 70)
        & (df["Kurs_Prozentzahl"] <= 90)
    ).astype(int)

    # 5. Gültigkeit
    df["Signal_Fenster_Aktiv"] = (
        df["Frisches_Signal"].rolling(window=validity_days).max() == 1
    )

    # 6. Sicherheits-Exit (>90% ist extrem hoch und deaktiviert sofort)
    df["Strategie_Aktiv"] = np.where(
        df["Kurs_Prozentzahl"] > 90, False, df["Signal_Fenster_Aktiv"]
    )

    # 7. Status-Text generieren
    status_conditions = [
        (df["Kurs_Prozentzahl"] > 90),
        (df["Kurs_Prozentzahl"] < 10),
        (df["Strategie_Aktiv"] == True) & (df["Frisches_Signal"] == 1),
        (df["Strategie_Aktiv"] == True) & (df["Frisches_Signal"] == 0),
    ]
    status_outputs = [
        "⚠️ Extrem Hoch (>90%) - Überhitzungsgefahr / Sicherheits-Exit greift!",
        "❄️ Extrem Tief (<10%) - Kein Windschatten-Sog vorhanden.",
        "🔥 MATCH: Signal HEUTE frisch generiert! Gültig für die nächsten 5-7 Werktage.",
        "✅ AKTIV: Signal läuft im Gültigkeitsfenster (Kurs stabil im Normalbereich).",
    ]
    df["Status_Grund"] = np.select(
        status_conditions,
        status_outputs,
        default="⚪ Normalbereich - Kein aktives Signal vorhanden.",
    )

    return df


# --- HAUPTPROGRAMM ---
print("Starte Datenabruf...", flush=True)

for ticker in watchlist:
    print(f"\nScanne Ticker: {ticker}...", flush=True)
    data = pd.DataFrame()
    modus = "LIVE-DATEN"

    try:
        # Sehr kurzes Timeout (5 Sek), damit das Skript niemals einfriert
        stock = yf.Ticker(ticker)
        data = stock.history(period="6mo", timeout=5)
    except Exception:
        # Stummer Übergang zum Fallback bei Netzwerkfehlern
        data = pd.DataFrame()

    # ERZWUNGENE DEFAULT-ANZEIGE: Falls API blockiert oder leere Tabellen liefert
    if data.empty or "Close" not in data.columns:
        modus = "DEFAULT-ANZEIGE (⚠️ Keine Live-Verbindung - Simulierter Testlauf)"
        data = generate_fallback_data()

    # Berechnung & Ausgabe
    try:
        processed = calculate_windschatten_strategy(data, validity_days=6)
        latest = processed.iloc[-1]

        print(f" -> Daten-Modus: {modus}", flush=True)
        print(f" -> Aktueller Schlusskurs: {latest['Close']:.2f}", flush=True)
        print(
            f" -> Position in Handelsspanne: {latest['Kurs_Prozentzahl']:.2f}%",
            flush=True,
        )
        print(
            f" -> 14-Tage Momentum (ROC): {latest['Momentum_ROC']:.2f}%",
            flush=True,
        )
        print(f" -> System-Status: {latest['Status_Grund']}", flush=True)
        print("-" * 66, flush=True)

    except Exception as e:
        print(
            f" -> Daten wurden geladen - aktuell aber keine Ergebnisse berechenbar. Fehler: {e}",
            flush=True,
        )
        print("-" * 66, flush=True)

print("\nScreening-Lauf beendet.", flush=True)
