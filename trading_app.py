import yfinance as yf
import pandas as pd

# 1. MARKTDATEN (Header)
market_headers = [
    {'ticker': '^GDAXI', 'name': 'DAX'},
    {'ticker': '^IXIC', 'name': 'Nasdaq'},
    {'ticker': 'EURUSD=X', 'name': 'EUR/USD'}
]

# 2. CHAMPIONS (Einzelwerte)
champion_stocks = [
    {'ticker': 'BAS.DE', 'name': 'BASF', 'china': '15%'},
    {'ticker': 'VOW3.DE', 'name': 'VW', 'china': '35%'},
    {'ticker': 'OTP.BU', 'name': 'OTP Bank', 'china': '0%'},
    {'ticker': 'A4L.SO', 'name': 'Allterco', 'china': '5%'},
    {'ticker': 'STLD', 'name': 'Steel Dynamics', 'china': '2%'},
    {'ticker': 'WMS', 'name': 'Adv. Drainage', 'china': '0%'}
]

def analyze_data(ticker_list):
    results = []
    for item in ticker_list:
        try:
            stock = yf.Ticker(item['ticker'])
            hist = stock.history(period="1y")
            if hist.empty: continue
            
            curr = hist['Close'].iloc[-1]
            lo, hi = hist['Low'].min(), hist['High'].max()
            pos = ((curr - lo) / (hi - lo)) * 100
            
            status = "Normal"
            if pos < 10: status = "EXTREM TIEF"
            elif pos > 90: status = "EXTREM HOCH"
            
            results.append({
                'Name': item['name'],
                'Preis': f"{curr:.2f}",
                'Position %': f"{pos:.1f}%",
                'Status': status,
                'China-Exp': item.get('china', '-')
            })
        except: continue
    return pd.DataFrame(results)

# Ausführung und Anzeige
print("\n=== MARKT-UMFELD (HEADER) ===")
print(analyze_data(market_headers).drop(columns=['China-Exp']).to_string(index=False))

print("\n=== CHAMPION TRACKER (EUROPA & USA) ===")
print(analyze_data(champion_stocks).to_string(index=False))
