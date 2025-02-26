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
    
    sorted = PropertyManager.get_planned_properties()
    assert sorted[0].get_buy_age() == 50
    assert sorted[1].get_buy_age() == 52
    assert sorted[2].get_buy_age() == 54
    
    sorted = PropertyManager.get_planned_properties(False)
    assert sorted[0].get_buy_age() == 50
    assert sorted[1].get_buy_age() == 52
    assert sorted[2].get_buy_age() == 54
    
    property1.set_buy_age(50)
    property2.set_buy_age(50)
    
    sorted = PropertyManager.get_planned_properties()
    assert sorted[0].get_price() == 80
    assert sorted[1].get_price() == 90
    assert sorted[2].get_price() == 100
    
    sorted = PropertyManager.get_planned_properties(False)
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
    assert len(PropertyManager.get_owned_properties()) == 1
    assert len(PropertyManager.get_planned_properties()) == 0
    assert len(PropertyManager.get_sold_properties()) == 0
    assert PropertyManager.get_owned_properties()[0] == property0
    
    property1 = Property(Config({"Name": "Owned House", "Worth": 200000, "Status" : "Owned"}))

    # Act
    PropertyManager.add_property(property1)

    # Assert
    assert len(PropertyManager.get_owned_properties()) == 2
    assert len(PropertyManager.get_planned_properties()) == 0
    assert len(PropertyManager.get_sold_properties()) == 0
    assert PropertyManager.get_owned_properties()[0] == property1
    assert PropertyManager.get_owned_properties()[1] == property0
    
    
    property2 = Property(Config({"Name": "Planned House", "Worth": 300000, "BuyAge": start_age, "Status" : "Planned"}))

    # Act
    PropertyManager.add_property(property2)

    # Assert
    assert len(PropertyManager.get_owned_properties()) == 2
    assert len(PropertyManager.get_planned_properties()) == 1
    assert len(PropertyManager.get_sold_properties()) == 0
    assert PropertyManager.get_owned_properties()[0] == property1
    assert PropertyManager.get_planned_properties()[0] == property2
    
    
    property3 = Property(Config({"Name": "Sold House", "Worth": 200000, "Status" : "Sold"}))

    # Act
    PropertyManager.add_property(property3)

    # Assert
    assert len(PropertyManager.get_owned_properties()) == 2
    assert len(PropertyManager.get_planned_properties()) == 1
    assert len(PropertyManager.get_sold_properties()) == 1
    assert PropertyManager.get_owned_properties()[0] == property1
    assert PropertyManager.get_planned_properties()[0] == property2
    assert PropertyManager.get_sold_properties()[0] == property3
    
    
    assert PropertyManager.get_property_for_sale() == property0
    assert PropertyManager.get_property_to_buy() == property2
    
    PropertyManager.remove_property(property0)
    
    assert len(PropertyManager.get_owned_properties()) == 1
    
def test_add_property_from_json() :  
    
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
       
    assert PropertyManager.get_owned_properties()[0].get_name() == "Haus"    
    assert PropertyManager.get_planned_properties()[0].get_name() == "Wohnung"   
    assert PropertyManager.get_rented_properties()[0].get_name() == "Mietwohnung"  
    
    
def test_sell_property(config):
     
     
    property = Property(Config({"Name": "Owned House", "Worth": 100000, "Status" : "Owned"}))
    
    property2 = Property(Config({"Name": "Owned House2", "Price": 200000, "Status" : "Owned"}))
    property3 = Property(Config({"Name": "Owned House3", "Price": 300000, "Status" : "Owned"}))
    
    data = Data(config.getStartAge(), config.getEndAge())

    # Act
    PropertyManager.add_property(property)
    PropertyManager.add_property(property2)
    PropertyManager.add_property(property3)
    
    assert PropertyManager.sell(property, data)  is True
    
    assert data.get_wealth() == property.get_price()
    
    assert PropertyManager.sell(property, data)  is False
    
    assert data.get_wealth() == property.get_price()
    
    data.set_wealth(10)
    data.set_spending(1)
    data.set_threshold_months(24)
    
    assert PropertyManager.sell(property, data)  is True
    
    assert data.get_wealth() == property2.get_price() + 10
    
    
    
    
    
    
def test_new_mortage(config : Config):  
    # Arrange

    data = Data(config.getStartAge(), config.getEndAge())
    data.set_wealth(0.0)
    data.set_legal_pension(10)
    data.set_private_pension(10)
    property = Property(config, {"Name": "Owned House", "Price": 1000, "Status" : "Owned", "SellAge": (config.getEndAge()+1), "Mortage.Interest" : 0.015 })

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
    assert mortage.get_interest() == property.get_planned_mortage_interest()
    assert mortage.get_term() == property.get_planned_mortage_term()
    assert property.get_fix_costs() == property.get_price()*0.01
    
    property.set_worth(3000.0)
    data.set_wealth(2000.0)
    mortage = PropertyManager.mortage(property, data, config)
    
    # Assert
    assert mortage is not None
    assert round(mortage.get_value(),2) == 1800

    property.set_worth(4000.0)
    data.set_wealth(2000.0)
    mortage = PropertyManager.mortage(property, data, config)
    
    # Assert
    assert mortage is not None
    assert round(mortage.get_value(),2) == 1800
    
    
    property.set_mortage(mortage)
    mortage = PropertyManager.mortage(property, data, config)
    
    # Assert
    assert mortage is not None
    assert round(mortage.get_value(),2) == 1800
    
    data.set_wealth(0.0)
    mortage = PropertyManager.mortage(property, data, config)
    
    assert mortage is None
    
    
    data.set_wealth(400.0)
    mortage = PropertyManager.mortage(property, data, config)
    
    assert round(mortage.get_value(),2) == 1400
    
    
    
    
    

    
