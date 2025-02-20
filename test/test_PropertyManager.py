import pytest
from src.data import Data
from src.property import Property, PropertyManager
from src.util.config import Config


@pytest.fixture
def config():
    PropertyManager.reset()
    config = Config().initialize()
    yield config
    
    
                      

def test_PropertyManager(config : Config):
    # Arrange

    start_age = config.getStartAge()
    property0 = Property(config, {"Name": "Owned House", "Worth": 100000, "Buy": start_age-10, "Sell": start_age+10})

    # Act
    PropertyManager.add_property(property0)

    # Assert
    # Assert
    assert len(PropertyManager.get_owned_properties()) == 1
    assert len(PropertyManager.get_planned_properties()) == 0
    assert len(PropertyManager.get_sold_properties()) == 0
    assert PropertyManager.get_owned_properties()[0] == property0
    
    property1 = Property(config, {"Name": "Owned House", "Worth": 200000, "Buy": start_age-10, "Sell": start_age+10})

    # Act
    PropertyManager.add_property(property1)

    # Assert
    assert len(PropertyManager.get_owned_properties()) == 2
    assert len(PropertyManager.get_planned_properties()) == 0
    assert len(PropertyManager.get_sold_properties()) == 0
    assert PropertyManager.get_owned_properties()[0] == property1
    assert PropertyManager.get_owned_properties()[1] == property0
    
    
    property2 = Property(config, {"Name": "Planned House", "Worth": 200000, "Buy": start_age, "Sell": start_age+10})

    # Act
    PropertyManager.add_property(property2)

    # Assert
    assert len(PropertyManager.get_owned_properties()) == 2
    assert len(PropertyManager.get_planned_properties()) == 1
    assert len(PropertyManager.get_sold_properties()) == 0
    assert PropertyManager.get_owned_properties()[0] == property1
    assert PropertyManager.get_planned_properties()[0] == property2
    
    
    property3 = Property(config, {"Name": "Sold House", "Worth": 200000, "Buy": start_age-10, "Sell": start_age-1})

    # Act
    PropertyManager.add_property(property3)

    # Assert
    assert len(PropertyManager.get_owned_properties()) == 2
    assert len(PropertyManager.get_planned_properties()) == 1
    assert len(PropertyManager.get_sold_properties()) == 1
    assert PropertyManager.get_owned_properties()[0] == property1
    assert PropertyManager.get_planned_properties()[0] == property2
    assert PropertyManager.get_sold_properties()[0] == property3
    
    
    assert PropertyManager.get_property_for_sale() == property1
    assert PropertyManager.get_property_to_buy() == property2
    
    PropertyManager.remove_property(property0)
    
    assert len(PropertyManager.get_owned_properties()) == 1
    
    assert PropertyManager.sell(property1) == 200000
    assert PropertyManager.sell(property2) is None
    
    assert len(PropertyManager.get_owned_properties()) == 0
    assert len(PropertyManager.get_sold_properties()) == 2
    
    
def test_new_mortage(config : Config):  
    # Arrange

    data = Data(config.getStartAge(), config.getEndAge())
    data.set_wealth(0.0)
    data.set_legal_pension(10)
    data.set_private_pension(10)
    property = Property(config, {"Name": "Owned House", "Price": 1000, "Buy": (config.getStartAge()-10.0), "Sell": (config.getEndAge()+1), "MortageInterest" : 0.015 })

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
    
    
    
    
    

    
