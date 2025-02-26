import json
import pytest
from event import ChangeValueEvent
from config import Config
from data import Data

@pytest.fixture
def config():

    config = Config()

    return config

@pytest.fixture
def data():
    return Data(Config.DEFAULT_STARTAGE,Config.DEFAULT_STARTAGE+Config.DEFAULT_MAXPERIOD, Config.DEFAULT_STARTMONTH)


def test_change_value_event_before_method(config, data):
    # Arrange
    test_value = 0.01
    config.setValue(Config.CALCULATION_SINGLE_PERFORMANCE, test_value)
    event = ChangeValueEvent(Config.DEFAULT_STARTMONTH,  Config.CALCULATION_SINGLE_PERFORMANCE)

    assert data.get_performance() == 0.0
    # Act
    event.before_method(config, data)

    # Assert
    assert data.get_performance() == test_value
    
def test_change_value_event_data_before_start(config, data):
    # Arrange
    test_value = {"40" : 0.04, "60" : 0.06}
    config.setValue( Config.CALCULATION_SINGLE_PERFORMANCE, test_value)
    event40 = ChangeValueEvent(Config.DEFAULT_STARTMONTH,  Config.CALCULATION_SINGLE_PERFORMANCE)
    event61 = ChangeValueEvent(config.age2months(61),  Config.CALCULATION_SINGLE_PERFORMANCE)
     

    # Act
    event40.before_method(config, data)
    assert data.get_performance() == 0.04
    event61.before_method(config, data) 
    assert data.get_performance() == 0.06

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

