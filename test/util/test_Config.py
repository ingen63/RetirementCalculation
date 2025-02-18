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
        "Early": {
            "Age": 62.17,
            "SeverancePay": 0.0,
            "Spending": 11000.0
        },

        "Legal": {
            "Age": 65,
            "Spending": 9000.0
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
        config.setValue(Config.GENERAL_STARTAGE, 40)
        config.setValue(Config.CALCULATION_SINGLE_INFLATION, 0.01)  
        config.setValue(Config.CALCULATION_SINGLE_PERFORMANCE, 0.1)
       
        # Act
        try:
            config.initialize()
        except Exception as e:
            pytest.fail(f"Initialization failed with exception: {e}")
            
            
        
            

def test_getValue(config):

    assert config.getValue("Property.Actual.Sell") == 100
    assert config.getValue("Property.Affordability.CapitalContribution") == 300
    
    assert config.getValue("Unknown.Affordability") is None
    assert config.getValue("Property.Unknown") is None
    assert config.getValue("Property.Unknown",5) == 5
    

def test_getActualValue(config):
    config = config.clone()
    config.setValue(Config.GENERAL_STARTAGE, 50)
    config.setValue("Test.Branch.Float", 1.2)
    config.setValue("Test.Branch.Dict", {"50" : 5000, "60.1" : 6000, "70" : 7000})
    config.initialize()
    
    assert config.getActualValue((50-50)*12, "Test.Branch.Float") == 1.2
    assert config.getActualValue((50-50)*12, "Test.Branch.Dict") == 5000
    assert config.getActualValue((51-50)*12, "Test.Branch.Dict") == 5000
    assert config.getActualValue((40-50)*12, "Test.Branch.Dict") is None
    assert config.getActualValue((40-50)*12, "Test.Branch.Dict", 21.0) == 21.0
    assert config.getActualValue((60-50)*12, "Test.Branch.Dict", 21.0) == 5000
    assert config.getActualValue((60.1-50)*12, "Test.Branch.Dict", 21.0) == 6000
    assert config.getActualValue((70-50)*12, "Test.Branch.Dict", 21.0) == 7000  
    assert config.getActualValue((80-50)*12, "Test.Branch.Dict") == 7000
    assert config.getActualValue((90-50)*12, "Test.Branch.Unknonw") is None

def test_setValue(config):
    
    assert config.setValue("Test.Test.Test" , 1) is None
    assert config.getValue("Test.Test.Test") == 1
   
    assert config.setValue(None,None) is None
    assert config.setValue('',None) is None
    
    assert config.getValue("Property.Actual.Sell") == 100
    old_value = config.setValue("Property.Actual.Sell", 150)
    assert old_value == 100
    assert config.getValue("Property.Actual.Sell") == 150
    
    assert config.setValue(Config.CALCULATION, {}) is None
    assert config.setValue(Config.CALCULATION_SINGLE_INFLATION , 0.01) is None
    assert config.getValue(Config.CALCULATION_SINGLE_INFLATION) == 0.01


def test_delete(config):
    assert config.delete("Property.Actual.Sell") == 100
    
    config.delete("Property.Actual")
    assert config.getValue("Property.Actual") is None
    
    config.setValue("Property.Actual.Sell", 100)
    config.setValue("Property.Actual.Worth", 200)
    assert config.delete("Property.Actual") == { 'Sell':100, 'Worth': 200 } 
    
def test_clear(config):
    config.clear()
    
    assert config.getValue("General") is None
    

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

