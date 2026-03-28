import yfinance as yf
import pandas as pd

def analyze_watchlist(watchlist, risk_per_trade_eur=500):
    print(f"\n--- Trading-Scan: Haltedauer 3-10 Tage ---")
    print(f"{'SYMBOL':<10} | {'PREIS':<10} | {'STÜCK':<7} | {'VOLUMEN':<12} | {'CRV':<5} | {'STATUS'}")
    print("-" * 80)

    for symbol, params in watchlist.items():
        try:
            ticker = yf.Ticker(symbol)
            # Sicherere Methode: Letzte 5 Tage laden, um den aktuellsten Schlusskurs zu finden
            data = ticker.history(period="5d")
            
            if data.empty:
                print(f"{symbol:<10} | Keine Daten von Yahoo empfangen.")
                continue
            
            current_price = data['Close'].iloc[-1]
            stop_loss = params['sl']
            take_profit = params['tp']
            
            # Risiko pro Aktie
            risk_per_share = abs(current_price - stop_loss)
            
            if risk_per_share <= 0.01:
                print(f"{symbol:<10} | Risiko zu gering/Stop-Loss ungültig.")
                continue

            # Stückzahl berechnen
            shares = int(risk_per_trade_eur / risk_per_share)
            total_position_value = shares * current_price
            
            # Kennzahlen (3-5-7 Regel)
            potential_gain = abs(take_profit - current_price)
            crv = potential_gain / risk_per_share
            profit_pct = (potential_gain / current_price) * 100
            
            status = "OK"
            if profit_pct < 7: status = "(!) Ziel < 7%"
            if crv < 1.5: status = "(!) CRV schwach"

            print(f"{symbol:<10} | {current_price:>10.2f} | {shares:>7} | {total_position_value:>10.2f} | {crv:>5.2f} | {status}")

        except Exception as e:
            print(f"{symbol:<10} | Fehler: {e}")

# --- KONFIGURATION ---
my_watchlist = {
    "NVDA":    {"sl": 120.00, "tp": 150.00},
    "SAP.DE":  {"sl": 170.00, "tp": 200.00},
    "RHM.DE":  {"sl": 480.00, "tp": 550.00}
}

# WICHTIG: Dieser Block startet das Programm erst!
if __name__ == "__main__":
    analyze_watchlist(my_watchlist)
