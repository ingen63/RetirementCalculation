
import pytest
from config import Config
from data import Data
from event import ChangeValueEvent, EarlyRetirmentEvent, EventHandler, MoneyFlowExtraEvent

@pytest.fixture
def config():
    config = Config()
    config.setValue(Config.GENERAL_STARTMONTH, 0)
    return config




def test_early_retirement_event(config):

    age = 60
    month = config.age2months(age)
    config.setValue(Config.PENSION_EARLYRETIREMENT, age)
    
    
    data = Data(config)

    config.setValue(Config.PENSION_PRIVATE,{
                "Capital": 1000,
                "LumpsumRatio": 0.5,
                "ConversionRate": 0.1, 
                "Contribution":  {"50": 5000.0},
                "Interest": {"50": 0.05}
            })
    config.setValue(Config.MONEYFLOWS, {
                "Savings":  {"50": 500.0, "60": 0},
                "Spendings": {"50": 5000,"60" : 6000,  "65": 6500},
                "Extra": {"60": 60000.0}
            })
    
    data.set_pk_capital(config.getValue(Config.PENSION_PRIVATE_CAPITAL))
    
    EventHandler.add_event(EarlyRetirmentEvent(month))
    EventHandler.add_event(MoneyFlowExtraEvent(month,60000.0))
    EventHandler.add_event(ChangeValueEvent(month, Config.MONEYFLOWS_SPENDINGS))
    
    EventHandler.init(config, data)
    # Call the before_method
    EventHandler.before(month, config, data)
    
    
    # Assert that extra and spending were set correctly
    assert data.get_extra() == 60000.0
    assert data.get_spending() == 6000
    assert data.get_lumpsum() == 0.5*1000.0
    
    EventHandler.after(month, config, data)
    
    assert data.get_extra() == 0.0
    assert data.get_spending() == 6000.0
    assert data.get_lumpsum() == 0.0
    
