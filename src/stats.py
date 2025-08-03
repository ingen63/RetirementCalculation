
import copy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


class Stats :
   
   TEMPLATE = "Template"
   RESULT = "Result"

   def __init__(self, name : str = None) :
      self.data = []
      self.headers = []
      if (name is None) :
         self.name = Stats.TEMPLATE
      
   def clone(self, name : str)  :
      stats = copy.deepcopy(self)
      stats.name = name
      return stats
                 

   def set_headers(self, headers : list[str]) :
      self.headers = headers
      self.headers.append(Stats.RESULT)
   

   def add_row(self, columns : list[float]) :
      columns = columns.copy()
      columns.append(None)
      if len(columns) != len(self.headers) :
         raise IndexError(f"Length of input ({len(columns)}) and doesnt not match given length of header ({len(self.headers)})")
      
      self.data.append(columns)
      
   def update_result(self, index : int,result : float) :
      row = self.data[index]
      row[-1] = result


   def show_statistics(self) :
      
      # Erstellen eines DataFrames für eine einfache Analyse
      df = pd.DataFrame(self.data, columns=self.headers)

      # ----------------------------
      # 1. Basisstatistiken
      # ----------------------------
      print("Zusammenfassung der Ergebnisse:")
      print(df[Stats.RESULT].describe())

      # ----------------------------
      # 2. Histogramm der Ergebnisse
      # ----------------------------
      plt.figure(figsize=(10, 6))
      sns.histplot(df[Stats.RESULT], bins=30, kde=True, color="steelblue")
      plt.title("Histogramm der Ergebnisse")
      plt.xlabel("Ergebnis")
      plt.ylabel("Häufigkeit")
      plt.show()

      # ----------------------------
      # 3. Gruppierte Statistiken
      # ----------------------------
      # Beispiel: Durchschnittlicher Ergebniswert für jeden a-Wert
      grouped_by_a = df.groupby(self.headers[0])[Stats.RESULT].mean()
      print("\nDurchschnittliche Ergebnisse nach Parameter a:")
      print(grouped_by_a)

      # ----------------------------
      # 4. Korrelationen analysieren
      # ----------------------------
      correlation_matrix = df[self.headers].corr()
      print("\nKorrelationsmatrix:")
      print(correlation_matrix)

      plt.figure(figsize=(8, 6))
      sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", fmt=".2f")
      plt.title("Korrelationen zwischen Parametern und Ergebnissen")
      plt.show()

      # ----------------------------
      # 5. Kumulative Verteilungsfunktion (CDF)
      # ----------------------------
      # Sortieren der Ergebnisse und Berechnung der kumulativen Wahrscheinlichkeiten
      sorted_results = np.sort(df[Stats.RESULT])
      cdf = np.arange(1, len(sorted_results) + 1) / len(sorted_results)

      plt.figure(figsize=(10, 6))
      plt.plot(sorted_results, cdf, marker="o", linestyle="--", color="darkred")
      plt.title("Kumulative Verteilungsfunktion (CDF)")
      plt.xlabel("Ergebnis")
      plt.ylabel("Kumulative Wahrscheinlichkeit")
      plt.grid(True)
      plt.show()


class StatsHandler :
   stats_list = {Stats.TEMPLATE : Stats()}
   
   @staticmethod
   def get_stats(name : str) -> Stats:   
      stats =  StatsHandler.stats_list.get(name)
      if stats is None  :
         stats = StatsHandler.add_stats(name)
      return stats
   
   @staticmethod
   def add_stats(name : str) -> Stats :
      template = StatsHandler.stats_list[Stats.TEMPLATE]
      stats = template.clone(name)
      StatsHandler.stats_list[stats.name] = stats
      return stats
   
   @staticmethod
   def set_headers(headers : list[str]) :
      for value in StatsHandler.stats_list.values() :
         value.set_headers (headers)
     
   @staticmethod
   def add_row(columns : list[float]) :
      for value in StatsHandler.stats_list.values() :
         value.add_row(columns)      
   
   @staticmethod      
   def update_result(name : str, index : int, result : float) :
      StatsHandler.get_stats(name).update_result(index, result)
      
   @staticmethod
   def shows_statistics() :
      for value in StatsHandler.stats_list.values() :
         value.show_statistics()
      
      

''' Was macht der Code?

1. **Parameter und Simulation**:  
   - Wir definieren die Bereiche für \(a\), \(b\) und \(c\) und iterieren über jede Kombination.  
   - Für jede Parameterkombination wird ein zufälliges Ergebnis (zwischen 60 und 100) erzeugt.

2. **Basisstatistiken**:  
   - Mit `df["Result"].describe()` erhalten Sie wichtige Kennzahlen wie Mittelwert, Median, Standardabweichung etc.

3. **Histogramm**:  
   - Das Histogramm (mit Überlagerung eines Kernel-Density-Estimates) zeigt Ihnen, wie sich die Ergebnisse verteilen.

4. **Gruppierungsanalyse**:  
   - Hier wird der Durchschnitt der Ergebnisse für verschiedene \(a\)-Werte berechnet. Ähnliche Gruppierungen können auch für \(b\) und \(c\) durchgeführt werden.

5. **Korrelation**:  
   - Die Korrelationsmatrix und die dazugehörige Heatmap geben Aufschluss darüber, wie stark die Parameter \(a\), \(b\), \(c\) mit den Ergebnissen zusammenhängen.

6. **Kumulative Verteilungsfunktion (CDF)**:  
   - Die CDF zeigt, welcher Anteil der Ergebnisse unter einem bestimmten Wert liegt, was Ihnen hilft, Grenzwerte oder Schwellen zu erkennen.

---

Falls Sie noch weitere Analysen, Visualisierungen oder Anpassungen zur Auswertung Ihrer Simulationsergebnisse wünschen, können wir den Code gezielt erweitern. Zum Beispiel könnten Sie Scatterplots für spezifische Parameterkombinationen oder Boxplots für Gruppen erstellen. Welche zusätzlichen Analysen würden Sie interessant finden?

'''