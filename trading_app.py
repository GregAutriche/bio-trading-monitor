import numpy as np
import pandas as pd
import yfinance as yf


def fetch_extended_data(ticker, period="6mo"):
    """Holt historische Marktdaten für den gewählten Ticker über Yahoo Finance."""
    stock = yf.Ticker(ticker)
    df = stock.history(period=period)
    return df


def calculate_windschatten_strategy(df, lookback_span=90, validity_days=6):
    """Berechnet die fortgeschrittene Windschatten-Strategie:

    1. Momentum (14 Tage Rate of Change)
    2. Volumen-Ausreißer (Vergleich mit 20-Tage SMA)
    3. Position in der 90-Tage Handelsspanne (0% bis 100%)
    4. 5-7 Werktage Gültigkeit (Lookback auf frische Signale)
    5. Sicherheits-Exit (Sofortiges Erlöschen bei Kursen > 90%)
    """
    if df.empty or len(df) < max(lookback_span, 20):
        df["Kurs_Prozentzahl"] = np.nan
        df["Strategie_Aktiv"] = False
        df["Status_Grund"] = "Ungenügende Datenhistorie"
        return df

    # 1. Windschatten-Momentum (14 Tage Rate of Change)
    df["Momentum_ROC"] = (
        (df["Close"] - df["Close"].shift(14)) / df["Close"].shift(14)
    ) * 100

    # 2. Gleitender Durchschnitt des Volumens (20 Tage)
    df["Vol_SMA"] = df["Volume"].rolling(window=20).mean()

    # 3. Exakte Position in der Handelsspanne der letzten X Tage (0% bis 100%)
    low_idx = df["Close"].rolling(window=lookback_span).min()
    high_idx = df["Close"].rolling(window=lookback_span).max()

    spanne = high_idx - low_idx
    # Vermeidung von Division durch Null, falls High == Low
    df["Kurs_Prozentzahl"] = np.where(
        spanne > 0, ((df["Close"] - low_idx) / spanne) * 100, 50.0
    )

    # 4. Kriterien für ein brandneues Signal am Tag des Entstehens
    # - Starkes Momentum (> 3%)
    # - Institutionelles Volumen (20% über dem Durchschnitt)
    # - Hohe Prozentzahl, aber streng im Normalbereich (70% bis 90%)
    df["Frisches_Signal"] = (
        (df["Momentum_ROC"] > 3)
        & (df["Volume"] > df["Vol_SMA"] * 1.2)
        & (df["Kurs_Prozentzahl"] >= 70)
        & (df["Kurs_Prozentzahl"] <= 90)
    ).astype(int)

    # 5. Gültigkeit für die nächsten X Werktage (z.B. 6 Tage) herbeiführen
    # Wenn in den letzten 'validity_days' ein frisches Signal auftrat, bleibt es aktiv
    df["Signal_Fenster_Aktiv"] = (
        df["Frisches_Signal"].rolling(window=validity_days).max() == 1
    )

    # 6. Sicherheits-Exit (MANDATORISCH):
    # Wenn der Kurs HEUTE extrem hoch ist (> 90%), wird die Strategie sofort deaktiviert!
    df["Strategie_Aktiv"] = np.where(
        df["Kurs_Prozentzahl"] > 90, False, df["Signal_Fenster_Aktiv"]
    )

    # 7. Status-Text für die Auswertung generieren
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


# --- Testlauf und Demonstration ---
if name == "main":
    # Watchlist mit Standard-Tickern und deinen ungarischen/bulgarischen Suffixen (.BU / .SO)
    watchlist = ["AAPL", "OTP.BU", "A4L.SO"]

    print("==================================================================")
    print(" BÖRSEN WETTER - WINDSCHATTEN STRATEGIE SCREENER                  ")
    print("==================================================================")

    for ticker in watchlist:
        print(f"Scanne Ticker: {ticker}...")
        try:
            data = fetch_extended_data(ticker, period="6mo")
            if data.empty:
                print(f"-> Keine Daten für {ticker} empfangen.\n")
continue

            processed = calculate_windschatten_strategy(data, validity_days=6)
            latest = processed.iloc[-1]

            print(f" -> Aktueller Schlusskurs: {latest['Close']:.2f}")
            print(
                f" -> Position in Handelsspanne: {latest['Kurs_Prozentzahl']:.2f}%"
            )
            print(f" -> 14-Tage Momentum (ROC): {latest['Momentum_ROC']:.2f}%")
            print(f" -> System-Status: {latest['Status_Grund']}")
            print("-" * 66)

        except Exception as e:
            print(f"-> Fehler beim Verarbeiten von {ticker}: {e}\n")
