
import pytest
from data import Data
from property import Property, PropertyManager
from config import Config


@pytest.fixture
def config():
    config = Config()    
    yield config
    
    
                      

def test_Amortization(config):
    # Arrange
    
    data = Data(config)
    data.set_wealth(0.0)
    data.set_legal_pension(10)
    data.set_private_pension(10)

    property = Property(Config({"Name": "House", "Price": 1000.0, "FixCosts" : 0.0, "Mortage" : {"Value": 800.0}}))
    
    PropertyManager.add_property(property)
    
    
    assert round(PropertyManager.max_mortage(property, data, config),2) == 800
    
    property.get_mortage().set_value(1000)
        
    assert round(PropertyManager.max_mortage(property, data, config),2) == 800
    
    
    property.set_price(2000)
    property.get_mortage().set_value(1600)
        
    assert round(PropertyManager.max_mortage(property, data, config),2) == 1600
    
    property.get_mortage().set_value(2000)
        
    assert round(PropertyManager.max_mortage(property, data, config),2) == 1600
    
    property.set_price(2400)
    property.set_fix_costs(property.get_price()*0.01/12)
    
    assert round(PropertyManager.max_mortage(property, data, config),2) == 1120
    
    data.set_wealth(2000)
    assert round(PropertyManager.max_mortage(property, data, config),2) == 1300
    
    data.set_wealth(4480)
    assert round(PropertyManager.max_mortage(property, data, config),2) == 1920
    
    data.set_wealth(60000)
    assert round(PropertyManager.max_mortage(property, data, config),2) == 1920
    

    
    
        
    
    
    