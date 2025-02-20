import json
import pytest
from src.event import ChangeValueEvent
from src.util.config import Config
from src.data import Data

@pytest.fixture
def config():
    sample_data = {
        
        "Calculation": {
            "Performance": 100
        }
    }
    config = Config()
    config.loads(json.dumps(sample_data))
    config.setValue(Config.GENERAL_STARTAGE, 50)
    config.initialize()
    return config

@pytest.fixture
def data():
    return Data(0,30*12)


def test_change_value_event_before_method(config, data):
    # Arrange
    test_value = 150
    config.setValue( Config.CALCULATION_PERFORMANCE, test_value)
    event = ChangeValueEvent(0,  Config.CALCULATION_PERFORMANCE)

    # Act
    event.before_method(config, data)

    # Assert
    assert data.get_performance() == test_value
    
def test_change_value_event_data_before_start(config, data):
    # Arrange
    test_value = {"40" : 0.04, "60" : 0.06}
    config.setValue( Config.CALCULATION_PERFORMANCE, test_value)
    event = ChangeValueEvent(0,  Config.CALCULATION_PERFORMANCE)

    # Act
    event.before_method(config, data)

    # Assert
    assert data.get_performance() == 0.04  

def test_change_value_event_nonexistent_key(config, data):
    # Arrange
    test_key = "NonExistent.Key"
    event = ChangeValueEvent(0, test_key)


    # Act
    try :
        event.before_method(config, data)
        pytest.fail(f"Expected an exception for non-existent key: {test_key}")
    except Exception as e:
        pytest.raises(KeyError, match=f"KeyError: {test_key} not found returning default value  e: {e}")    

