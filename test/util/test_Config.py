import pytest

import json

from src.util.config import Config



@pytest.fixture
def config():
    sample_data = {
        "Property": {
            "Actual": {
                "Sell": 100,
                "Worth": 200
            },
            "Affordability": {
                "CapitalContribution": 300,
                "ExtraCosts": 400
            }
        }
    }

    config = Config()
    config.loads(json.dumps(sample_data))
    yield config

def test_load(config):
  
    try: 
        config.load("./data/config.json")
    except Exception as e:
        pytest.fail(f"Initialization failed with exception: {e}")
    


def test_initialize(config):
        # Arrange
        config = Config()
        
        config.setValue(Config.CALCULATION_METHOD, "Single")
        config.setValue(Config.CALCULATION_SINGLE_MAX, 100)
        config.setValue(Config.GENERAL_AGE, 40)
        config.setValue(Config.CALCULATION_SINGLE_INFLATION, 0.01)  
        config.setValue(Config.CALCULATION_SINGLE_PERFORMANCE, 0.1)
       
        # Act
        try:
            config.initialize()
        except Exception as e:
            pytest.fail(f"Initialization failed with exception: {e}")

def test_setSimulationTime(config):
        config.setSimulationTime(36)
        actual_year, actual_month = config.getSimulationTime()
        assert actual_year == 3
        assert actual_month == 36
        
        config.setSimulationTime(0)
        actual_year, actual_month = config.getSimulationTime()
        assert actual_year == 0
        assert actual_month == 0

        config.setSimulationTime(30)
        actual_year, actual_month = config.getSimulationTime()
        assert actual_year == 2.5
        assert actual_month == 30
        
        
        config.setSimulationTime(31)
        actual_year, actual_month = config.getSimulationTime()
        assert actual_year == 2.0+7/12
        assert actual_month == 31
        
            

def test_getValue(caplog,config):

    assert config.getValue("Property.Actual.Sell") == 100
    assert config.getValue("Property.Affordability.CapitalContribution") == 300
    
    assert config.getValue("Unknown.Affordability") is None
    assert config.getValue("Property.Unknown") is None


def test_setValue(config):
    assert config.setValue(None,None) is None
    assert config.setValue('',None) is None
    
    assert config.getValue("Property.Actual.Sell") == 100
    old_value = config.setValue("Property.Actual.Sell", 150)
    assert old_value == 100
    assert config.getValue("Property.Actual.Sell") == 150
    
    assert config.setValue(Config.CALCULATION, {}) is None
    assert config.setValue(Config.CALCULATION_SINGLE_INFLATION , 0.01) is None
    assert config.getValue(Config.CALCULATION_SINGLE_INFLATION) == 0.01
    assert config.setValue(Config.GENERAL_AGE , 40) is None
    assert config.setValue(Config.CALCULATION_SINGLE_MAX,100) is None

def test_delete(config):
    assert config.delete("Property.Actual.Sell") == 100
    
    config.delete("Property.Actual")
    assert config.getValue("Property.Actual") is None
    
    config.setValue("Property.Actual.Sell", 100)
    config.setValue("Property.Actual.Worth", 200)
    assert config.delete("Property.Actual") == { 'Sell':100, 'Worth': 200 } 



def test_clone(config):
    data_copy = config.clone()
    
    assert data_copy.getValue("Property.Actual.Sell") == config.getValue("Property.Actual.Sell")
    assert data_copy is not config
    
def test_dump(config):
    try: 
        config.load("./data/config.json")
    except Exception as e:
        pytest.fail(f"Initialization failed with exception: {e}")
    
    config.dump_data()
