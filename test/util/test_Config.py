import pytest

import json

from src.util.config import Config



@pytest.fixture
def config():
    sample_data = {
         
        "General": {
            "Start": 2020,
            "End": 2090,
            "Age": 56.75
        },
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
        config.setValue(Config.GENERAL_AGE, 40)
        config.setValue(Config.CALCULATION_SINGLE_INFLATION, 0.01)  
        config.setValue(Config.CALCULATION_SINGLE_PERFORMANCE, 0.1)
       
        # Act
        try:
            config.initialize()
        except Exception as e:
            pytest.fail(f"Initialization failed with exception: {e}")
            
                # Act
        try:
            config.initialize()
            pytest.fail( "Initialization didnt fail after called twice")
        except Exception as e:
            pass 
            
        
            
def test_convert_to_monthly_list(config):
     
    key = "Test.Value"
    i = 100
    config.setValue(key, i)
    expected_output = {0 : i}
    monthly_list = config.convert_to_monthly_list(key)
    assert monthly_list == expected_output
    
    i = i+1
    config.setValue(key, {1970 : i})
    expected_output = {0 : i}
    monthly_list = config.convert_to_monthly_list(key)
    assert monthly_list == expected_output
    
    i = i+1
    config.setValue(key, {53.3 : i})
    expected_output = {0 : i}
    monthly_list = config.convert_to_monthly_list(key)
    assert monthly_list == expected_output
    
    i = i+1
    config.setValue(key, {57.75 : i})
    expected_output = {12 : i}
    monthly_list = config.convert_to_monthly_list(key)
    assert monthly_list == expected_output
    
    i = i+1
    config.setValue(key, {57.75+2/12 : i})
    expected_output = {14 : i}
    monthly_list = config.convert_to_monthly_list(key)
    assert monthly_list == expected_output
    
    i = i+1
    config.setValue(key, {57.75+2/12+0.5/12 : i})
    expected_output = {14 : i}
    monthly_list = config.convert_to_monthly_list(key)
    assert monthly_list == expected_output
    
    i = i+1
    config.setValue(key, {57.75+2/12+0.50001/12 : i})
    expected_output = {15 : i}
    monthly_list = config.convert_to_monthly_list(key)
    assert monthly_list == expected_output
    
    i = i+1
    config.setValue(key, {56.75 : i, 2020 : -2 })
    expected_output = {0 : -2}
    monthly_list = config.convert_to_monthly_list(key)
    assert monthly_list == expected_output
    
    i = i+1
    config.setValue(key, {57.75 : i, 2020 : -2 })
    expected_output = {0 : -2, 12 : i}
    monthly_list = config.convert_to_monthly_list(key)
    assert monthly_list == expected_output
           

def test_setSimulationTime(config):
        config.setSimulationTime(36)
        actual_month = config.getSimulationTime()
        assert actual_month == 36
        
        config.setSimulationTime(0)
        actual_month = config.getSimulationTime()
        assert actual_month == 0

        config.setSimulationTime(-3)
        actual_month = config.getSimulationTime()
        assert actual_month == -3
        
            

def test_getValue(caplog,config):

    assert config.getValue("Property.Actual.Sell") == 100
    assert config.getValue("Property.Affordability.CapitalContribution") == 300
    
    assert config.getValue("Unknown.Affordability") is None
    assert config.getValue("Property.Unknown") is None
    assert config.getValue("Property.Unknown",5) == 5
    


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
    assert config.setValue(Config.GENERAL_AGE , 40) == 56.75

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

