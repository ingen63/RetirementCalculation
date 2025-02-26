
import pytest
from data import Data
from property import Mortage, Property, PropertyManager
from config import Config


@pytest.fixture
def config():
    config = Config()    
    yield config
    
    
                      

def test_Amortization(config):
    # Arrange
    
    data = Data(config.getStartAge(), config.getEndAge())
    data.set_wealth(0.0)
    data.set_legal_pension(10)
    data.set_private_pension(10)

    start_age = config.getStartAge()
    property = Property(Config({"Name": "Owned House", "Price": 1000.0, "Buy": start_age-10, "Sell": start_age+10, "FixCosts" : 0.0}))
    
    PropertyManager.add_property(property)
    
    property.set_mortage(None)
    
    assert round(PropertyManager.max_mortage(property, data, config),2) == 800
    
    mortage = Mortage()
    mortage.set_value(1000)
    property.set_mortage(mortage)
        
    assert round(PropertyManager.max_mortage(property, data, config),2) == 800
    
    
    property.set_worth(2000)
    mortage.set_value(1600)
    property.set_mortage(mortage)
        
    assert round(PropertyManager.max_mortage(property, data, config),2) == 1600
    
    mortage.set_value(2000)
    property.set_mortage(mortage)
        
    assert round(PropertyManager.max_mortage(property, data, config),2) == 1600
    
    property.set_fix_costs(None)
    
    assert round(PropertyManager.max_mortage(property, data, config),2) == 1400
    
    data.set_wealth(10000)
    mortage.set_value(4000)
    property.set_worth(4000)
    assert round(PropertyManager.max_mortage(property, data, config),2) == 3200
    
    data.set_wealth(0)
    data.set_legal_pension(0/Config.MONTHS)
    data.set_private_pension(100/Config.MONTHS)
    property.set_price(1000)
    property.set_worth(1000)
    
    max_mortaqe = PropertyManager.max_mortage(property, data, config)
    max_mortage_costs = max_mortaqe*Mortage.DEFAULT_AFFORDABILITY_MORTAGEINTEREST+property.get_price()*Mortage.DEFAULT_AFFORDABILITY_FIXCOSTS
    income = (data.get_private_pension()+data.get_legal_pension())*Config.MONTHS + data.get_wealth()*Mortage.DEFAULT_AFFORDABILITY_CAPITALCONTRIBUTION
    assert round(max_mortage_costs,2) == round(income*Mortage.DEFAULT_AFFORDABILITY_SUSTAINABILITY,2)
    
    data.set_wealth(200)
    property.set_mortage(None)
    max_mortaqe = PropertyManager.max_mortage(property, data, config)
    max_mortage_costs = max_mortaqe*Mortage.DEFAULT_AFFORDABILITY_MORTAGEINTEREST+property.get_price()*Mortage.DEFAULT_AFFORDABILITY_FIXCOSTS
    income = (data.get_private_pension()+data.get_legal_pension())*Config.MONTHS + data.get_wealth()*Mortage.DEFAULT_AFFORDABILITY_CAPITALCONTRIBUTION
    assert round(max_mortage_costs,2) == round(income*Mortage.DEFAULT_AFFORDABILITY_SUSTAINABILITY,2)
    
    
        
    
    
    