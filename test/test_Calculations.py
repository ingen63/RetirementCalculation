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
      
    
def test_calculate_early_retirement(config):
    calculations = Calculations()
    age = config.getValue(Config.GENERAL_AGE)
    
    data = __setup_pension(config,100,1,0.1,0.0)
    __setup_calculate_early_retirement(data, age+1, 100.0, 1.0, 0.0, 0.0, 0.0)
    __test_calculate_early_retirement(calculations, data, 1, 200-12*1)
    __test_calculate_early_retirement(calculations, data, 1, 300-24*1)
    
    data = __setup_pension(config,240,0.5,0.1,0.0)
    __setup_calculate_early_retirement(data, age+1, 100.0, 1, 0.0, 0.0, 0.0)
    __test_calculate_early_retirement(calculations, data, 1, 220-12*1+12*1)
    
    data = __setup_pension(config,240,0.5,0.1,0.0)
    __setup_calculate_early_retirement(data, age+1, 100.0, 2, 100.0, 0.0, 0.0)
    __test_calculate_early_retirement(calculations, data, 1, 320-12*2+12*1)
    
    data = __setup_pension(config,240,0.5,0.1,0.0)
    __setup_calculate_early_retirement(data, age+1, 100.0, 2, 100.0, 0.0, 0.0)
    __test_calculate_early_retirement(calculations, data, 5, 320-5*12*2+5*12*1)
    
    data = __setup_pension(config,240,0.5,0.1,0.0)
    __setup_calculate_early_retirement(data, age+1, 120.0, 11, 0.0, 0.0, 0.0)
    __test_calculate_early_retirement(calculations, data, 3, 0)
    assert data.getSimulationTime() == 36
    
    data = __setup_pension(config,240,0.5,0.1,0.0)
    __setup_calculate_early_retirement(data, age+1, 120.0, 11, 0.0, 0.0, 0.0)
    __test_calculate_early_retirement(calculations, data, 5, 0)
    assert data.getSimulationTime() == 36
    
    data = __setup_pension(config,240,0.5,0.1,0.0)
    __setup_calculate_early_retirement(data, age+1, 120.0, 11, 0.0, 0.04, 0.01)
    __test_calculate_early_retirement(calculations, data, 5, 4.964358105212648)
    assert data.getSimulationTime() == 36

def __setup_calculate_early_retirement(data, age, wealth, spending, severance_pay,  performance, inflation):  
    data.setValue(Config.CALCULATION_PERFORMANCE, {0 : performance})
    data.setValue(Config.CALCULATION_INFLATION, {0 : inflation})
    data.convert_to_monthly_list(Config.CALCULATION_PERFORMANCE, True)
    data.convert_to_monthly_list(Config.CALCULATION_INFLATION, True)
    
    data.setValue(Config.GENERAL_WEALTH, wealth)
    data.setValue(Config.EARLY_AGE, age)
    data.setValue(Config.EARLY_SPENDING, spending)
    data.setValue(Config.EARLY_SEVERANCEPAY, severance_pay)
    data.convert_to_monthly_list(Config.EARLY_SPENDING, False, age)
    data.setSimulationTime(Utils.years_to_months(age-data.getValue(Config.GENERAL_AGE)))
    
    return data

def __test_calculate_early_retirement(calculations, data, years, expectedWealth):
     
    age = data.getValue(Config.EARLY_AGE)
    calculations.calculate_early_retirement(age, age+years, data)
    
    assert data.getValue(Config.GENERAL_WEALTH) == pytest.approx(expectedWealth, abs=1e-3, rel=1e-6)
    
def test_calculate_pension(config):
    
    data = __setup_pension(config, 1000, 1.0, 0.0, 0.0)
    __test_calculate_pension(data, 1000, 0)
    
    data = __setup_pension(config, 1200, 0.0, 0.1, 0.0)
    __test_calculate_pension(data, 0, 10)
    
    data = __setup_pension(config, 2400, 0.5, 0.1, 0.0)
    __test_calculate_pension(data, 1200, 10)
    
    data = __setup_pension(config, 2400, 0.5, 0.1, 0.0)
    __test_calculate_pension(data, 1200, 10)
    
    data = __setup_pension(config, 2400, 0.5, 0.1, 0.01)
    __test_calculate_pension(data, 1200-12, 10)
    
    data = __setup_pension(config, 0, 0, 0.0, 0.00)
    __test_calculate_pension(data, 0, 0)


    
    
def __setup_pension(config, capital, lumpsum_ratio,  conversion_rate, lumpsum_taxrate):
    data = config.clone().initialize()
    data.setValue(Config.PENSION_PRIVATE_CAPITAL, capital)
    data.setValue(Config.PENSION_PRIVATE_LUMPSUMRATIO, lumpsum_ratio)
    data.setValue(Config.PENSION_PRIVATE_LUMPSUMTAXRATE, lumpsum_taxrate)
    data.setValue(Config.PENSION_PRIVATE_CONVERSIONRATE, conversion_rate)
    return data
    

def __test_calculate_pension(data, lumpsum, pension):

    Calculations().calculate_pension(data)
    
    assert data.getValue(Config.PENSION_PRIVATE_LUMPSUM) == pytest.approx(lumpsum, abs=1e-3, rel=1e-6)
    assert data.getValue(Config.PENSION_PRIVATE_PENSION) == pytest.approx(pension, abs=1e-3, rel=1e-6)



