import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh

# --- 1. KONFIGURATION ---
st.set_page_config(page_title="Bio-Trading Monitor Live PRO", layout="wide")
st_autorefresh(interval=60000, limit=1000, key="fscounter")

# --- 2. TICKER-MAPPING ---
TICKER_NAMES = {
    "EURUSD=X": "EUR/USD", "EURRUB=X": "EUR/RUB", "^GDAXI": "DAX 40", "^STOXX50E": "EuroStoxx 50",
    "^NDX": "NASDAQ 100", "XU100.IS": "BIST 100", "^NSEI": "Nifty 50",
    # DAX 40
    "ADS.DE": "Adidas", "AIR.DE": "Airbus", "ALV.DE": "Allianz", "BAS.DE": "BASF", "BAYN.DE": "Bayer",
    "BEI.DE": "Beiersdorf", "BMW.DE": "BMW", "BNR.DE": "Brenntag", "CBK.DE": "Commerzbank", "CON.DE": "Continental",
    "1COV.DE": "Covestro", "DTG.DE": "Daimler Truck", "DBK.DE": "Deutsche Bank", "DB1.DE": "Deutsche Börse",
    "DHL.DE": "DHL Group", "DTE.DE": "Telekom", "EON.DE": "E.ON", "FME.DE": "Fresenius Med.", "FRE.DE": "Fresenius SE",
    "GEA.DE": "GEA Group", "HNR1.DE": "Hannover Rück", "HEI.DE": "Heidelberg Mat.", "HEN3.DE": "Henkel",
    "IFX.DE": "Infineon", "MBG.DE": "Mercedes-Benz", "MRK.DE": "Merck", "MTX.DE": "MTU Aero", "MUV2.DE": "Münchener Rück",
    "PAH3.DE": "Porsche SE", "PUM.DE": "Puma", "QIA.DE": "Qiagen", "RHM.DE": "Rheinmetall", "RWE.DE": "RWE",
    "SAP.DE": "SAP", "SIE.DE": "Siemens", "ENR.DE": "Siemens Energy", "SHL.DE": "Siemens Health.", "SY1.DE": "Symrise",
    "VOW3.DE": "Volkswagen", "VNA.DE": "Vonovia", "ZAL.DE": "Zalando",
    # NASDAQ
    "AAPL": "Apple", "MSFT": "Microsoft", "NVDA": "Nvidia", "AMZN": "Amazon", "META": "Meta", "TSLA": "Tesla",
    "GOOGL": "Alphabet", "AVGO": "Broadcom", "COST": "Costco", "NFLX": "Netflix", "AMD": "AMD"
}

TICKER_GROUPS = {
    "DAX 40 (DE)": [k for k in TICKER_NAMES.keys() if k.endswith(".DE")],
    "NASDAQ 100 (US)": ["AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "TSLA", "AVGO", "COST", "NFLX", "AMD"]
}

# --- 3. DESIGN ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #E0E0E0; }
    .market-card { background: rgba(255,255,255,0.03); border-radius: 10px; padding: 12px; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 10px; }
    .metric-value { font-size: 1.1rem; font-weight: bold; font-family: 'Courier New', monospace; color: white; }
    .bullish { color: #00FFA3 !important; font-weight: bold; }
    .bearish { color: #FF4B4B !important; font-weight: bold; }
    .header-box { padding: 15px; border-radius: 12px; text-align: center; margin-bottom: 25px; border: 1px solid #1E90FF; background: rgba(30,144,255,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FUNKTIONEN ---
@st.cache_data(ttl=60)
def get_data(ticker, period="60d", interval="4h"):
    try:
        d = yf.download(ticker, period=period, interval=interval, progress=False)
        if isinstance(d.columns, pd.MultiIndex): d.columns = d.columns.get_level_values(0)
        return d
    except: return pd.DataFrame()

def extract_price(df, idx):
    try:
        if df.empty: return 0.0
        val = df['Close'].iloc[idx]
        return float(val.iloc[0]) if isinstance(val, pd.Series) else float(val)
    except: return 0.0

def run_market_scanner(ticker_list):
    results = []
    # Batch download für Geschwindigkeit
    data = yf.download(ticker_list, period="5d", interval="4h", progress=False)
    if isinstance(data.columns, pd.MultiIndex): close_prices = data['Close']
    else: close_prices = data[['Close']]
    
    for t in ticker_list:
        try:
            series = close_prices[t].dropna()
            if len(series) >= 2:
                cp = series.iloc[-1]; prev = series.iloc[-2]
                trend = ((cp / prev) - 1) * 100
                results.append({"Aktie": TICKER_NAMES.get(t, t), "Kurs": round(cp, 2), "Trend %": round(trend, 2)})
        except: continue
    return pd.DataFrame(results)

# --- 5. AUFBAU ---
st.title("🚀 Bio-Trading Monitor Live PRO")

# 1. WÄHRUNGEN
st.subheader("💱 Fokus/ Währungen 💱")
cf1, cf2, _ = st.columns(3)
for i, t in enumerate(["EURUSD=X", "EURRUB=X"]):
    df_f = get_data(t, period="5d")
    if not df_f.empty:
        l = extract_price(df_f, -1); p = extract_price(df_f, -2)
        diff = ((l/p)-1)*100
        sig = "STARK" if diff > 0.1 else "SCHWACH" if diff < -0.1 else "NEUTRAL"
        sig_clr = "#00FFA3" if diff > 0.1 else "#FF4B4B" if diff < -0.1 else "#8892b0"
        (cf1 if i==0 else cf2).markdown(f'<div class="market-card"><small>{TICKER_NAMES.get(t,t)}</small><br><span class="metric-value">{l:,.4f}</span> <span style="color:{sig_clr}; font-size:0.8rem; float:right;">{sig} ({diff:+.2f}%)</span></div>', unsafe_allow_html=True)

# 2. INDIZES
st.subheader("📈 Fokus/ Indizes 📈")
cols_i = st.columns(5)
for i, t in enumerate(["^GDAXI", "^STOXX50E", "^NDX", "XU100.IS", "^NSEI"]):
    df_i = get_data(t, period="2d")
    if not df_i.empty:
        l = extract_price(df_i, -1); p = extract_price(df_i, -2); c = ((l/p)-1)*100
        cols_i[i].markdown(f'<div class="market-card"><small>{TICKER_NAMES.get(t,t)}</small><br><span class="metric-value">{l:,.2f}</span><br><span class="{"bullish" if c>0 else "bearish"}">{c:+.2f}%</span></div>', unsafe_allow_html=True)

    # --- 8. RISIKO-RADAR: EARNINGS & NEWS ---
    st.subheader("🚨 Risiko-Radar: Termine & News")
    
    col_e1, col_e2 = st.columns([1, 2])
    
    # A. Earnings Check
    with col_e1:
        try:
            ticker_obj = yf.Ticker(sel_stock)
            calendar = ticker_obj.calendar
            if calendar is not None and not calendar.empty:
                # Wir suchen nach dem nächsten Datum
                next_date = calendar.iloc[0, 0]
                days_to_earn = (next_date.tz_localize(None) - pd.Timestamp.now()).days
                
                # Warn-Logik
                warn_col = "#FF4B4B" if days_to_earn <= 7 else "#FFD700" if days_to_earn <= 14 else "#00FFA3"
                st.markdown(f"""
                    <div style="background:rgba(255,255,255,0.03); padding:15px; border-radius:10px; border-top: 4px solid {warn_col};">
                        <small style="color:#8892b0;">NÄCHSTE ZAHLEN</small><br>
                        <b style="font-size:1.1rem; color:white;">{next_date.strftime('%d.%m.%Y')}</b><br>
                        <span style="color:{warn_col};">In {days_to_earn} Tagen</span>
                    </div>
                """, unsafe_allow_html=True)
                if days_to_earn <= 3:
                    st.error("⚠️ ACHTUNG: Earnings stehen kurz bevor! Erhöhtes Gap-Risiko.")
            else:
                st.info("Keine anstehenden Earnings-Termine gefunden.")
        except:
            st.info("Earnings-Daten aktuell nicht verfügbar.")

    # B. News Feed (Was passiert gerade?)
    with col_e2:
        try:
            news = ticker_obj.news[:3] # Die letzten 3 Schlagzeilen
            for n in news:
                st.markdown(f"""
                    <div style="margin-bottom:8px; padding-bottom:5px; border-bottom:1px solid rgba(255,255,255,0.05);">
                        <a href="{n['link']}" target="_blank" style="text-decoration:none; color:#1E90FF; font-size:0.9rem;">
                            <b>{n['title']}</b>
                        </a><br>
                        <small style="color:#8892b0;">Quelle: {n['publisher']} | {pd.to_datetime(n['providerPublishTime'], unit='s').strftime('%H:%M')}</small>
                    </div>
                """, unsafe_allow_html=True)
        except:
            st.write("News-Feed konnte nicht geladen werden.")


st.divider()

# 3. STEUERUNG & SCANNER
cs1, cs2 = st.columns(2)
sel_market = cs1.selectbox("Markt wählen:", list(TICKER_GROUPS.keys()))
sel_stock = cs2.selectbox("Aktie wählen:", TICKER_GROUPS[sel_market], format_func=lambda x: TICKER_NAMES.get(x, x))

st.subheader(f"🎯 Scanner: {sel_market}")
scan_results = run_market_scanner(TICKER_GROUPS[sel_market])
if not scan_results.empty:
    col_c, col_p = st.columns(2)
    with col_c:
        st.markdown("<span class='bullish'>🟢 TOP 5 CALLS</span>", unsafe_allow_html=True)
        st.dataframe(scan_results.sort_values(by="Trend %", ascending=False).head(5), use_container_width=True, hide_index=True)
    with col_p:
        st.markdown("<span class='bearish'>🔴 TOP 5 PUTS</span>", unsafe_allow_html=True)
        st.dataframe(scan_results.sort_values(by="Trend %", ascending=True).head(5), use_container_width=True, hide_index=True)

    # --- 8. RISIKO-RADAR (POSITIONSMIGRATION) ---
st.divider() # Trennung zum Rest
    st.subheader("🚨 Risiko-Radar: Termine & News")
    
    col_e1, col_e2 = st.columns(2)
    
    # Sicherstellen, dass das Ticker-Objekt existiert
    t_obj = yf.Ticker(sel_stock)

    with col_e1:
        try:
            # Versuch, den Kalender zu laden
            cal = t_obj.calendar
            # Check: Ist es ein DataFrame und hat Daten?
            if isinstance(cal, pd.DataFrame) and not cal.empty:
                # Wir nehmen das erste Datum (Earnings Date)
                # Manche Versionen von yfinance geben Spaltennamen anders aus
                e_date = cal.iloc[0, 0] if 'Earnings Date' in cal.index else cal.iloc[0]
                
                # Datum bereinigen für den Vergleich
                if isinstance(e_date, list): e_date = e_date[0]
                days_to = (e_date.replace(tzinfo=None) - pd.Timestamp.now()).days
                
                color = "#FF4B4B" if days_to <= 7 else "#00FFA3"
                st.info(f"Nächste Zahlen am: **{e_date.strftime('%d.%m.%Y')}** (in {days_to} Tagen)")
            else:
                st.write("Keine Termin-Daten (Earnings) gefunden.")
        except Exception as e:
            st.write("Earnings-Check übersprungen.")

    with col_e2:
        try:
            # News abrufen
            stock_news = t_obj.news[:3]
            if stock_news:
                for n in stock_news:
                    st.markdown(f"🔹 **{n['title']}** ({n['publisher']})")
            else:
                st.write("Aktuell keine News verfügbar.")
        except:
            st.write("News-Feed temporär nicht erreichbar.")


# 4. FOKUS ANALYSE
d_s = get_data(sel_stock, period="60d")
if not d_s.empty:
    log_returns = np.log(d_s['Close'] / d_s['Close'].shift(1)).dropna()
    vol = log_returns.std(); ann_vol = vol * np.sqrt(252) * 100
    cp = extract_price(d_s, -1); trend = ((cp / extract_price(d_s, -2)) - 1) * 100

    # Signal-Logik für Header
    if trend > 0.5 and ann_vol < 25: sig_t, sig_i, sig_c = "LONG EINSTIEG", "🟢", "#00FFA3"
    elif trend < -0.5: sig_t, sig_i, sig_c = "SHORT CHANCE", "🔴", "#FF4B4B"
    else: sig_t, sig_i, sig_c = "ABWARTEN", "⚪", "#8892b0"

    st.markdown(f'<div class="header-box" style="border-color:{sig_c};"><b>{TICKER_NAMES.get(sel_stock, sel_stock)}</b> | Signal: <span style="color:{sig_c};">{sig_i} {sig_t}</span> | Vola: {ann_vol:.1f}%</div>', unsafe_allow_html=True)

    # Monte Carlo (15 Tage)
    n_sims = 40; sim_results = []
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(12, 4))
    fig.patch.set_facecolor('#0E1117'); ax.set_facecolor('#0E1117')
    for _ in range(n_sims):
        prices = [cp]
        for _ in range(15): prices.append(prices[-1] * np.exp(np.random.normal(0, vol)))
        sim_results.append(prices[-1]); ax.plot(prices, color=sig_c, alpha=0.1)
    
    t_up, t_down = np.percentile(sim_results, 95), np.percentile(sim_results, 5)
    ax.axhline(t_up, color='#00FFA3', ls='--', alpha=0.3); ax.axhline(t_down, color='#FF4B4B', ls='--', alpha=0.3)
    st.pyplot(fig)

    # --- 6. ORDER-BOARD ---
    is_long = trend >= 0
    dir_label = "[ CALL / LONG ]" if is_long else "[ PUT / SHORT ]"
    dir_col = "#00FFA3" if is_long else "#FF4B4B"

    st.markdown(f"### 📝 Handels-Setup: <span style='color:{dir_col};'>{dir_label}</span>", unsafe_allow_html=True)
    
    entry = cp
    target_price = t_up if is_long else t_down
    stop_loss = cp * 0.97 if is_long else cp * 1.03
    
    risk = abs(entry - stop_loss); reward = abs(target_price - entry)
    crv = reward / risk if risk > 0 else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("EINSTIEG", f"{entry:,.2f}")
    c2.metric("ZIEL (TP)", f"{target_price:,.2f}", f"{(target_price/entry-1)*100:+.2f}%", delta_color="normal" if is_long else "inverse")
    c3.metric("STOP LOSS", f"{stop_loss:,.2f}", f"{(stop_loss/entry-1)*100:+.2f}%", delta_color="inverse" if is_long else "normal")
    
    crv_c = "#00FFA3" if crv >= 2 else "#FFD700" if crv >= 1.5 else "#FF4B4B"
    c4.markdown(f'<div style="text-align:center; background:rgba(255,255,255,0.05); padding:10px; border-radius:10px; border: 1px solid {crv_c};"><small>CRV</small><br><span style="font-size:1.5rem; font-weight:bold; color:{crv_c};">{crv:.2f}</span></div>', unsafe_allow_html=True)

st.info(f"Update: {pd.Timestamp.now().strftime('%H:%M:%S')}")
