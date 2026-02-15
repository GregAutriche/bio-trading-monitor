import streamlit as st
import plotly.graph_objects as go
from datetime import datetime

# Seiteneinstellungen (Dark Mode wird durch Streamlit/Browser-Theming gesteuert)
st.set_page_config(layout="wide", page_title="Börsen-Wetter Dashboard")

# 1. HEADER: Datum und Uhrzeit (YYMMDD)
now = datetime.now()
timestamp_str = now.strftime("%y%m%d")
update_info = now.strftime("%A, %H:%M (Letztes Update)")

st.write(f"### {timestamp_str}")
st.write(f"**{update_info}**")
st.divider()

# 2. SEKTION 1: EUR/USD (Einzelne Zeile)
# Hier simulieren wir die Daten (Wert / Wetter / Action)
st.subheader("Währungs-Fokus")
col_eurusd = st.columns([1, 1, 1])
with col_eurusd[0]:
    st.metric(label="EUR/USD", value="1.0822", delta="+0.15%")
with col_eurusd[1]:
    st.write("☀️ **Wetter:** Heiter")
with col_eurusd[2]:
    st.write("🟢 **Action:** Halten / Bullisch")

st.divider()

# 3. SEKTION 2: Indizes untereinander
st.subheader("Markt-Indizes")

# Euro Stoxx 600 Zeile
col_stoxx = st.columns([1, 1, 1])
with col_stoxx[0]:
    st.metric(label="Euro Stoxx 600", value="490.10", delta="-0.5%", delta_color="inverse")
with col_stoxx[1]:
    st.write("🌧️ **Wetter:** Regen")
with col_stoxx[2]:
    st.write("🔴 **Action:** Absichern")

# S&P 1000 Zeile
col_sp = st.columns([1, 1, 1])
with col_sp[0]:
    st.metric(label="S&P 1000", value="5,230.55", delta="+1.2%")
with col_sp[1]:
    st.write("☀️ **Wetter:** Sonnig")
with col_sp[2]:
    st.write("🟢 **Action:** Kaufen")

st.divider()

# 4. SEKTION 3: GRAFIK (Candlestick Chart)
st.subheader("Markt-Grafik (Korrelation)")

# Beispielhafte Chart-Daten
fig = go.Figure(data=[go.Candlestick(
    x=['2024-05-18', '2024-05-19', '2024-05-20', '2024-05-21'],
    open=[100, 105, 102, 108],
    high=[110, 107, 105, 112],
    low=[98, 101, 99, 106],
    close=[105, 102, 104, 110]
)])

# Wetter-Icons als Annotationen in der Grafik hinzufügen
fig.add_annotation(x='2024-05-19', y=108, text="🌧️", showarrow=False, font=dict(size=20))
fig.add_annotation(x='2024-05-21', y=113, text="☀️", showarrow=False, font=dict(size=20))

fig.update_layout(
    template="plotly_dark",
    xaxis_rangeslider_visible=False,
    height=500,
    margin=dict(l=10, r=10, t=10, b=10)
)

st.plotly_chart(fig, use_container_width=True)

# 5. FUSSZEILE: Detail Info / Beschreibung
st.divider()
st.info("**Detail Info / Beschreibung:**\n\nDieses Dashboard zeigt die Korrelation zwischen globalen Wetterereignissen und der Marktvolatilität. Der S&P 1000 dient hierbei als Indikator für die US-Märkte, während der EUR/USD die währungsspezifische Dynamik abbildet.")
