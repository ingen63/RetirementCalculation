import json
import pytest
from src.data import Data
from src.property import Mortage, Property, PropertyManager
from src.util.config import Config


@pytest.fixture
def config():
    sample_data = {
    }
    config = Config()    
    config.loads(json.dumps(sample_data))
    config.initialize()
    config = Config().initialize()
    yield config
    
    
                      

def test_Amortization(config):
    # Arrange
    
    data = Data(config.getStartAge(), config.getEndAge())
    data.set_wealth(0.0)
    data.set_legal_pension(10)
    data.set_private_pension(10)

    start_age = config.getStartAge()
    property = Property(config, {"Name": "Owned House", "Price": 1000.0, "Buy": start_age-10, "Sell": start_age+10,  "FixCosts": 0.0})
    
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
    
    property.set_fix_costs(0.01*property.get_price())
    
    assert round(PropertyManager.max_mortage(property, data, config),2) == 1400
    
    data.set_wealth(10000)
    mortage.set_value(4000)
    property.set_worth(4000)
    assert round(PropertyManager.max_mortage(property, data, config),2) == 3200

    
        
    
    
    