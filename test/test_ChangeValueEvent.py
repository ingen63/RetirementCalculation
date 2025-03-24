import json
import pytest
from event import ChangeValueEvent
from config import Config
from data import Data

@pytest.fixture
def config():

    config = Config()

    return config


def test_change_value_event_before_method(config):
    data = Data(config)
    # Arrange
    test_value = 0.01
    config.setValue(Config.WEALTHMANAGEMENT_STOCKPERFORMANCE, test_value)
    event = ChangeValueEvent(Config.DEFAULT_STARTMONTH,  Config.WEALTHMANAGEMENT_STOCKPERFORMANCE)

    assert data.get_performance() == 0.0
    # Act
    event.before_method(config, data)

    # Assert
    assert data.get_performance() == test_value
    
def test_change_value_event_data_before_start(config):
    data = Data(config)
    # Arrange
    test_value = {"40" : 0.04, "60" : 0.061}
    config.setValue( Config.WEALTHMANAGEMENT_STOCKPERFORMANCE, test_value)
    event40 = ChangeValueEvent(Config.DEFAULT_STARTMONTH,  Config.WEALTHMANAGEMENT_STOCKPERFORMANCE)
    event61 = ChangeValueEvent(config.age2months(61),  Config.WEALTHMANAGEMENT_STOCKPERFORMANCE)
     

    # Act
    event40.before_method(config, data)
    assert data.get_performance() == 0.04
    event61.before_method(config, data) 
    assert data.get_performance() == 0.061

def test_change_value_event_nonexistent_key(config):
    data = Data(config)
    # Arrange
    test_key = "NonExistent.Key"
    event = ChangeValueEvent(0, test_key)


    # Act
    try :
        event.before_method(config, data)
        pytest.fail(f"Expected an exception for non-existent key: {test_key}")
    except Exception as e:
        pytest.raises(KeyError, match=f"KeyError: {test_key} not found returning default value  e: {e}")    

