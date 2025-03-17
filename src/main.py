
import logging
import argparse
from config import Config
from historical import HistoricalData
from output import Output
from simulation import Simulation


def main(file : str, log_level : int, overrides : str) :
    
    intialize_logging(log_level)
    
    logging.info("------------------------------------------------------------------------")
    logging.info("          R E T I R E M E N T   S I M U L A T I O N   T O O L           ")
    logging.info("------------------------------------------------------------------------")

    
    if (file is None) :
        file = "./data/config.json"
    config = Config().load(file)
    config.replace_variables()
    override(config, overrides)
    
    if config.getValue(Config.CALCULATION_METHOD) == "Single":
        Output.add_result(Output.SCENARIO_NAME,"Single simulation")

        start_single_simulation(config)
        
    elif config.getValue(Config.CALCULATION_METHOD) == "Scenarios":
        scenarios(config)
    elif config.getValue(Config.CALCULATION_METHOD) == "Historical" :
        historical_scenarios(config)
    else:
        logging.error(f"Unsupported calculation method '{config.getValue(Config.CALCULATION_METHOD)}'")
        
        
    print(" ------------------------------------------------------------------------------------------------")
    print()
    Output.print(list(range(1,Output.columns)))
    print()
    print("------------------------------------------------------------------------------------------------")
    Output.print_ranking()
    print("------------------------------------------------------------------------------------------------")
    Output.print_selected(Output.get_best_and_worth(Output.WEALTH[1], 2))
    print("------------------------------------------------------------------------------------------------")
    
def scenarios(config : Config): 
    
    scenarios = config.getValue(Config.CALCULATION_SCENARIOS)
    Output.set_scenarios(len(scenarios))
    for scenario in scenarios: 
        scenarion_config = config.clone()

        scenarion_config.setValues(scenario[Config.CALCULATION_SCENARIOS_PARAMETERS])
        Output.add_result(Output.SCENARIO_NAME,scenario[Config.CALCULATION_SCENARIOS_NAME])
        start_single_simulation(scenarion_config) 
        Output.next_scenario()
        
def historical_scenarios(reference : Config):
    config = reference.clone()
    
    config.setValue(Config.GENERAL_STARTAGE, config.getValue(Config.CALCULATION_HISTORICAL_STARTAGE,config.getEarlyRetirementAge()))
    config.setValue(Config.GENERAL_STARTMONTH, config.getValue(Config.CALCULATION_HISTORICAL_STARTMONTH,config.age2months(config.getEarlyRetirementAge())))
    config.setValue(Config.GENERAL_ENDAGE, config.getValue(Config.CALCULATION_HISTORICAL_ENDAGE,config.getStartAge()+30))
    historical_years = config.getValue(Config.CALCULATION_HISTORICAL_YEAR,None)
    
    if historical_years is not None and not isinstance(historical_years, list) : 
      historical_years = [historical_years]
    
    simulation_years = int(config.getEndAge() - config.getStartAge())+1
    
    length = HistoricalData.load(config.getValue(Config.CALCULATION_HISTORICAL_DATA))
    balance = config.getValue(Config.CALCULATION_HISTORICAL_PORTFOLIOBALANCE,0.5)
    
    
    end = length - simulation_years
    
    historical_index = []
    if  historical_years is None :
        for index in range(0, end) :
            historical_index.append(index)  
    else :
         
        for year in historical_years :
            if year + simulation_years > HistoricalData.years[-1] :
                logging.error(f"Historical data does not cover all data between start year {year} end end year {year + simulation_years}")
                return
            index = HistoricalData.get_index(year)
            if  index is None :
                logging.error(f"Historical data does not cover year {year}")
            historical_index.append(index)  

    Output.set_scenarios(len(historical_index))
    
    
    
    for index in historical_index:
        performance_list = HistoricalData.get_performance(balance, index, index + simulation_years)
        inflation_list = HistoricalData.get_inflation(index, index + simulation_years)
        years = HistoricalData.get_years(index, index + simulation_years)
       
        year = config.getStartAge()
        performance = {}
        inflation = {}
        for i in range(simulation_years):
            performance[str(year + i)] = performance_list[i]
            inflation[str(year + i)] = inflation_list[i]
        
        config.setValue(Config.GENERAL_PERFORMANCE, performance)
        config.setValue(Config.GENERAL_INFLATION, inflation)
        
        Output.add_result(Output.SCENARIO_NAME,f"Historical Simulation: {years[0]}")
        start_single_simulation(config, years[0]) 
        Output.next_scenario()
        
           
    
def start_single_simulation(config: Config, historical_year: int = None) :
    simulation = Simulation()
    data = simulation.init(config, historical_year)
    Output.add_result(Output.DESCRIPTION,f"Age: {config.getEarlyRetirementAge() : .2f} Ratio: {data.get_lumpsum_ratio()*100: .2f}%")
    simulation.run(data, config)
    
    
def override(config : Config, overrides : str) :
    if (overrides is None) :
        return
    keys = overrides.split(',')
    for key in keys:
        key, value = key.split(':')
        
        if config.exists(key) :
            # try to convert it to int or float
            old_value = config.setValue(key, value)
            logging.info(f"Overriding value '{old_value}' for '{key}' with '{value}'")
            
            
def intialize_logging(log_level : int,):
    logging.basicConfig(level=log_level, force=True)
    
    logger = logging.getLogger(Config.LOGGER_SUMMARY)
    logger.setLevel(logging.INFO)
 
   # Create a file handler to log messages to a file
    handler = logging.FileHandler('summary.log', "w")
    handler.setLevel(logging.INFO)

    # Define the log message format
    formatter = logging.Formatter('%(message)s')
    handler.setFormatter(formatter)

    # Attach the handler to the logger
    logger.addHandler(handler)


    
    
            
if __name__=="__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", help = "Input file to be used for simulation. Default is ./data/config.json", default="./data/config.json")
    parser.add_argument("--log", help = "set log level, default is INFO", default=logging.INFO)
    parser.add_argument("-o", "--overrides", help = "To override keys from the given config file. Format is 'key1 : value1, key2 : value2,...'")
    args = parser.parse_args()
    main(args.file, args.log, args.overrides)
    
    