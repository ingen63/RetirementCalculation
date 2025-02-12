import logging
import pytest
import json


from src.util.config import Config
from src.calculations import Calculations
from src.util.utils import Utils

    
    
    
@pytest.fixture
def config():
    sample_data = {
    "General": {
        "Age": 50.0,
        "Wealth": 100.00, 
        "Start" : 2020,
        "End" : 2090,
        "IncomeTaxRate": 0.0,
        "CapitalTaxRate": 0.0
    },

    "Pension": {
        "Private": {
            "Capital": 1000.0,
            "Lumpsum": 0.5,
            "LumpsumTaxrate": 0.01,
            "ConversionRate": 0.042, 
            "Contribution":  { 50 : 10.0, 52 : 20.0},
            "Interest":  { 50: 0.06}
        },
        "Legal": 1800.0
    },
    
    "Before": {
            "Savings":  { 50 : 1.0, 52 : 2.0}
    },
    
    "Calculation": {
        "Method": "Single",
        "Single": {
            "Max": 100,
            "Inflation": 0.0,
            "Performance": 0.1             
        }
     }
    }

    config = Config()
    config.loads(json.dumps(sample_data))

    yield config
     



CAPITAL = Config.PENSION_PRIVATE_CAPITAL 
RATIO = Config.PENSION_PRIVATE_LUMPSUMRATIO
CONVERSION_RATE = Config.PENSION_PRIVATE_CONVERSIONRATE
LUMPSUM_TAX =  Config.PENSION_PRIVATE_LUMPSUMTAXRATE

TEST_PENSION_SETUP = [CAPITAL, RATIO, CONVERSION_RATE, LUMPSUM_TAX]

START_YEAR = Config.GENERAL_START
END_YEAR = Config.GENERAL_END
WEALTH = Config.GENERAL_WEALTH
SEVERANCE_PAY = Config.EARLY_SEVERANCEPAY
EARLY_SPENDING = Config.EARLY_SPENDING
LEGAL_SPENDING = Config.LEGAL_SPENDING
PERFORMANCE = Config.CALCULATION_SINGLE_PERFORMANCE
INFLATION =  Config.CALCULATION_SINGLE_INFLATION

TEST_RETIREMENT_SETUP = [START_YEAR, END_YEAR, WEALTH, SEVERANCE_PAY, EARLY_SPENDING, LEGAL_SPENDING, PERFORMANCE, INFLATION]

def test_calculate_pre_retirement(config):
    calculations = Calculations()
    
    data = __setup_calculate_pre_retirement(config,0.0,0.0)
    __test_calculate_pre_retirement(calculations, data, 0, 100.0,1000.0)

    data = __setup_calculate_pre_retirement(config,0.0,0.0)
    __test_calculate_pre_retirement(calculations, data, -1, 100.0,1000.0)
    
    data = __setup_calculate_pre_retirement(config,0.0,0.0)
    __test_calculate_pre_retirement(calculations, data, 1, 112,1120)
    

    data = __setup_calculate_pre_retirement(config,0.0,0.01)
    __test_calculate_pre_retirement(calculations, data, 2, 124,1263.712)

    
    data = __setup_calculate_pre_retirement(config,0.1,0.01)   
    __test_calculate_pre_retirement(calculations, data, 2, 147.5451268,1263.712)
   
    data = __setup_calculate_pre_retirement(config,0.1,0.01)   
    __test_calculate_pre_retirement(calculations, data, 1.5, 134.79618026625,1191.2)
    
    data = __setup_calculate_pre_retirement(config,0.1,0.01)   
    __test_calculate_pre_retirement(calculations, data, 3, 187.580712798857,1518.74912)

def __setup_calculate_pre_retirement(config, performance, interest):
    
    data = config.clone().initialize()    
    data.setValue(Config.CALCULATION_PERFORMANCE, {0 : performance})
    data.setValue(Config.PENSION_PRIVATE_INTEREST, {0 : interest})
    data.convert_to_monthly_list(Config.CALCULATION_PERFORMANCE, True)
    data.convert_to_monthly_list(Config.PENSION_PRIVATE_INTEREST, False)
    return data
    
 
def __test_calculate_pre_retirement(calculations, data, years, expectedWealth, expectedPensionCapital):
     
    age = data.getValue(Config.GENERAL_AGE)
    calculations.calculate_pre_retirement(age, age+years, data)
    
    assert data.getValue(Config.GENERAL_WEALTH) == pytest.approx(expectedWealth, abs=1e-3, rel=1e-6)
    assert data.getValue(Config.PENSION_PRIVATE_CAPITAL) == pytest.approx(expectedPensionCapital, abs=1e-3, rel=1e-6)
      
    
def test_calculate_retirement(config):
    calculations = Calculations()
    config.setValue(Config.EARLY_AGE, 60)
    early_retirement_age = config.getEarlyRetirementAge()
    legal_retirement_age = config.getLegalRetirementAge()
    
    data = config.clone().initialize()
    __setup(data, TEST_PENSION_SETUP, {CAPITAL : 100, RATIO : 1.0, CONVERSION_RATE: 0.1}) 
    __setup_calculate_retirement(data, TEST_RETIREMENT_SETUP,  {START_YEAR : early_retirement_age, END_YEAR : early_retirement_age +2, WEALTH : 100.0,  EARLY_SPENDING : 1.0} )
    __test_calculate_retirement(calculations, data, early_retirement_age, 1, 200-12*1)
    __test_calculate_retirement(calculations, data, early_retirement_age+1, 1, 200-24*1)
    

    data = config.clone().initialize()
    __setup(data, TEST_PENSION_SETUP, {CAPITAL : 240, RATIO : 0.5, CONVERSION_RATE: 0.1}) 
    __setup_calculate_retirement(data, TEST_RETIREMENT_SETUP,  {START_YEAR : early_retirement_age, END_YEAR : early_retirement_age +1, WEALTH : 100.0,  EARLY_SPENDING : 1.0} )
    __test_calculate_retirement(calculations, data, early_retirement_age, 1, 220-12*1+12*1)
    
    data = config.clone().initialize()
    __setup(data, TEST_PENSION_SETUP, {CAPITAL : 240, RATIO : 0.5, CONVERSION_RATE: 0.1}) 
    __setup_calculate_retirement(data, TEST_RETIREMENT_SETUP,  {START_YEAR : early_retirement_age -1, END_YEAR : early_retirement_age +2, WEALTH : 100.0,  EARLY_SPENDING : 2.0} )
    __test_calculate_retirement(calculations, data, early_retirement_age-1 , 2, 220-12*2+12*1)
    
    data = config.clone().initialize()
    __setup(data, TEST_PENSION_SETUP, {CAPITAL : 240, RATIO : 0.5, CONVERSION_RATE: 0.1}) 
    __setup_calculate_retirement(data, TEST_RETIREMENT_SETUP,  {START_YEAR : early_retirement_age, END_YEAR : early_retirement_age +5, WEALTH : 100.0,  EARLY_SPENDING : 2.0} )
    __test_calculate_retirement(calculations, data, early_retirement_age, 5, 220-5*12*2+5*12*1)
    
    data = config.clone().initialize()
    __setup(data, TEST_PENSION_SETUP, {CAPITAL : 240, RATIO : 0.5, CONVERSION_RATE: 0.1}) 
    __setup_calculate_retirement(data, TEST_RETIREMENT_SETUP,  {START_YEAR : early_retirement_age, END_YEAR : early_retirement_age + 20, WEALTH : 120.0,  EARLY_SPENDING : 11.0} )
    __test_calculate_retirement(calculations, data, early_retirement_age, 3, 0)
    assert data.getSimulationTime() == 120+24
    
    data = config.clone().initialize()
    __setup(data, TEST_PENSION_SETUP, {CAPITAL : 240, RATIO : 0.5, CONVERSION_RATE: 0.1}) 
    __setup_calculate_retirement(data, TEST_RETIREMENT_SETUP,  {START_YEAR : early_retirement_age, END_YEAR : early_retirement_age + 20, WEALTH : 120.0,  EARLY_SPENDING : 11.0} )
    __test_calculate_retirement(calculations, data, early_retirement_age, 5, 0)
    assert data.getSimulationTime() == 120+24
    
    data = config.clone().initialize()
    __setup(data, TEST_PENSION_SETUP, {CAPITAL : 240, RATIO : 0.5, CONVERSION_RATE: 0.1})  
    __setup_calculate_retirement(data, TEST_RETIREMENT_SETUP,  {START_YEAR : early_retirement_age, END_YEAR : early_retirement_age + 1, WEALTH : 120.0,  EARLY_SPENDING : 11.0, PERFORMANCE : 0.04, INFLATION : 0.01} )
    __test_calculate_retirement(calculations, data, early_retirement_age, 5, 88.32919)
    assert data.getSimulationTime() == 120+13


def __setup_calculate_retirement(data : Config, keys : list[str],  input : dict):  
    
    __setup(data, keys, input)
    
    data.setValue(Config.CALCULATION_PERFORMANCE,data.convert_to_monthly_list(Config.CALCULATION_SINGLE_PERFORMANCE, True))
    data.setValue(Config.CALCULATION_INFLATION,data.convert_to_monthly_list(Config.CALCULATION_SINGLE_INFLATION, False))
    
    data.setSimulationTime(Utils.years_to_months(data.offset( Utils.getValue(input, START_YEAR))))
    data.setValue(Config.GENERAL_MAXPERIOD, Utils.getValue(input, END_YEAR))
    
    return data

def __test_calculate_retirement(calculations : Calculations, data : Config, start_year : float, period : float,  expectedWealth : float):
      
    calculations.calculate_retirement(start_year, start_year + period, data)
    
    assert data.getValue(Config.GENERAL_WEALTH) == pytest.approx(expectedWealth, abs=1e-3, rel=1e-6)
   
     
def test_calculate_pension(config):
    
    data = config.clone().initialize()
    __setup(data, TEST_PENSION_SETUP, {CAPITAL : 1000, RATIO: 1.0})
    __test_calculate_pension(data, 1000, 0)
    
    data = config.clone().initialize()
    __setup(data,TEST_PENSION_SETUP,  {CAPITAL : 1200, CONVERSION_RATE:  0.1} )
    __test_calculate_pension(data, 0, 10)
    
    data = config.clone().initialize()
    __setup(data,TEST_PENSION_SETUP,  {CAPITAL : 2400, RATIO : 0.5, CONVERSION_RATE:  0.1})
    __test_calculate_pension(data, 1200, 10)
    
    data = config.clone().initialize()
    __setup(data,TEST_PENSION_SETUP,  {CAPITAL : 2400, RATIO : 0.5, CONVERSION_RATE:  0.1, LUMPSUM_TAX : 0.01} )
    __test_calculate_pension(data, 1200-12, 10)
    
    data = config.clone().initialize()  
    __setup(data,TEST_PENSION_SETUP,  {})
    __test_calculate_pension(data, 0, 0)


    
    
def __setup(data, keys : list[str], input : dict):
    for key in keys :
        data.setValue(key, Utils.getValue(input, key))
    

def __test_calculate_pension(data, lumpsum, pension):

    Calculations().calculate_pension(data)
    
    assert data.getValue(Config.PENSION_PRIVATE_LUMPSUM) == pytest.approx(lumpsum, abs=1e-3, rel=1e-6)
    assert data.getValue(Config.PENSION_PRIVATE_PENSION) == pytest.approx(pension, abs=1e-3, rel=1e-6)
    
    




