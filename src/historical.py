import csv

class HistoricalData :
    
    years = []
    bonds = []
    stocks = []
    inflation = []
    
    @staticmethod
    def load(file : str) -> int :
        with open(file, 'r') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # skip header row
            for row in reader:
                HistoricalData.years.append(int(row[0]))
                HistoricalData.stocks.append(float(row[1]))
                HistoricalData.bonds.append(float(row[2]))
                HistoricalData.inflation.append(float(row[3]))
            
        return len(HistoricalData.years)
            
    @staticmethod
    def get_years(start : int, end : int) -> list[float]:
       return HistoricalData.years[start : end]
   
    @staticmethod
    def get_stocks(start : int, end : int) -> list[float]:
       return HistoricalData.stocks[start : end]
   
    @staticmethod
    def get_bonds(start : int, end : int) -> list[float]:
       return HistoricalData.bonds[start : end]
   
    @staticmethod
    def get_inflation(start : int, end : int) -> list[float]:
       return HistoricalData.inflation[start : end]
   
    @staticmethod
    def get_performance(balance : float, start : int, end : int) -> list[float]:
        performance = []
        for stock, bond in zip(HistoricalData.get_stocks(start, end), HistoricalData.get_bonds(start, end)):
            performance.append(stock * balance + bond * (1-balance))
        return performance
    @staticmethod
    def get_index(year : int) -> int :
        for index, value in enumerate(HistoricalData.years):
            if value == year :
                return index
        return None