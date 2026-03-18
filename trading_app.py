import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import os

# --- KLASSE ---
class DataAnalyzer:
    def __init__(self, file_path): # Korrigiert: __init__ statt init
        self.file_path = file_path
        self.df = None
        self.report_data = {}

    def load_and_clean(self):
        """Lädt die Excel-Datei und führt Basis-Bereinigungen durch."""
        try:
            self.df = pd.read_excel(self.file_path)
            self.df.columns = [c.strip().lower() for c in self.df.columns]
            if 'datum' in self.df.columns:
                self.df['datum'] = pd.to_datetime(self.df['datum'])
            return True
        except Exception as e:
            st.error(f"Fehler beim Laden: {e}")
            return False

    def analyze_trends(self):
        """Berechnet monatliche Trends."""
        if self.df is not None and 'datum' in self.df.columns:
            self.df['monat'] = self.df['datum'].dt.to_period('M').astype(str)
            # Metrik: Anzahl Einträge pro Monat
            self.report_data['monthly_trend'] = self.df.groupby('monat').size()
        
    def create_visualizations(self):
        """Generiert Diagramme für das Dashboard."""
        if 'monthly_trend' in self.report_data:
            fig, ax = plt.subplots(figsize=(10, 6))
            self.report_data['monthly_trend'].plot(kind='line', marker='o', ax=ax)
            ax.set_title('Monatlicher Trend')
            plt.grid(True)
            plt.xticks(rotation=45)
            # In Streamlit anzeigen statt speichern
            st.pyplot(fig)

    def generate_summary_report(self):
        """Erstellt eine Zusammenfassung."""
        if self.df is not None:
            return self.df.describe()

# --- STREAMLIT OBERFLÄCHE ---
st.title("Bio-Trading Monitor")

# Der Uploader verhindert den Absturz, wenn keine Datei da ist
uploaded_file = st.file_uploader("Bitte Excel-Datei (.xlsx) hochladen", type=['xlsx'])

if uploaded_file is not None:
    # Nur wenn eine Datei hochgeladen wurde, wird der Code ausgeführt
    analyzer = DataAnalyzer(uploaded_file)
    
    if analyzer.load_and_clean():
        analyzer.analyze_trends()
        
        st.subheader("Analyse der Trends")
        analyzer.create_visualizations()
        
        st.subheader("Statistische Zusammenfassung")
        st.write(analyzer.generate_summary_report())
else:
    st.info("Warte auf Datei-Upload...")
