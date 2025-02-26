import json
import pytest

from property import Mortage, Property
from src.config import Config


@pytest.fixture
def config():
    
    sample_data = {
        "RealEstate": {
            "ThresholdYears" : 2,
            "BuyAfterSell": "True",
            "Affordability": { 
                "Sustainability": 0.33, 
                "MortageInterest": 0.05,
                "CapitalContribution": 0.03,
                "FixCosts": 0.01
            },
            "Properties": [
                {
                    "Name": "Haus",
                    "Status": "Owned",
                    "Price": 1000.0,
                    "Worth":  2000.0, 
                    "RentalIncome": 10.0,
                    "FixCosts": 750.0,
                    "Sell": 72.0,
                    "Mortage": {       
                        "Value": 750.0,
                        "Interest": 0.01,
                        "Start": 62.0,
                        "Term": 10.0,
                        "Amortization": 15.0
                    } 
                }
                ]     
            }
        }
    
    config = Config()
    config.loads(json.dumps(sample_data))
    
    yield config
    
    
def test_property(config: Config):
    properties = config.getValue(Config.REALESTATE_PROPERTIES)

    property_config = Config(properties[0])
    property = Property(property_config)

    assert property.get_name() == property_config.getValue(Property.NAME)
    assert property.get_status() == property_config.getValue(Property.STATUS)
    assert round(property.get_price(),2) == property_config.getValue(Property.PRICE)
    assert round(property.get_worth(),2) == property_config.getValue(Property.WORTH)
    assert property.get_buy_age() == property_config.getValue(Property.BUYAGE)
    assert property.get_sell_age() == property_config.getValue(Property.SELLAGE)
    assert property.get_mortage().get_value() == property_config.getValue(Property.MORTAGE_VALUE)
    assert property.get_mortage().get_interest() == property_config.getValue(Property.MORTAGE_INTEREST)
    assert property.get_mortage().get_term() == property_config.getValue(Property.MORTAGE_TERM)
    assert property.get_fix_costs() == property_config.getValue(Property.FIXCOSTS)
    assert property.get_rental_income() == property_config.getValue(Property.RENTALINCOME)

    property = Property(Config())
    assert property.get_name() is not None
    assert property.get_status() == Property.PLANNED
    assert round(property.get_price(),2) == 0.0
    assert round(property.get_worth(),2) == 0.0
    assert property.get_buy_age() is None
    assert property.get_sell_age() is None
    assert property.get_mortage().get_value() == 0.0
    assert property.get_mortage().get_interest() == Mortage.DEFAULT_AFFORDABILITY_MORTAGEINTEREST
    assert property.get_mortage().get_term() == Mortage.DEFAULT_MORTAGE_TERM
    assert round(property.get_fix_costs(),2) == 0.0
    assert property.get_rental_income() == 0.0
        
         
        
    
    
                      

