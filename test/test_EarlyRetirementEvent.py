
import pytest
from config import Config
from data import Data
from event import ChangeValueEvent, EarlyRetirmentEvent

@pytest.fixture
def config():
    config = Config()
    return config

@pytest.fixture
def data():
    return Data(0,10)


def test_early_retirement_event(config, data):

    config.setValue(Config.PENSION_EARLYRETIREMENT, 60)
    event = EarlyRetirmentEvent(config.age2months(config.getEarlyRetirementAge()))
    change_event = ChangeValueEvent(event.get_month(),Config.MONEYFLOWS_EXTRA)
    data = Data(config.getStartMonth(), config.getEndMonth())

    config.setValue(Config.PENSION,{"Private": {
                "Capital": 1000,
                "LumpsumRatio": 0.5,
                "ConversionRate": 0.1, 
                "Contribution":  {"50": 5000.0},
                "Interest": {"50": 0.05}
                }
            })
    config.setValue(Config.MONEYFLOWS, {
                "Savings":  {"50": 500.0, "60": 0},
                "Spendings": {"50": 5000,"60" : 6000,  "65": 6500},
                "Extra": {"60": 60000.0}
            })
    
    data.set_pk_capital(config.getValue(Config.PENSION_PRIVATE_CAPITAL))
    
    # Call the before_method
    event.before_method(config, data)
    change_event.before_method(config, data)
    
    
    # Assert that extra and spending were set correctly
    assert data.get_extra() == 60000.0
    assert data.get_spending() == 6000
    assert data.get_lumpsum() == 0.5*1000.0
    
    
    event.after_method(config, data)
    change_event.after_method(config, data)
    assert data.get_extra() == 0.0
    assert data.get_spending() == 6000.0
    assert data.get_lumpsum() == 0.0
    
