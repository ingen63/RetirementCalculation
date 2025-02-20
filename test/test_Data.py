import json
import pytest
from src.data import Data
from src.util.config import Config


@pytest.fixture
def config():
    sample_data = {
         
        "Early": {
            "Spending": 11000.0
        },

        "Legal": {
            "Spending": {"65" : 6500.0, "75" : 7500}
        },
        "Pension": {
            "Private": {
                "Contribution": 
                    {"60": 4500.0, "62": 5000.0}
            }
        },
        "Calculation": {
            "Single": {
                "Inflation": {"60" : 0.01, "62" : 0.02},
                "Performance":{"61" : 0.05, "63" : 0.07}     
            }
        }
    }

    config = Config()
    config.loads(json.dumps(sample_data))
    yield config


def test_set_value(config):
    config = config.clone()
    config.setValue(Config.GENERAL_STARTAGE, 50)
    config.initialize()
    
    data = Data(config.getStartAge(), config.getEndAge())
    
    initial = data.get_spending()
    actual = config.getActualValue((65-50)*12, Config.EARLY_SPENDING)
    data.set_value(Config.EARLY_SPENDING,actual)
    assert data.get_spending() == actual
    assert data.get_spending() != initial
    
    
    initial = data.get_pk_contribution()
    actual = config.getActualValue((65-50)*12, Config.PENSION_PRIVATE_CONTRIBUTION)
    data.set_value(Config.PENSION_PRIVATE_CONTRIBUTION,actual)
    assert data.get_pk_contribution() == actual
    assert data.get_pk_contribution() != initial
    
    initial = data.get_pk_contribution()
    actual = config.getActualValue(45, Config.PENSION_PRIVATE_CONTRIBUTION)
    data.set_value(Config.PENSION_PRIVATE_CONTRIBUTION,actual)
    assert data.get_pk_contribution() is None
    assert data.get_pk_contribution() != initial
