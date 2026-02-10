import yfinance as yf
import pandas as pd

# 1. Konfiguration & Ticker-Symbole
# S&P 1000 wird oft durch den ETF 'IVOO' oder den Index ^SP1000 repräsentiert
tickers = {
    "EUR/USD": "EURUSD=X",
    "DAX": "^GDAXI",
    "NASDAQ 100": "^NDX",
    "S&P 1000": "^SP1000"
}

# China-Exposition (Beispielwerte für DAX-Schwergewichte)
china_exposure = {
    "SAP.DE": "ca. 10%",
    "BASF.DE": "ca. 15%",
    "VOW3.DE": "ca. 35%",  # Hohes Risiko
}

def get_market_data():
    print(f"{'Asset':<12} | {'Kurs':<15} | {'Status (10/90)'}")
    print("-" * 45)
    
    for name, ticker in tickers.items():
        data = yf.Ticker(ticker)
        # Aktuellen Kurs und 52-Wochen-Bereich für die 10/90 Regel laden
        info = data.history(period="1y")
        
        if not info.empty:
            current_price = info['Close'].iloc[-1]
            low_52w = info['Low'].min()
            high_52w = info['High'].max()
            
            # Berechnung der relativen Position (0 bis 100%)
            position = ((current_price - low_52w) / (high_52w - low_52w)) * 100
            
            # Status-Logik (Deine Regel)
            if position > 90:
                status = "EXTREM HOCH (>90%)"
            elif position < 10:
                status = "EXTREM TIEF (<10%)"
            else:
                status = "Normalbereich"
            
            # Formatierung: EUR/USD mit 6 Stellen, Indizes mit 2 Stellen
            if name == "EUR/USD":
                print(f"{name:<12} | {current_price:<15.6f} | {status}")
            else:
                print(f"{name:<12} | {current_price:<15.2f} | {status}")
        else:
            print(f"{name:<12} | Datenfehler")

if __name__ == "__main__":
    print("--- Dein App-Dashboard (Stand: 2026) ---")
    get_market_data()
    print("\n--- China-Exposition DAX-Referenz ---")
    for stock, exposure in china_exposure.items():
        print(f"{stock}: {exposure}")
