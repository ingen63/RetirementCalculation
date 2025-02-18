import json
import pytest
from src.util.config import Config
from src.data import Data
from src.event import EarlyRetirmentEvent

@pytest.fixture
def config():
    sample_data = {
        "Early": {
            "SeverancePay": 10000.0,
            "Spending": 5000.0
        },
        "Pension": {
            "Private": {
                "Capital": 500000.0,
                "LumpsumRatio": 0.25,
                "LumpsumTaxrate": 0.1,
                "ConversionRate": 0.05
            }
        }
    }
    config = Config()
    config.loads(json.dumps(sample_data))
    return config

@pytest.fixture
def data():
    return Data()


def test_early_retirement_event(config, data):
    event = EarlyRetirmentEvent(0)
    
    
    # Call the before_method
    event.before_method(config, data)
    
    
    # Assert that extra and spending were set correctly
    assert data.get_extra() == config.getValue(Config.EARLY_SEVERANCEPAY)
    assert data.get_spending() == config.getValue(Config.EARLY_SPENDING)
    assert data.get_lumpsum() == 0.25*500000*(1-0.1)
    
    
    event.after_method(config, data)
    assert data.get_extra() == 0.0
    assert data.get_spending() == config.getValue(Config.EARLY_SPENDING)
    assert data.get_lumpsum() == 0.0
    
