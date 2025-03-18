import json
import pytest
from simulation import Simulation
from config import Config
from event import EventHandler

@pytest.fixture
def config():
    sample_data = {
        "General": {
            "StartAge":50.0,
            "StartMonth" : 3,
            "Wealth": 50000.00  
        },
        
        "Pension": {
            "EarlyRetirement" : 60,
            "LegalRetirement" : 65,
            "Private": {
                "Capital": 10000.0,
                "LumpsumRatio": 0.5,
                "ConversionRate": 0.05, 
                "Contribution":  {"50": 5000.0},
                "Interest": {"50": 0.05}
            },
            "Legal": 2000.0
        },

        "MoneyFlows": {
            "Savings":  {"50": 500.0, "60": 0},
            "Spendings": {"63": 6300, "65": 6500.00},
            "Extra": {"60": 63000.0}
        }
    }
    
    config = Config()
    config.loads(json.dumps(sample_data))
    return config

def test_init(config):
    
    simulation = Simulation()
    
    data = simulation.init(config)
    
    
    events = EventHandler.get_events(config.age2months(50))
    
    assert len(events) == 4
    assert events[0].get_name() == "StartSimulationEvent"
    assert events[1].get_name() == f"ChangeValueEvent {Config.PENSION_PRIVATE_CONTRIBUTION}"
    assert events[2].get_name() == f"ChangeValueEvent {Config.PENSION_PRIVATE_INTEREST}"
    assert events[3].get_name() == f"ChangeValueEvent {Config.MONEYFLOWS_SAVINGS}"
    
    events = EventHandler.get_events(config.age2months(52))   
    assert len(events) == 0

    
    events = EventHandler.get_events(config.age2months(55)) 
    assert len(events) == 0
    
    events = EventHandler.get_events(config.age2months(60))   
    assert len(events) == 4
    assert events[2].get_name() == "EarlyRetirementEvent"
    
    events = EventHandler.get_events(config.age2months(65))   
    assert len(events) == 2
    assert events[1].get_name() == "LegalRetirementEvent"
    assert events[0].get_name() == f"ChangeValueEvent {Config.MONEYFLOWS_SPENDINGS}"
    
    events = EventHandler.get_events(data.get_end_simulation_month())  
    assert len(events) == 1
    assert events[0].get_name() == "EndSimulationEvent"
    
    




def test_simulate_before_retirement_static(config):
    
     
    simulation = Simulation()

    config.setValue(Config.GENERAL_ENDAGE, 55)
    config.setValue(Config.GENERAL_INFLATION,0.0)
    config.setValue(Config.GENERAL_INFLATION,0.0)
    config.setValue(Config.PENSION_PRIVATE_INTEREST,0.0)
    
    data = simulation.init(config)
    simulation.run(data, config)
    
    target = data.get_end_simulation_month() - config.getStartMonth() + 1
    assert data.get_actual_month() == data.get_end_simulation_month()
    assert data.get_wealth() == 50000 + target*500
    assert data.get_pk_capital() == 10000 + target*5000
    
    
    config.setValue(Config.GENERAL_STARTMONTH, 2)
    config.setValue(Config.GENERAL_STARTAGE, 50)
    data = simulation.init(config)
    simulation.run(data, config)
    
    target = data.get_end_simulation_month() - config.getStartMonth() + 1
    assert data.get_actual_month() == data.get_end_simulation_month() 
    assert round(data.get_wealth(),2) == 50000.0 + target*500.0
    assert data.get_pk_capital() == 10000.0 + target*5000
  

    config.setValue(Config.GENERAL_STARTMONTH, 1)
    config.setValue(Config.GENERAL_STARTAGE, 50 - 2/12)
    config.setValue(Config.MONEYFLOWS_SAVINGS,500)
    config.setValue(Config.PENSION_PRIVATE_CONTRIBUTION,1500)
    data = simulation.init(config)
    simulation.run(data, config)
    
    target = data.get_end_simulation_month() - config.getStartMonth() + 1
    assert data.get_actual_month() == data.get_end_simulation_month()
    assert round(data.get_wealth(),2) == 50000.0 + target*500.0
    assert round(data.get_pk_capital(),2) == 10000 + target*1500.0


    
    
def test_simulate_before_retirement_dynamic(config):
    simulation = Simulation()  
    
    config.setValue(Config.PENSION_EARLYRETIREMENT,65)
    config.setValue(Config.PENSION_LEGALRETIREMENT,65)
    config.setValue(Config.GENERAL_ENDAGE, 55)
    config.setValue(Config.GENERAL_PERFORMANCE,0.0)
    config.setValue(Config.GENERAL_INFLATION,0.0)
    config.setValue(Config.MONEYFLOWS_SAVINGS, 500.0)   
    config.setValue(Config.MONEYFLOWS_SPENDINGS, 0.0)
    config.setValue(Config.MONEYFLOWS_EXTRA, {65 : 0.0})
    
    config.setValue(Config.PENSION_PRIVATE_INTEREST, {"40": 0.04,"59.75": 0.06, "60.75" : 0.08, "62.75" : 0.06})
    data = simulation.init(config)
    simulation.run(data, config)
    
    target = data.get_end_simulation_month() - config.getStartMonth() + 1
    assert data.get_actual_month() == data.get_end_simulation_month()
    assert round(data.get_wealth(),2) == 50000 + target*500
    assert round(data.get_pk_capital(),2) == 352978.53
    
    config.setValue(Config.GENERAL_ENDAGE, 62)
    data = simulation.init(config)
    simulation.run(data, config)
    
    target = data.get_end_simulation_month() - config.getStartMonth() + 1
    assert data.get_actual_month() == data.get_end_simulation_month()
    assert round(data.get_wealth(),2) == 50000 + target*500
    assert round(data.get_pk_capital(),2) == 1040433.52
    

    config.setValue(Config.MONEYFLOWS_SAVINGS, {"40": 500.0,"55": 1500.0})    
    config.setValue(Config.GENERAL_PERFORMANCE, {"40": 0.04, "60" : 0.06})
    data = simulation.init(config)
    simulation.run(data, config)
    
    assert data.get_actual_month() == data.get_end_simulation_month()
    assert round(data.get_wealth(),2) == 281584.24
    assert round(data.get_pk_capital(),2) == 1040433.52
    
    data = simulation.init(config)
    simulation.run(data, config)
    
    assert data.get_actual_month() == data.get_end_simulation_month()
    assert round(data.get_wealth(),2) == 281584.24
    assert round(data.get_pk_capital(),2) == 1040433.52
    
    config.setValue(Config.PENSION_EARLYRETIREMENT,65)
    config.setValue(Config.PENSION_LEGALRETIREMENT,65)
    
    config.setValue(Config.GENERAL_ENDAGE, 65-1/12)   
    data = simulation.init(config)
    simulation.run(data, config)
    
    assert data.get_actual_month() == data.get_end_simulation_month()
    assert round(data.get_wealth(),2) == 391110.91
    assert round(data.get_pk_capital(),2) == 1433784.70
    
 
def test_simulate_early_retirement_dynamic_inflation(config):
    simulation = Simulation()  
    

    config.setValue(Config.PENSION_EARLYRETIREMENT,63) 
    config.setValue(Config.GENERAL_ENDAGE, 65.0 - 1/12)
    config.setValue(Config.MONEYFLOWS_SAVINGS, {"40": 500.0,"55": 1500.0})    
    config.setValue(Config.GENERAL_PERFORMANCE, {"40": 0.04, "60" : 0.06})
    config.setValue(Config.PENSION_PRIVATE_INTEREST, {"40": 0.04,"59.75": 0.06, "60.75" : 0.08, "62.75" : 0.06})
    config.setValue(Config.GENERAL_INFLATION,0.0)
    config.setValue(Config.MONEYFLOWS_EXTRA, {63 : 63000.0})
       
    data = simulation.init(config)
    simulation.run(data, config)
    
    assert data.get_actual_month() == data.get_end_simulation_month()
    assert round(data.get_wealth(),2) ==  976567.33
    assert round(data.get_pk_capital(),2) == 0.00
    
    config.setValue(Config.GENERAL_INFLATION, {"40": 0.01,"60": 0.02}) 
          
    data = simulation.init(config)
    simulation.run(data, config)
    
    assert data.get_actual_month() == data.get_end_simulation_month()
    assert round(data.get_wealth(),2) == 1014841.7 
    assert round(data.get_pk_capital(),2) == 0.00
    
def test_simulate_legal_retirement_dynamic_inflation(config):
    simulation = Simulation()  
    
    config.setValue(Config.PENSION_EARLYRETIREMENT,63) 
    config.setValue(Config.GENERAL_ENDAGE, 65.0 )
    config.setValue(Config.MONEYFLOWS_SAVINGS, {"40": 500.0,"55": 1500.0})  
    config.setValue(Config.MONEYFLOWS_SPENDINGS, {"63": 6300, "65": 6500.00})  
    config.setValue(Config.GENERAL_PERFORMANCE, {"40": 0.04, "60" : 0.06})
    config.setValue(Config.PENSION_PRIVATE_INTEREST, {"40": 0.04,"59.75": 0.06, "60.75" : 0.08, "62.75" : 0.06})
    config.setValue(Config.GENERAL_INFLATION, {"40": 0.01,"60": 0.02}) 
    config.setValue(Config.MONEYFLOWS_EXTRA, {63 : 63000.0})
       
    data = simulation.init(config)
    simulation.run(data, config)
    
    assert data.get_actual_month() == data.get_end_simulation_month()
    assert round(data.get_wealth(),2) == 975903.56
    assert round(data.get_pk_capital(),2) == 0.00

        
    config.setValue(Config.GENERAL_ENDAGE,81)     
    data = simulation.init(config)
    simulation.run(data, config)
    
    assert data.get_actual_month() == data.get_end_simulation_month()
    assert round(data.get_wealth(),2) == 1596657.21
    assert round(data.get_pk_capital(),2) == 0.00   

