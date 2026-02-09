import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import time

# 1. KONFIGURATION & ZEITZONE
# ---------------------------------------------------------
st.set_page_config(page_title="Kontrollturm Aktiv", layout="wide")
local_tz = pytz.timezone('Europe/Berlin')

# 2. DATEN-FUNKTION (Mit automatischer Aktualisierung alle 60 Sek)
# ---------------------------------------------------------
@st.cache_data(ttl=60)
def get_kita_data():
    # Hier simulieren wir den Abruf deiner monetären Werte
    # Ersetze dies durch deine echte Datenquelle (CSV, API oder Google Sheet)
    data = {
        "Posten": ["Stunden Kita", "Sprossen Invest", "Sonstiges"],
        "Wert": [1.0, 45.50, 10.00], # Beispiel für die "eine Stunde" Differenz
        "Kurs_Status": [95, 12, 50]   # Prozentwert für die Analyse
    }
    return pd.DataFrame(data)

# 3. HEADER & UHRZEIT (Synchron mit deiner Windows-Uhr)
# ---------------------------------------------------------
now = datetime.now(local_tz)
t1, t2 = st.columns([3, 1])

with t1:
    st.title("🚀 Kontrollturm Aktiv")
with t2:
    st.metric("Lokalzeit (Wien/Berlin)", now.strftime("%H:%M:%S"))

# 4. MONETÄRE ÜBERSICHT & AKTUALISIERUNG
# ---------------------------------------------------------
df = get_kita_data()

st.subheader("Finanzielles Controlling")
cols = st.columns(len(df))

for i, row in df.iterrows():
    # Logik für extrem hohe/tiefe Kurse (>90% / <10%)
    status_color = "normal"
    if row['Kurs_Status'] > 90:
        status_color = "inverse" # Rot/Extrem Hoch
        label_suffix = "⚠️ EXTREM HOCH"
    elif row['Kurs_Status'] < 10:
        status_color = "off"
        label_suffix = "❄️ EXTREM TIEF"
    else:
        label_suffix = "(Normalbereich)"

    cols[i].metric(
        label=f"{row['Posten']} {label_suffix}",
        value=f"{row['Wert']} €",
        delta=f"{row['Kurs_Status']}% Auslastung",
        delta_color=status_color
    )

# 5. GESUNDHEITS-DASHBOARD (Wandsitz & Blutdruck)
# ---------------------------------------------------------
st.divider()
st.sidebar.header("🛡️ Gesundheits-Check")
st.sidebar.warning("""
**WANDSITZ-REMINDER:**
* Keine Pressatmung!
* Locker weiteratmen.
* Lächeln nicht vergessen.
""")

st.sidebar.info(f"""
**Ernährung heute:**
* Sprossen: ✅
* Rote Bete: ✅
* ACE-Hemmer Check: ✅
""")

# 6. TICKER-HINWEIS FÜR HUNG/BUL AKTIEN
# ---------------------------------------------------------
st.sidebar.write("---")
st.sidebar.write("**Stock-Suffixe:**")
st.sidebar.code("Ungarn: .BU\nBulgarien: .SO")

# 7. AUTOMATISCHER REFRESH DES BROWSERS (Optional)
# ---------------------------------------------------------
# Damit die App sich wirklich von selbst bewegt:
# st.empty()
# time.sleep(60)
# st.rerun()
