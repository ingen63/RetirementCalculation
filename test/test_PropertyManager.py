import json
import pytest
from src.data import Data
from src.property import Property, PropertyManager
from src.config import Config


@pytest.fixture
def config():
    PropertyManager.reset()
    config = Config()
    yield config
    
    
def test_sort(config : Config) :
    
    property0 = Property(Config({Property.BUYAGE : 50, Property.PRICE : 100}))
    property1 = Property(Config({Property.BUYAGE : 52, Property.PRICE : 90}))
    property2 = Property(Config({Property.BUYAGE : 54, Property.PRICE : 80}))
    
    PropertyManager.add_property(property0)
    PropertyManager.add_property(property1)
    PropertyManager.add_property(property2)
    
    sorted = PropertyManager.get_properties(Property.PLANNED)
    assert sorted[0].get_buy_age() == 50
    assert sorted[1].get_buy_age() == 52
    assert sorted[2].get_buy_age() == 54
    
    sorted = PropertyManager.get_properties(Property.PLANNED, False)
    assert sorted[0].get_buy_age() == 50
    assert sorted[1].get_buy_age() == 52
    assert sorted[2].get_buy_age() == 54
    
    property1.set_buy_age(50)
    property2.set_buy_age(50)
    
    sorted = PropertyManager.get_properties(Property.PLANNED)
    assert sorted[0].get_price() == 80
    assert sorted[1].get_price() == 90
    assert sorted[2].get_price() == 100
    
    sorted = PropertyManager.get_properties(Property.PLANNED, False)
    assert sorted[0].get_price() == 100
    assert sorted[1].get_price() == 90
    assert sorted[2].get_price() == 80
                      

def test_PropertyManager(config : Config):
    # Arrange

    start_age = config.getStartAge()
    property0 = Property(Config({"Name": "Owned House", "Worth": 100000, "Status" : "Owned"}))

    # Act
    PropertyManager.add_property(property0)

    # Assert
    # Assert
    assert len(PropertyManager.get_properties(Property.OWNED)) == 1
    assert len(PropertyManager.get_properties(Property.PLANNED)) == 0
    assert len(PropertyManager.get_properties(Property.SOLD)) == 0
    assert PropertyManager.get_properties(Property.OWNED)[0] == property0
    
    property1 = Property(Config({"Name": "Owned House", "Worth": 200000, "Status" : "Owned"}))

    # Act
    PropertyManager.add_property(property1)

    # Assert
    assert len(PropertyManager.get_properties(Property.OWNED)) == 2
    assert len(PropertyManager.get_properties(Property.PLANNED)) == 0
    assert len(PropertyManager.get_properties(Property.SOLD)) == 0
    assert PropertyManager.get_properties(Property.OWNED)[0] == property0
    assert PropertyManager.get_properties(Property.OWNED)[1] == property1
    
    
    property2 = Property(Config({"Name": "Planned House", "Worth": 300000, "BuyAge": start_age, "Status" : "Planned"}))

    # Act
    PropertyManager.add_property(property2)

    # Assert
    assert len(PropertyManager.get_properties(Property.OWNED)) == 2
    assert len(PropertyManager.get_properties(Property.PLANNED)) == 1
    assert len(PropertyManager.get_properties(Property.SOLD)) == 0
    assert PropertyManager.get_properties(Property.OWNED)[0] == property0
    assert PropertyManager.get_properties(Property.PLANNED)[0] == property2

    
    
    property3 = Property(Config({"Name": "Sold House", "Worth": 200000, "Status" : "Sold"}))

    # Act
    PropertyManager.add_property(property3)
    
    assert len(PropertyManager.get_properties(Property.OWNED)) == 2
    assert len(PropertyManager.get_properties(Property.PLANNED)) == 1
    assert len(PropertyManager.get_properties(Property.SOLD)) == 1
    assert PropertyManager.get_properties(Property.OWNED)[0] == property0
    assert PropertyManager.get_properties(Property.PLANNED)[0] == property2
    assert PropertyManager.get_properties(Property.SOLD)[0] == property3

    
    
    assert PropertyManager.get_property_for_sale() == property1
    assert PropertyManager.get_property_to_buy() == property2
    
    PropertyManager.remove_property(property0)
    
    assert len(PropertyManager.get_properties(Property.OWNED)) == 1
    
def test_add_property_from_json(config : Config): 
    
    sample_data = {
            "RealEstate": {
                "Properties": [
                    {
                        "Name": "Haus",
                        "Status": "Owned",
                        "Price": 725000.0,
                        "Worth":  1400000.0, 
                        "RentalIncome": 0.0,
                        "FixCosts": 600.0,
                        "Sell": 72.0,
                        "Mortage": {       
                            "Value": 650000.0,
                            "Interest": 0.0105,
                            "Start": 62.0,
                            "Term": 10.0,
                            "Amortization": 550.0
                        } 
                    },
                    {
                        "Name": "Wohnung",
                        "Status": "Planned",
                        "Price":  750000.0, 
                        "Mortage": {       
                            "Interest": 0.0105,
                            "Term": 10.0,
                            "Amortization": 550.0
                        }    
                    },
                    {
                        "Name": "Mietwohnung",
                        "Status": "Rented",
                        "Price": 1800.0    
                    }    
                ]
            },              
                              
    }
    
    config = Config()
    config.loads(json.dumps(sample_data))
    
    properties_config = config.getValue(Config.REALESTATE_PROPERTIES,[]) 
    
    for property_config in properties_config :
        property = Property(Config(property_config))
        PropertyManager.add_property(property)
       
    assert PropertyManager.get_properties(Property.OWNED)[0].get_name() == "Haus"    
    assert PropertyManager.get_properties(Property.PLANNED)[0].get_name() == "Wohnung"   
    assert PropertyManager.get_properties(Property.RENTED)[0].get_name() == "Mietwohnung"  
    
    
def test_sell_property(config : Config):
     
     
    property1 = Property(Config({"Name": "Owned House", "Price": 100000, "Status" : "Owned"})) 
    property2 = Property(Config({"Name": "Owned House2", "Price": 200000, "Status" : "Owned"}))
    property3 = Property(Config({"Name": "Owned House3", "Price": 300000, "Status" : "Owned"}))
    
    data = Data(config)

    # Act
    PropertyManager.add_property(property1)
    PropertyManager.add_property(property2)
    PropertyManager.add_property(property3)
    assert PropertyManager.get_properties_expenses() == 0.01*(property1.get_price() + property2.get_price() + property3.get_price())/Config.MONTHS
    
    assert PropertyManager.get_property_for_sale() == property3
    
    assert PropertyManager.sell(property3, data, config)  is True
    assert data.get_wealth() == property3.get_price()
    assert PropertyManager.get_properties_expenses() == 0.01*(property1.get_price() + property2.get_price())/Config.MONTHS
    assert len(PropertyManager.get_properties(Property.OWNED)) == 2
    assert len(PropertyManager.get_properties(Property.SOLD)) == 1
    
    assert PropertyManager.sell(property3, data, config)  is False
    assert data.get_wealth() == property3.get_price()
    assert PropertyManager.get_properties_expenses() == 0.01*(property1.get_price() + property2.get_price())/Config.MONTHS
    assert len(PropertyManager.get_properties(Property.OWNED)) == 2
    assert len(PropertyManager.get_properties(Property.SOLD)) == 1
    
    assert PropertyManager.get_property_for_sale() == property2
    
    assert PropertyManager.sell(property2, data, config)  is True
    assert data.get_wealth() == property3.get_price() +  property2.get_price()
    assert PropertyManager.get_properties_expenses() == 0.01*property1.get_price()/Config.MONTHS
    assert len(PropertyManager.get_properties(Property.OWNED)) == 1
    assert len(PropertyManager.get_properties(Property.SOLD)) == 2
    
    
def test_new_mortage(config : Config):  
    # Arrange

    data = Data(config)
    data.set_wealth(0.0)
    data.set_legal_pension(10)
    data.set_private_pension(10)
    property = Property(Config({"Name": "Owned House", "Price": 1000, "Status" : "Planned" }))
    property.get_mortage().set_value(800.0)

    # Act
    mortage = PropertyManager.mortage(property, data, config)
    assert mortage is None   # not enough own fund
    
    data.set_wealth(199)
    mortage = PropertyManager.mortage(property, data, config)
    assert mortage is None   # not enough own fund
    
    data.set_wealth(200)
    mortage = PropertyManager.mortage(property, data, config)
    
    # Assert
    assert mortage is not None
    assert round(mortage.get_value(),2) == 800.0
    assert mortage.get_interest() == 0.05
    assert mortage.get_term() == 10.0
    assert property.get_fix_costs() == property.get_price()*0.01/12
    
    property.set_worth(3000.0)
    data.set_wealth(2000.0)
    mortage = PropertyManager.mortage(property, data, config)
    
    # Assert
    assert mortage is not None
    assert round(mortage.get_value(),2) == 800

    property = Property(Config({"Name": "Owned House", "Price": 4000, "Status" : "Planned" }))
    property.get_mortage().set_value(4000*0.8)
    data.set_wealth(2000.0)
    assert PropertyManager.mortage(property, data, config) is None
        
    data.set_wealth(3200.0)
    mortage = PropertyManager.mortage(property, data, config)
    assert mortage is not None
    assert round(mortage.get_value(),2) == 800
    
    data.set_wealth(4000.0)
    mortage = PropertyManager.mortage(property, data, config)
    assert mortage is not None
    assert round(mortage.get_value(),2) == 1000
    
    
    data.set_wealth(16000.0)
    mortage = PropertyManager.mortage(property, data, config)
    assert mortage is not None
    assert round(mortage.get_value(),2) == 3200
    
    
    
    

    
