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
    
    properties = PropertyManager.get_owned_properties(True)
   
    for property in properties:
        EventHandler.add_event(SellPropertyEvent(property.get_sell_age(), property))
                              
    wealth = 0 
    i=1 
    for month in range(data.get_start_simulation_month()-10, data.get_start_simulation_month()+5*12) :
        events = EventHandler.get_events(month)
        for event in events :
            if isinstance(event, SellPropertyEvent) :
                wealth += i*150000
                i += 1
            event.before_method(config, data)
            event.after_method(config, data)
            assert data.get_wealth() == wealth

    assert data.get_wealth() == 150000.0 + 300000.0 + 450000.0 + 600000.0
   
   
    

    
    
    
    
    

    
