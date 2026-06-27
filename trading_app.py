import numpy as np
import pandas as pd
import yfinance as yf

# INFO: Wir definieren die Watchlist direkt oben, um sie für yf.download zu nutzen
watchlist = ["AAPL", "OTP.BU", "A4L.SO"]

print("==================================================================", flush=True)
print(" BÖRSEN WETTER - WINDSCHATTEN STRATEGIE SCREENER                  ", flush=True)
print("==================================================================", flush=True)


def calculate_windschatten_strategy(df, lookback_span=90, validity_days=6):
    """Berechnet die fortgeschrittene Windschatten-Strategie."""
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

    # 3. Exakte Position in der Handelsspanne (0% bis 100%)
    low_idx = df["Close"].rolling(window=lookback_span).min()
    high_idx = df["Close"].rolling(window=lookback_span).max()

    spanne = high_idx - low_idx
    df["Kurs_Prozentzahl"] = np.where(
        spanne > 0, ((df["Close"] - low_idx) / spanne) * 100, 50.0
    )

    # 4. Kriterien für ein brandneues Signal
    df["Frisches_Signal"] = (
        (df["Momentum_ROC"] > 3)
        & (df["Volume"] > df["Vol_SMA"] * 1.2)
        & (df["Kurs_Prozentzahl"] >= 70)
        & (df["Kurs_Prozentzahl"] <= 90)
    ).astype(int)

    # 5. Gültigkeit für die nächsten X Werktage
    df["Signal_Fenster_Aktiv"] = (
        df["Frisches_Signal"].rolling(window=validity_days).max() == 1
    )

    # 6. Sicherheits-Exit (MANDATORISCH)
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


# --- SCHRITT 1: Massen-Download (Viel stabiler gegen Hänger) ---
print("Lade Marktdaten von Yahoo Finance... Bitte warten...", flush=True)
try:
    # group_by='ticker' sorgt dafür, dass wir die Daten pro Aktie sauber trennen können
    raw_data = yf.download(
        watchlist, period="6mo", group_by="ticker", timeout=15, progress=False
    )
    print("-> Download abgeschlossen! Starte Analyse...\n", flush=True)
except Exception as e:
    print(f"❌ Kritischer Netzwerkfehler beim Datenabruf: {e}", flush=True)
    raw_data = None

# --- SCHRITT 2: Verarbeitung der geladenen Daten ---
if raw_data is not None and not raw_data.empty:
    for ticker in watchlist:
        print(f"Scanne Ticker: {ticker}...", flush=True)
        try:
            # Daten für den spezifischen Ticker extrahieren
            if len(watchlist) > 1:
                data = raw_data[ticker].dropna(subset=["Close"]).copy()
            else:
                data = raw_data.copy()

            if data.empty:
                print(
                    f" -> Keine Daten für {ticker} in dieser Periode gefunden.",
                    flush=True,
                )
                print("-" * 66, flush=True)
                continue

            processed = calculate_windschatten_strategy(data, validity_days=6)
            latest = processed.iloc[-1]

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
                f" -> Fehler bei der Berechnung von {ticker}: {e}", flush=True
            )
            print("-" * 66, flush=True)
else:
    print(
        "❌ Keine Daten empfangen. Bitte überprüfe deine Internetverbindung.",
        flush=True,
    )
