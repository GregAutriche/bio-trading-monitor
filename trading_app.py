import streamlit as st
import yfinance as yf
import pandas as pd

# --- Konfiguration ---
st.set_page_config(page_title="Bio-Trading Monitor", layout="centered")

SYMBOLS_GENERAL = {
    "EUR/USD": "EURUSD=X", 
    "EUR/RUB": "EURRUB=X", 
    "DAX": "^GDAXI", 
    "EuroStoxx": "^STOXX50E", 
    "Nifty": "^NSEI", 
    "BIST100": "XU100.IS"
}

st.title("📊 Marktüberblick")
st.markdown("---")

# --- Marktdaten untereinander anzeigen ---
for name, ticker in SYMBOLS_GENERAL.items():
    # Daten abrufen
    df_gen = yf.download(ticker, period="5d", interval="1d", progress=False)
    
    if not df_gen.empty and len(df_gen) >= 2:
        last_c = float(df_gen['Close'].iloc[-1])
        prev_c = float(df_gen['Close'].iloc[-2])
        change = ((last_c / prev_c) - 1) * 100
        
        # Formatierung: Währungen mit 5 Nachkommastellen, Indizes mit 2
        if "/" in name or "USD" in ticker or "X" in ticker:
            val_str = f"{last_c:.5f}"
        else:
            val_str = f"{last_c:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        # Anzeige als Metrik (untereinander durch einfachen Aufruf)
        st.metric(
            label=name, 
            value=val_str, 
            delta=f"{change:+.2f}%"
        )
        st.markdown("---") # Trennlinie für bessere Lesbarkeit untereinander
    else:
        st.metric(label=name, value="N/A", delta="Keine Daten")
        st.markdown("---")

# Der Rest deines Codes (Momentum / Monte Carlo) folgt hier...

st.header("1. Globales Markt-Framework")
cols = st.columns(len(SYMBOLS_GENERAL))

for i, (name, ticker) in enumerate(SYMBOLS_GENERAL.items()):
    df_gen = get_market_data(ticker, interval="1d", period="5d")
    
    if not df_gen.empty and len(df_gen) >= 2:
        last_c = float(df_gen['Close'].iloc[-1])
        prev_c = float(df_gen['Close'].iloc[-2])
        change = ((last_c / prev_c) - 1) * 100
        cols[i].metric(name, f"{last_c:.2f}", f"{change:+.2f}%")
    else:
        cols[i].metric(name, "N/A", "Keine Daten")

st.divider()

# SEKTION 2: Einzelaktien-Analyse (H4 Momentum)
st.header("2. Momentum-Analyse (H4 Intervall)")

col_sel1, col_sel2 = st.columns(2)
with col_sel1:
    selected_idx = st.selectbox("Wähle einen Index:", list(STOCKS_BY_INDEX.keys()))
with col_sel2:
    selected_stock = st.selectbox("Wähle eine Aktie:", STOCKS_BY_INDEX[selected_idx])

if selected_stock:
    # H4 Daten laden (Yahoo liefert H4 meist nur für max 60 Tage)
    stock_data = get_market_data(selected_stock, interval="4h", period="60d")
    
    if not stock_data.empty:
        # Momentum Berechnung (z.B. Preis-Differenz über 14 Perioden auf H4)
        stock_data['Momentum'] = stock_data['Close'] - stock_data['Close'].shift(14)
        
        c1, c2 = st.columns([2, 1])
        with c1:
            st.subheader(f"Chart & Momentum: {selected_stock}")
            st.line_chart(stock_data['Close'])
            st.caption("Momentum Indikator (H4 - 14 Perioden)")
            st.area_chart(stock_data['Momentum'])
            
        with c2:
            st.subheader("Monte Carlo (30 Tage)")
            # Simulation starten
            sim_results = run_monte_carlo(stock_data)
            
            fig, ax = plt.subplots(figsize=(10, 7))
            ax.plot(sim_results, color='royalblue', alpha=0.05) # Viele Pfade blass
            ax.plot(sim_results.mean(axis=1), color='red', linewidth=2, label='Mittelwert')
            ax.set_title(f"Simulation für {selected_stock}")
            ax.set_xlabel("Tage in die Zukunft")
            ax.set_ylabel("Kurs")
            ax.grid(True, alpha=0.3)
            st.pyplot(fig)
            
            # Statistisches Kursziel
            target_price = sim_results.mean(axis=1).iloc[-1]
            st.metric("Erwarteter Kurs (30d)", f"{target_price:.2f}")
    else:
        st.error(f"Konnte keine H4-Daten für {selected_stock} abrufen.")

# Footer
st.divider()
st.caption("Datenquelle: Yahoo Finance API. Intervall: H4 (4 Stunden) / D (Tag).")
