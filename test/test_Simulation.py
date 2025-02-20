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
            "SeverancePay": 88600.0,
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
    
    




def test_simulate_before_retirement_static(config):
    simulation = Simulation()

    __init(config)
    
    data = simulation.init(config)
    simulation.simulate(data, config)
    
    target = data.get_end_simulation_month() - config.getStartMonth() + 1
    assert data.get_actual_month() == data.get_end_simulation_month()
    assert data.get_wealth() == 100000 + target*1000
    assert data.get_pk_capital() == 200000 + target*2000
    
    
    config.setValue(Config.GENERAL_STARTMONTH, 2)
    config.setValue(Config.GENERAL_STARTAGE, 50)
    data = simulation.init(config)
    simulation.simulate(data, config)
    
    target = data.get_end_simulation_month() - config.getStartMonth() + 1
    assert data.get_actual_month() == data.get_end_simulation_month() 
    assert round(data.get_wealth(),2) == 100000.0 + target*1000.0
    assert data.get_pk_capital() == 200000.0 + target*2000-0
  

    config.setValue(Config.GENERAL_STARTMONTH, 0)
    config.setValue(Config.GENERAL_STARTAGE, 50 - 2/12)
    data = simulation.init(config)
    simulation.simulate(data, config)
    
    target = data.get_end_simulation_month() - config.getStartMonth() + 1
    assert data.get_actual_month() == data.get_end_simulation_month()
    assert round(data.get_wealth(),2) == 100000.0 + target*1000.0
    assert round(data.get_pk_capital(),2) == 200000-0 + target*2000.0


    
    
def test_simulate_before_retirement_dynamic(config):
    simulation = Simulation()  
    
    __init(config)
    
    config.setValue(Config.GENERAL_ENDAGE, 55)
    config.setValue(Config.PENSION_PRIVATE_INTEREST, {str(50-2/12): 0.04,"59.75": 0.06, "60.75" : 0.08, "62.75" : 0.06})
    data = simulation.init(config)
    simulation.simulate(data, config)
    
    target = data.get_end_simulation_month() - config.getStartMonth() + 1
    assert data.get_actual_month() == data.get_end_simulation_month()
    assert round(data.get_wealth(),2) == 100000 + target*1000
    assert round(data.get_pk_capital(),2) == 384521.99
    
    config.setValue(Config.GENERAL_ENDAGE, 62)
    config.setValue(Config.PENSION_PRIVATE_INTEREST, {str(50-2/12): 0.04,"59.75": 0.06, "60.75" : 0.08, "62.75" : 0.06})
    data = simulation.init(config)
    simulation.simulate(data, config)
    
    target = data.get_end_simulation_month() - config.getStartMonth() + 1
    assert data.get_actual_month() == data.get_end_simulation_month()
    assert round(data.get_wealth(),2) == 100000 + target*1000
    assert round(data.get_pk_capital(),2) == 768125.40

    config.setValue(Config.BEFORE_SAVINGS, {"40": 1000.0,"55": 1500.0})    
    config.setValue(Config.CALCULATION_PERFORMANCE, {str(50-2/12): 0.04, "60.0" : 0.06})
    data = simulation.init(config)
    simulation.simulate(data, config)
    
    assert data.get_actual_month() == data.get_end_simulation_month()
    assert round(data.get_wealth(),2) == 415207.63
    assert round(data.get_pk_capital(),2) ==  768125.40
    
    data = simulation.init(config)
    simulation.simulate(data, config)
    
    assert data.get_actual_month() == data.get_end_simulation_month()
    assert round(data.get_wealth(),2) == 415207.63
    assert round(data.get_pk_capital(),2) ==  768125.40
    
    config.setValue(Config.GENERAL_ENDAGE, 63.0+2/12)   
    data = simulation.init(config)
    simulation.simulate(data, config)
    
    assert data.get_actual_month() == data.get_end_simulation_month()
    assert round(data.get_wealth(),2) ==  466198.18
    assert round(data.get_pk_capital(),2) == 843292.92
    
 
def test_simulate_early_retirement_dynamic_inflation(config):
    simulation = Simulation()  
    
    __init(config)

    config.setValue(Config.EARLY_AGE, 63.0 + 3/12)    
    config.setValue(Config.GENERAL_ENDAGE, 65.0 - 1/12)
    config.setValue(Config.PENSION_PRIVATE_INTEREST, {str(50-2/12): 0.04,"59.75": 0.06, "60.75" : 0.08, "62.75" : 0.06})  
    config.setValue(Config.BEFORE_SAVINGS, {"40": 1000.0,"55": 1500.0})    
    config.setValue(Config.CALCULATION_PERFORMANCE, {str(50-2/12): 0.04,"60": 0.06}) 
       
    data = simulation.init(config)
    simulation.simulate(data, config)
    
    assert data.get_actual_month() == data.get_end_simulation_month()
    assert round(data.get_wealth(),2) == 870193.08
    assert round(data.get_pk_capital(),2) == 0.00
    
    config.setValue(Config.CALCULATION_INFLATION, {"40": 0.01,"60": 0.02}) 
          
    data = simulation.init(config)
    simulation.simulate(data, config)
    
    assert data.get_actual_month() == data.get_end_simulation_month()
    assert round(data.get_wealth(),2) == 865788.02
    assert round(data.get_pk_capital(),2) == 0.00
    
def test_simulate_legal_retirement_dynamic_inflation(config):
    simulation = Simulation()  
    
    __init(config)

    config.setValue(Config.EARLY_AGE, 63.0 + 3/12)    
    config.setValue(Config.GENERAL_ENDAGE, 65.0)
    config.setValue(Config.PENSION_PRIVATE_INTEREST, {str(50-2/12): 0.04,"59.75": 0.06, "60.75" : 0.08, "62.75" : 0.06})  
    config.setValue(Config.BEFORE_SAVINGS, {"40": 1000.0,"55": 1500.0})    
    config.setValue(Config.CALCULATION_PERFORMANCE, {str(50-2/12): 0.04,"60": 0.06}) 
    config.setValue(Config.CALCULATION_INFLATION, {"40": 0.01,"60": 0.02}) 
       
    data = simulation.init(config)
    simulation.simulate(data, config)
    
    assert data.get_actual_month() == data.get_end_simulation_month()
    assert round(data.get_wealth(),2) == 864387.99
    assert round(data.get_pk_capital(),2) == 0.00

        
    config.setValue(Config.GENERAL_ENDAGE,81)     
    data = simulation.init(config)
    simulation.simulate(data, config)
    
    assert data.get_actual_month() == data.get_end_simulation_month()
    assert round(data.get_wealth(),2) == 80101.96
    assert round(data.get_pk_capital(),2) == 0.00   

def __init(config):
    config.setValue(Config.GENERAL_ENDAGE, 55)
    config.setValue(Config.EARLY_AGE, 63.0 + 3/12)
    config.setValue(Config.CALCULATION_PERFORMANCE,0.0)
    config.setValue(Config.CALCULATION_INFLATION,0.0)
    config.setValue(Config.PENSION_PRIVATE_INTEREST,0.0)
    config.setValue(Config.PENSION_PRIVATE_CONTRIBUTION,2000) 
    config.setValue(Config.BEFORE_SAVINGS,1000)