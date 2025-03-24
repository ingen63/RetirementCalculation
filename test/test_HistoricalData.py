import pytest
from historical import HistoricalData
from src.data import Data
from src.config import Config

HISTORY_RANGE = 100   

@pytest.fixture
def config():

    config = Config()
    config.setValue(Config.GENERAL_STARTAGE,50)
    config.setValue(Config.GENERAL_ENDAGE,50+25)
    config.setValue(Config.WEALTHMANAGEMENT_STOCKPERFORMANCE, 0.08)
    config.setValue(Config.WEALTHMANAGEMENT_BONDPERFORMANCE, 0.02)
    config.setValue(Config.WEALTHMANAGEMENT_INFLATION, 0.01)
    config.setValue(Config.WEALTHMANAGEMENT_PORTFOLIOBALANCE, 0.5)
    
    initialize_history()
    
    yield config
    
 
def initialize_history() :
    if HistoricalData.is_loaded() :
        return
    for i in range(0, HISTORY_RANGE): 
        HistoricalData.stocks.append(stock(i))
        HistoricalData.bonds.append(bond(i))
        HistoricalData.inflation.append(inflation(i))
        HistoricalData.years.append(1900+i)
        HistoricalData.index[1900+i] = i 
        HistoricalData.loaded = True   
 
def stock(i : int) -> float:
    return 2*i/1000.0

def bond(i : int) -> float:
    return 0.5*i/1000.0

def inflation(i : int) -> float:
    return 0.1*i/1000        
        
def test_loaded(config: Config) :
    assert HistoricalData.is_loaded() is True
    
def test_no_interpolation(config : Config) :
    cloned_config = config.clone()
    hd = HistoricalData(cloned_config)
    data = Data(cloned_config)
    
    hd.setValues(1900, cloned_config, data)
    
    i=0
    for age in range(data.get_start_age(),data.get_end_age()) :
        sp =  cloned_config.getActualValue(cloned_config.age2months(age), Config.WEALTHMANAGEMENT_STOCKPERFORMANCE) 
        bp =  cloned_config.getActualValue(cloned_config.age2months(age), Config.WEALTHMANAGEMENT_BONDPERFORMANCE) 
        ir =  cloned_config.getActualValue(cloned_config.age2months(age), Config.WEALTHMANAGEMENT_INFLATION) 
        assert sp == stock(i)
        assert bp == bond(i)
        assert ir == inflation(i)
        i += 1
        
    
    hd.setValues(1925, cloned_config, data)
    
    i=25
    for age in range(data.get_start_age(),data.get_end_age()) :
        sp =  cloned_config.getActualValue(cloned_config.age2months(age), Config.WEALTHMANAGEMENT_STOCKPERFORMANCE) 
        bp =  cloned_config.getActualValue(cloned_config.age2months(age), Config.WEALTHMANAGEMENT_BONDPERFORMANCE) 
        ir =  cloned_config.getActualValue(cloned_config.age2months(age), Config.WEALTHMANAGEMENT_INFLATION) 
        assert sp == stock(i)
        assert bp == bond(i)
        assert ir == inflation(i)
        i += 1
    
    
def test_fixed_interpolation(config : Config) :
    cloned_config = config.clone()
    cloned_config.setValue(Config.WEALTHMANAGEMENT_EXTRAPOLATION,Config.EXTRAPOLATION_FIXED)
    hd = HistoricalData(cloned_config)
    data = Data(cloned_config)
    
    hd.setValues(1980, cloned_config, data)
    lastValue = data.get_start_age() + (1900 + HISTORY_RANGE - 1980 - 1)
    
    i=80
    for age in range(data.get_start_age(),data.get_end_age()) :
        sp =  cloned_config.getActualValue(cloned_config.age2months(age), Config.WEALTHMANAGEMENT_STOCKPERFORMANCE) 
        bp =  cloned_config.getActualValue(cloned_config.age2months(age), Config.WEALTHMANAGEMENT_BONDPERFORMANCE) 
        ir =  cloned_config.getActualValue(cloned_config.age2months(age), Config.WEALTHMANAGEMENT_INFLATION) 
        if age <= lastValue :
            assert sp == stock(i)
            assert bp == bond(i)
            assert ir == inflation(i)
            i += 1
        else :
            assert sp == 0.08
            assert bp == 0.02
            assert ir == 0.01
    
def test_average_interpolation(config : Config) :
    cloned_config = config.clone()
    cloned_config.setValue(Config.WEALTHMANAGEMENT_EXTRAPOLATION,Config.EXTRAPOLATION_AVERAGE)
    hd = HistoricalData(cloned_config)
    data = Data(cloned_config)
    
    hd.setValues(1980, cloned_config, data)
    lastValue = data.get_start_age() + (1900 + HISTORY_RANGE - 1980 - 1)
    
    i=80
    stocks = HistoricalData.stocks[HISTORY_RANGE-hd.average_range:]
    
    sp_average = [0.169]
    for j in range(1, 50) :
        value = (sp_average[j-1]*hd.average_range-stocks[j-1]+sp_average[j-1])/hd.average_range
        sp_average.append(value)
        stocks.append(value)

    for age in range(data.get_start_age(),data.get_end_age()) :
        sp =  cloned_config.getActualValue(cloned_config.age2months(age), Config.WEALTHMANAGEMENT_STOCKPERFORMANCE) 
        bp =  cloned_config.getActualValue(cloned_config.age2months(age), Config.WEALTHMANAGEMENT_BONDPERFORMANCE) 
        ir =  cloned_config.getActualValue(cloned_config.age2months(age), Config.WEALTHMANAGEMENT_INFLATION) 
        if age <= lastValue :
            assert sp == stock(i)
            assert bp == bond(i)
            assert ir == inflation(i)   
        else :
            assert sp == sp_average[i-HISTORY_RANGE]
        i += 1  
    
    
def test_weighted_average_interpolation(config: Config):
    cloned_config = config.clone()
    cloned_config.setValue(Config.WEALTHMANAGEMENT_EXTRAPOLATION, Config.EXTRAPOLATION_WEIGHTED_AVERAGE)
    hd = HistoricalData(cloned_config)
    data = Data(cloned_config)

    hd.setValues(1980, cloned_config, data)
    lastValue = data.get_start_age() + (1900 + HISTORY_RANGE - 1980 - 1)

    i = 80
    stocks = HistoricalData.stocks[HISTORY_RANGE - hd.average_range :]

    sp_average = [1.16887180953608]
    for j in range(1, 50):
        value = sp_average[j - 1] ** hd.average_range
        value = (value / (1+stocks[j - 1]) * sp_average[j - 1]) ** (1/hd.average_range)
        sp_average.append(value)
        stocks.append(value)

    for age in range(data.get_start_age(), data.get_end_age()):
        sp = cloned_config.getActualValue(cloned_config.age2months(age), Config.WEALTHMANAGEMENT_STOCKPERFORMANCE)
        bp = cloned_config.getActualValue(cloned_config.age2months(age), Config.WEALTHMANAGEMENT_BONDPERFORMANCE)
        ir = cloned_config.getActualValue(cloned_config.age2months(age), Config.WEALTHMANAGEMENT_INFLATION)
        if age <= lastValue:
            assert sp == stock(i)
            assert bp == bond(i)
            assert ir == inflation(i)
        else:
            assert round(sp,10) == round(sp_average[i - HISTORY_RANGE] -1.0,10)
        i += 1
