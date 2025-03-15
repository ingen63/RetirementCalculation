import pytest

from data import Data
from event import EventHandler, SellPropertyEvent
from property import Property, PropertyManager
from config import Config



@pytest.fixture
def config():
    return Config()
    
   
                      

def test_SellPropertyEvent(config : Config):
    # Arrange
    
    
    PropertyManager.add_property(Property(Config({"Name": "Owned House", "SellAge" : 50,  "Worth": 150000, "Status" : "Owned"})))  
    PropertyManager.add_property(Property(Config({"Name": "Owned House2A", "SellAge" : 52, "Price": 300000, "Status" : "Owned"})))
    PropertyManager.add_property(Property(Config({"Name": "Owned House2B", "SellAge" : 52, "Price": 450000, "Status" : "Owned"})))   
    PropertyManager.add_property(Property(Config({"Name": "Owned House3", "SellAge" : 54, "Price":  600000, "Status" : "Owned"})))
    
    data = Data(config.getStartAge(), config.getEndAge())
    
    properties = PropertyManager.get_properties(Property.OWNED)
   
    for property in properties:
        EventHandler.add_event(SellPropertyEvent(config.age2months(property.get_sell_age()), property))
                              

    EventHandler.before(config.age2months(50), config, data) 
    assert data.get_wealth() == 150000.0
    
    EventHandler.before(config.age2months(50), config, data)
    assert data.get_wealth() == 150000.0
    
    EventHandler.before(config.age2months(52), config, data)
    assert data.get_wealth() == 150000.0 + 300000.0 + 450000.0
    
    EventHandler.before(config.age2months(54), config, data)
    assert data.get_wealth() == 150000.0 + 300000.0 + 450000.0 + 600000.0


   
   
    

    
    
    
    
    

    
