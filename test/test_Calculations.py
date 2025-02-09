import pytest
import json


from src.util.config import Config
from src.calculations import Calculations

    
    
    
@pytest.fixture
def config():
    sample_data = {
    "General": {
        "Age": 50.0,
        "Wealth": 100.00,  
        "IncomeTaxRate": 0.1,
        "CapitalTaxRate": 0.01
    },

    "Pension": {
        "Private": {
            "Capital": 1000.0,
            "Lumpsum": 0.5,
            "LumpsumTaxrate": 0.01,
            "ConversionRate": 0.042, 
            "Contribution": [
                {"50": 100.0},
                {"52": 200.0}
            ],
            "Interest": [
                {"50": 0.06}
            ]
        },
        "Legal": 1800.0
    },

    "Before": {
        "Monthly": {
            "Savings": [
                {"50": 10.0},
                {"52": 20.0}
            ]
        }
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
    config.initialize()
    yield config
    

def test_calculate_pre_retirement(config):
    calculations = Calculations()
    
    data = config.clone()

    __test_calculate_pre_retirement(calculations, data, 0, 100.0,1000.0)
    __test_calculate_pre_retirement(calculations, data, -1, 100.0,1000.0)
    data.setValue(Config.CALCULATION_SINGLE_PERFORMANCE, 0.0)
    data.setValue(Config.PENSION_PRIVATE_INTEREST, 0.0)
    __test_calculate_pre_retirement(calculations, data, 1, 112,1120)
    data = config.clone()
    
    data.setValue(Config.CALCULATION_SINGLE_PERFORMANCE, 0.0)
    data.setValue(Config.PENSION_PRIVATE_INTEREST, 0.01)
    __test_calculate_pre_retirement(calculations, data, 2, 124,1263.712)
    data = config.clone()
    
    data.setValue(Config.CALCULATION_SINGLE_PERFORMANCE, 0.1)
    data.setValue(Config.PENSION_PRIVATE_INTEREST, 0.01)
    __test_calculate_pre_retirement(calculations, data, 2, 147.5451268,1263.712)
   
    data = config.clone()
    __test_calculate_pre_retirement(calculations, data, 1+6/12, 134.79618026625,1187.2)
    
 
def __test_calculate_pre_retirement(calculations, data, years, expectedWealth, expectedPensionCapital):
     
 
    data.initialize()
    age = data.getValue(Config.GENERAL_AGE)
    calculations.calculate_pre_retirement_wealth(age+years, data)
    
    assert data.getValue(Config.GENERAL_WEALTH) == pytest.approx(expectedWealth, abs=1e-3, rel=1e-6)
    assert data.getValue(Config.PENSION_PRIVATE_CAPITAL) == pytest.approx(expectedPensionCapital, abs=1e-3, rel=1e-6)