
import pytest
from src.data import Data
from src.config import Config


@pytest.fixture
def config():

    config = Config()

    yield config


def test_set_value(config):

    config.setValue(Config.GENERAL_STARTMONTH, 13)    
    config.setValue(Config.GENERAL_STARTAGE, 50)
    config.setValue(Config.MONEYFLOWS_SPENDINGS, {50 : 500, 60 : 600})
    config.setValue(Config.PENSION_PRIVATE_CONTRIBUTION, {50 : 5000, 60 : 6000})
    
    data = Data(config.getStartAge(), config.getEndAge())
    

    assert data.get_spending() == 0.0
    actual = config.getActualValue(config.age2months(60), Config.MONEYFLOWS_SPENDINGS)
    data.set_value(Config.MONEYFLOWS_SPENDINGS,actual)
    assert data.get_spending() == 600
    
    
    assert data.get_pk_contribution() == 0.0
    actual = config.getActualValue(config.age2months(61), Config.PENSION_PRIVATE_CONTRIBUTION)
    data.set_value(Config.PENSION_PRIVATE_CONTRIBUTION,actual)
    assert data.get_pk_contribution() == 6000

    actual = config.getActualValue(config.age2months(59), Config.PENSION_PRIVATE_CONTRIBUTION)
    data.set_value(Config.PENSION_PRIVATE_CONTRIBUTION,actual)
    assert data.get_pk_contribution() == 5000
    

    actual = config.getActualValue(config.age2months(40), Config.PENSION_PRIVATE_CONTRIBUTION)
    data.set_value(Config.PENSION_PRIVATE_CONTRIBUTION,actual)
    assert data.get_pk_contribution() == 0.0
    
    
def test_time_to_sell(config) :
    
    data = Data(config.getStartAge(), config.getEndAge())
    data.set_threshold_months(10)

    assert data.time_to_sell() is False

    data.set_wealth(-1.0)
    assert data.time_to_sell() is True

    data.set_wealth(10)
    data.set_spending(1)

    assert data.time_to_sell() is False

    data.set_wealth(9.9)
    assert data.time_to_sell() is True
    
    
def test_inflation_correction(config) :
    
    data = Data(0,10)
    
    data.set_inflation(0.0)
    
    assert data.get_inflation_correction() == 1.0
    data.push_inflation()
    assert data.get_inflation_correction() == 1.0
    data.push_inflation()
    data.push_inflation()
    assert data.get_inflation_correction() == 1.0
    
    data = Data(0,10)
    data.set_inflation(0.1)
    data.push_inflation()
    assert data.get_inflation_correction() == 1.1
    data.push_inflation()
    data.push_inflation()
    assert round(data.get_inflation_correction(),6) == 1.331000
    
        
    data = Data(0,10)
    data.set_inflation(0.1)
    data.push_inflation()
    data.set_inflation(0.2)
    data.push_inflation()
    data.set_inflation(0.0)
    data.push_inflation()
    data.set_inflation(0.3)
    data.push_inflation()
    assert round(data.get_inflation_correction(),6) == 1.716
    
    
    
    
