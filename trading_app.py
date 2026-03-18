import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import numpy as np
from datetime import datetime, timedelta

# Konfiguration der Seite
st.set_page_config(page_title="Bio-Trading Monitor", layout="wide")

class DataAnalyzer:
    def __init__(self, data_source=None):
        """Initialisiert den Analyzer mit Datei oder Testdaten."""
        self.df = None
        self.report_data = {}
        
        if data_source is not None:
            self.load_from_file(data_source)
        else:
            self.generate_demo_data()

    def generate_demo_data(self):
        """Erstellt fiktive Daten für Testzwecke."""
        st.info("💡 Nutze Demo-Daten, da keine Datei hochgeladen wurde.")
        dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
        data = {
            'datum': dates,
            'wert': np.random.randint(10, 100, size=len(dates)),
            'kategorie': np.random.choice(['Bio', 'Konventionell'], size=len(dates))
        }
        self.df = pd.DataFrame(data)
        self.df.columns = [c.strip().lower() for c in self.df.columns]

    def load_from_file(self, file_path):
        """Lädt eine echte Excel-Datei."""
        try:
            self.df = pd.read_excel(file_path)
            self.df.columns = [c.strip().lower() for c in self.df.columns]
            if 'datum' in self.df.columns:
                self.df['datum'] = pd.to_datetime(self.df['datum'])
        except Exception as e:
            st.error(f"Fehler beim Laden: {e}")

    def analyze_trends(self):
        """Berechnet monatliche Trends."""
        if self.df is not None and 'datum' in self.df.columns:
            self.df = self.df.sort_values('datum')
            self.df['monat'] = self.df['datum'].dt.to_period('M').astype(str)
            # Wir nehmen hier die Summe der 'wert' Spalte oder zählen einfach Zeilen
            target_col = 'wert' if 'wert' in self.df.columns else self.df.columns[0]
            self.report_data['monthly_trend'] = self.df.groupby('monat')[target_col].count()
        
    def create_visualizations(self):
        """Erstellt das Diagramm."""
        if 'monthly_trend' in self.report_data:
            st.subheader("📈 Visualisierung: Monatlicher Trend")
            fig, ax = plt.subplots(figsize=(10, 5))
            
            # Das eigentliche Diagramm
            self.report_data['monthly_trend'].plot(kind='line', marker='o', ax=ax, color='#2a9d8f', linewidth=2)
            
            ax.set_title('Aktivität über die Zeit', fontsize=12)
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3)
            st.pyplot(fig)

# --- Hauptprogramm ---
def main():
    st.title("📊 Bio-Trading Monitor")
    
    # Sidebar für den Upload
    st.sidebar.header("Datenquelle")
    uploaded_file = st.sidebar.file_uploader("Excel hochladen", type=['xlsx'])

    # Analyzer starten (entweder mit Datei oder automatisch mit Demo-Daten)
    analyzer = DataAnalyzer(uploaded_file)
    
    analyzer.analyze_trends()
    
    # Layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        analyzer.create_visualizations()
    
    with col2:
        st.subheader("Details")
        st.write(analyzer.df.describe())

    with st.expander("Vorschau der Datentabelle"):
        st.dataframe(analyzer.df.head(20), use_container_width=True)

if __name__ == "__main__":
    main()
