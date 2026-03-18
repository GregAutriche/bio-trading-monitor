import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import os

# Konfiguration der Seite (Optional)
st.set_page_config(page_title="Bio-Trading Monitor", layout="wide")

class DataAnalyzer:
    def __init__(self, file_path):
        """Initialisiert den Analyzer mit dem Pfad zur Datei."""
        self.file_path = file_path
        self.df = None
        self.report_data = {}

    def load_and_clean(self):
        """Lädt die Excel-Datei und führt Basis-Bereinigungen durch."""
        try:
            # openpyxl muss in der requirements.txt stehen
            self.df = pd.read_excel(self.file_path)
            
            # Spaltennamen säubern (Leerzeichen weg, kleinschreiben)
            self.df.columns = [c.strip().lower() for c in self.df.columns]
            
            # Datum konvertieren, falls Spalte existiert
            if 'datum' in self.df.columns:
                self.df['datum'] = pd.to_datetime(self.df['datum'])
                self.df = self.df.sort_values('datum')
                return True
            else:
                st.warning("Spalte 'datum' wurde in der Datei nicht gefunden.")
                return True
        except Exception as e:
            st.error(f"Fehler beim Laden der Datei: {e}")
            return False

    def analyze_trends(self):
        """Berechnet monatliche Trends basierend auf der Datums-Spalte."""
        if self.df is not None and 'datum' in self.df.columns:
            # Monat extrahieren für Gruppierung
            self.df['monat'] = self.df['datum'].dt.to_period('M').astype(str)
            # Beispiel: Anzahl der Einträge pro Monat zählen
            self.report_data['monthly_trend'] = self.df.groupby('monat').size()
        
    def create_visualizations(self):
        """Generiert Diagramme und zeigt sie direkt in Streamlit an."""
        if 'monthly_trend' in self.report_data and not self.report_data['monthly_trend'].empty:
            st.subheader("Visualisierung: Monatlicher Trend")
            
            # --- Dein gewünschter Teil hier integriert ---
            fig, ax = plt.subplots(figsize=(10, 6))
            self.report_data['monthly_trend'].plot(kind='line', marker='o', ax=ax, color='#0077b6')
            
            # Optische Verfeinerungen
            ax.set_title('Anzahl der Vorgänge pro Monat', fontsize=14)
            ax.set_xlabel('Zeitraum (Monat)')
            ax.set_ylabel('Anzahl')
            plt.xticks(rotation=45)
            plt.grid(True, linestyle='--', alpha=0.7)
            plt.tight_layout()
            
            # In Streamlit anzeigen
            st.pyplot(fig)
            # ---------------------------------------------
        else:
            st.info("Keine Trend-Daten für die Grafik verfügbar.")

    def generate_summary_report(self):
        """Zeigt eine statistische Zusammenfassung in Streamlit."""
        if self.df is not None:
            st.subheader("Statistische Zusammenfassung")
            st.write(self.df.describe())

# --- Streamlit Hauptprogramm ---

def main():
    st.title("📊 Bio-Trading Monitor")
    st.markdown("Lade deine Excel-Datei hoch, um Trends und Statistiken zu visualisieren.")

    # Datei-Upload Interface
    uploaded_file = st.file_uploader("Excel-Datei auswählen", type=['xlsx'])

    if uploaded_file is not None:
        # 1. Instanz erstellen
        analyzer = DataAnalyzer(uploaded_file)
        
        # 2. Daten laden
        with st.spinner('Daten werden verarbeitet...'):
            if analyzer.load_and_clean():
                
                # 3. Analyse durchführen
                analyzer.analyze_trends()
                
                # 4. Ergebnisse anzeigen (Layout in Spalten)
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    analyzer.create_visualizations()
                
                with col2:
                    analyzer.generate_summary_report()
                
                # Optionale Datenansicht
                with st.expander("Rohdaten anzeigen"):
                    st.dataframe(analyzer.df)

if __name__ == "__main__":
    main()
