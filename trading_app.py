import yfinance as yf
import sys

def run_scanner():
    # Deine Trading-Konfiguration (500€ Risiko pro Trade)
    watchlist = {
        "NVDA":    {"sl": 120.0, "tp": 150.0},
        "SAP.DE":  {"sl": 170.0, "tp": 200.0},
        "RHM.DE":  {"sl": 480.0, "tp": 550.0}
    }
    risk_eur = 500

    print("--- Programm gestartet: Suche Marktdaten ---")

    for symbol, params in watchlist.items():
        print(f"Prüfe {symbol}...") # Checkpoint 1
        
        try:
            ticker = yf.Ticker(symbol)
            # Wir laden die Daten der letzten 3 Tage
            df = ticker.history(period="3d")
            
            if df.empty:
                print(f"(!) Keine Daten für {symbol} gefunden. (Märkte ggf. geschlossen?)")
                continue
            
            # Letzten verfügbaren Schlusskurs nehmen
            current_price = df['Close'].iloc[-1]
            sl = params['sl']
            tp = params['tp']
            
            # Berechnung
            risk_per_share = abs(current_price - sl)
            shares = int(risk_eur / risk_per_share) if risk_per_share > 0 else 0
            
            # Ergebnis-Ausgabe
            print(f"> {symbol}: Kurs {current_price:.2f} | Stück: {shares} | Ziel: {tp}")
            
        except Exception as e:
            print(f"(!) Fehler bei {symbol}: {e}")

    print("--- Scan beendet ---")

if __name__ == "__main__":
    run_scanner()
