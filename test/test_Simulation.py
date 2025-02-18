import json
import pytest
from src.simulation import Simulation
from src.util.config import Config
from src.event import EventHandler
from src.util.utils import Utils

@pytest.fixture
def config():
    sample_data = {
        "General" : {
            "StartAge": 49.8333,
            "Wealth": 100000.00,  
            "IncomeTaxRate": 0.0,
            "CapitalTaxRate": 0.0
        },
        "Pension": {
            "Private": {
                "Capital": 200000.0,
                "LumpsumRatio": 0.5,
                "LumpsumTaxrate": 0.00,
                "ConversionRate": 0.042, 
                "Contribution":  {"50": 4555.0},
                "Interest":  {"50": 0.04,"59.75": 0.06, "60.75" : 0.08, "62.75" : 0.06}
            },
            "Legal": 1952.0
        },
        "Before": {
            "Savings": {"50": 1000.0, "55": 1500}
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
        "Calculation": {
             "Method": "Single",
            "Single": {
                "Inflation": 0.01,
                "Performance": 0.04              
            }
        }
    }
    
    config = Config()
    config.loads(json.dumps(sample_data))
    config.initialize()
    return config

def test_init(config):
    
    simulation = Simulation()
    
    data = simulation.init(config)
    
    start_age = config.getStartAge()
    
    events = EventHandler.get_events(Utils.years_to_months(50 - start_age))
    
    assert len(events) == 3
    assert events[0].get_name() == f"ChangeValueEvent {Config.PENSION_PRIVATE_CONTRIBUTION}"
    assert events[1].get_name() == f"ChangeValueEvent {Config.PENSION_PRIVATE_INTEREST}"
    assert events[2].get_name() == f"ChangeValueEvent {Config.BEFORE_SAVINGS}"
    
    events = EventHandler.get_events(Utils.years_to_months(52 - start_age))   
    assert len(events) == 0

    
    events = EventHandler.get_events(Utils.years_to_months(55 - start_age))   
    assert len(events) == 1
    assert events[0].get_name() == f"ChangeValueEvent {Config.BEFORE_SAVINGS}"
    
    events = EventHandler.get_events(Utils.years_to_months(62.17 - start_age))   
    assert len(events) == 2
    assert events[0].get_name() == "EarlyRetirementEvent"
    
    events = EventHandler.get_events(Utils.years_to_months(65 - start_age))   
    assert len(events) == 2
    assert events[0].get_name() == "LegalRetirementEvent"
    
    events = EventHandler.get_events(data.get_end_simulation_month())  
    assert len(events) == 1
    assert events[0].get_name() == "EndSimulationEvent"
    
    




def test_simulate(config):
    simulation = Simulation()

 
    config.setValue(Config.GENERAL_ENDAGE, 55)
    config.setValue(Config.EARLY_AGE, 62.17)
    config.setValue(Config.CALCULATION_PERFORMANCE,0.0)
    config.setValue(Config.CALCULATION_INFLATION,0.0)
    config.setValue(Config.PENSION_PRIVATE_INTEREST,0.0)
    config.setValue(Config.PENSION_PRIVATE_CONTRIBUTION,2000) 
    config.setValue(Config.BEFORE_SAVINGS,1000)
    
    data = simulation.init(config)
    simulation.simulate(data, config)
    
    target = data.get_end_simulation_month() - Config.DEFAULT_STARTMONTH
    assert data.get_actual_month() + 1 == target 
    assert data.get_wealth() == 100000 + target*1000
    assert data.get_pk_capital() == 200000 + target*2000
  

    data = simulation.init(config)
    simulation.simulate(data, config)
    
    target = data.get_end_simulation_month() - Config.DEFAULT_STARTMONTH
    assert data.get_actual_month() +1 == target
    assert data.get_wealth() == 100000 + target*1000
    assert data.get_pk_capital() == 200000 + target*2000
    
    config.setValue(Config.GENERAL_ENDAGE, 55)
    config.setValue(Config.PENSION_PRIVATE_INTEREST, {"50": 0.04,"59.75": 0.06, "60.75" : 0.08, "62.75" : 0.06})
    data = simulation.init(config)
    simulation.simulate(data, config)
    
    target = data.get_end_simulation_month() - Config.DEFAULT_STARTMONTH
    assert data.get_actual_month() +1 == target
    assert data.get_wealth() == 100000 + target*1000
    assert round(data.get_pk_capital(),2) == 384521.99
    
    config.setValue(Config.GENERAL_ENDAGE, 62)
    config.setValue(Config.PENSION_PRIVATE_INTEREST, {"50": 0.04,"59.75": 0.06, "60.75" : 0.08, "62.75" : 0.06})
    data = simulation.init(config)
    simulation.simulate(data, config)
    
    target = data.get_end_simulation_month() - Config.DEFAULT_STARTMONTH
    assert data.get_actual_month() +1 == target
    assert data.get_wealth() == 100000 + target*1000
    assert round(data.get_pk_capital(),2) == 768125.40
