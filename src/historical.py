import csv

from config import Config
from data import Data

class HistoricalData :
    
    loaded = False
    index = {}
    years = []
    bonds = []
    stocks = []
    inflation = []
    
    
    def __init__(self, config : Config):
        self.extrapolation = config.getValue(Config.WEALTHMANAGEMENT_EXTRAPOLATION, Config.DEFAULT_WEALTHMANAGEMENT_EXTRAPOLATION)
        self.average_range = config.getValue(Config.WEALTHMANAGEMENT_AVERAGERANGE, Config.DEFAULT_WEALTHMANAGEMENT_AVERAGERANGE)
        self.fixed_bond_performance = config.getValue(Config.WEALTHMANAGEMENT_BONDPERFORMANCE,0.0)
        self.fixed_stock_performance = config.getValue(Config.WEALTHMANAGEMENT_STOCKPERFORMANCE,0.0)
        self.fixed_inflation_rate = config.getValue(Config.WEALTHMANAGEMENT_INFLATION,0.0)    
    
    @staticmethod
    def load(file : str) -> int :
        with open(file, 'r') as csvfile:
            reader = csv.reader(csvfile)
            i = 0
            next(reader)  # skip header row
            for row in reader:
                HistoricalData.years.append(int(row[0]))
                HistoricalData.index[int(row[0])] = i
                i += 1
                HistoricalData.stocks.append(float(row[1]))
                HistoricalData.bonds.append(float(row[2]))
                HistoricalData.inflation.append(float(row[3]))
          
        HistoricalData.loaded = True    
        return len(HistoricalData.years)
    
    @staticmethod 
    def is_loaded() -> bool : 
        return HistoricalData.loaded
     
    def setValues(self, year : int, config : Config, data : Data) :
        
        start_year = year
        period =  data.get_end_age() - data.get_start_age()
        end_year = start_year + period
        stock_performance = self.get_stock_performance(start_year, end_year)
        bond_performance = self.get_bond_performance(start_year, end_year)
        inflation_rates =self.get_inflation_rates(start_year, end_year)
        
        start_age = config.month2age(1)
        config.setValue(Config.WEALTHMANAGEMENT_STOCKPERFORMANCE, self.to_dict(start_age,stock_performance ))
        config.setValue(Config.WEALTHMANAGEMENT_BONDPERFORMANCE, self.to_dict(start_age, bond_performance))
        config.setValue(Config.WEALTHMANAGEMENT_INFLATION, self.to_dict(start_age, inflation_rates))
        
           
    def to_dict(self, start_age : float, data : list) -> dict :
        values = {}
        for i in range(0, len(data)) :
            values[start_age+i] = data[i]  
        return values
            
            

    def get_years(start : int, end : int) -> list[float]:
       return HistoricalData.years[start : end]
   

    def get_stock_performance(self, start_year : int, end_year : int) -> list[float]:
        if end_year <= HistoricalData.years[-1] : 
            return HistoricalData.stocks[self.get_index(start_year) : self.get_index(end_year)]
        else :
            return self.extrapolate(start_year, end_year, HistoricalData.stocks, self.fixed_stock_performance)
   

    def get_bond_performance(self, start_year : int, end_year : int) -> list[float]:
        if end_year <= HistoricalData.years[-1] : 
            return HistoricalData.bonds[self.get_index(start_year) : self.get_index(end_year)]
        else :
            return self.extrapolate(start_year, end_year, HistoricalData.bonds, self.fixed_bond_performance)

    def get_inflation_rates(self, start_year : int, end_year : int) -> list[float]:
        if end_year <= HistoricalData.years[-1] : 
            return HistoricalData.inflation[self.get_index(start_year) : self.get_index(end_year)]
        else :
            return self.extrapolate(start_year, end_year, HistoricalData.inflation, self.fixed_inflation_rate)


    def get_index(self, year : int) -> int :
        if HistoricalData.years[0] > year :
            raise IndexError(f"Historical data start with year {HistoricalData.years[0]} year: {year} is out of range")
        if HistoricalData.years[-1] < year :
            raise IndexError(f"Historical data end with year {HistoricalData.years[-1]} year: {year} is out of range")
        return HistoricalData.index[year]
    
    
    def extrapolate(self, start_year :int, end_year : int, data : list[float], value : float) -> list[float] :

        historical_data = data[self.get_index(start_year) : -1 ]
        
        if self.extrapolation == "Fixed" :
            return historical_data + self.extrapolate_values(end_year, [value] * self.average_range, self.fixed)
        elif self.extrapolation == "Weighted Average" : 
            return historical_data + self.extrapolate_values(end_year, data, self.weighted_average)
        elif self.extrapolation == "Average" :
             return historical_data + self.extrapolate_values(end_year, data, self.average)
        else :
            raise ValueError(f"Unsupported extrapolation method: {self.extrapolation}")
        
        
    def extrapolate_values(self, end_year :int, data : list[float], extrapolation_method)  -> list[float]:  
        values = []
        
        start_year = HistoricalData.years[-1]
        end_index = int(end_year - start_year)
        
        end = len(data)
        data = data[end - self.average_range : end]
        for i in range(0, end_index+1) :
            value = extrapolation_method(data)
            values.append(value)
            del data[0]
            data.append(value)
            
        return values
        
         
       
    def fixed(self, values : list[float]) -> float :  
        return values[0]
       
    def average(self, values : list[float]) -> float :
        value = 0.0
        for i in range(0, len(values)):
            value += values[i]
        return value/len(values)
    
           
    def weighted_average(self, values : list) -> float :
        value = 1.0
        for i in range(0, len(values)):
            value *= (1.0+values[i])
        return value**(1.0/len(values)) - 1.0
            
            
    