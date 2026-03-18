import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

class DataAnalyzer:
    def init(self, file_path):
        self.file_path = file_path
        self.df = None
        self.report_data = {}

    def load_and_clean(self):
        """Lädt die Excel-Datei und führt Basis-Bereinigungen durch."""
        self.df = pd.read_excel(self.file_path)
        # Beispiel: Spaltennamen normalisieren und Zeitstempel konvertieren
        self.df.columns = [c.strip().lower() for c in self.df.columns]
        if 'datum' in self.df.columns:
            self.df['datum'] = pd.to_datetime(self.df['datum'])
        print("Daten erfolgreich geladen und bereinigt.")

    def analyze_trends(self):
        """Berechnet monatliche Trends."""
        if 'datum' in self.df.columns:
            self.df['monat'] = self.df['datum'].dt.to_period('M')
            # Beispiel-Metrik: Summe pro Monat (muss an deine Spalten angepasst werden)
            self.report_data['monthly_trend'] = self.df.groupby('monat').size()
        
    def create_visualizations(self, output_folder='plots'):
        """Generiert Diagramme für das Dashboard."""
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
            
        plt.figure(figsize=(10, 6))
        self.report_data['monthly_trend'].plot(kind='line', marker='o')
        plt.title('Monatlicher Trend')
        plt.grid(True)
        plot_path = f"{output_folder}/trend_chart.png"
        plt.savefig(plot_path)
        plt.close()
        return plot_path

    def generate_summary_report(self):
        """Erstellt eine einfache Text- oder HTML-Zusammenfassung."""
        summary = self.df.describe()
        print("Analyse abgeschlossen. Zusammenfassung erstellt.")
        return summary

# --- Ausführung ---
# analyzer = DataAnalyzer('deine_datei.xlsx')
# analyzer.load_and_clean()
# analyzer.analyze_trends()
# analyzer.create_visualizations()
