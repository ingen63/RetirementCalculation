from itertools import product
import logging
import re

from config import Config
from output import Output
from simulation import Simulation
from stats import StatsHandler

class Iterations :
    
    def __init__(self):
        self.iterations = {}
   
   
   
    def iterate(self, reference : Config, overrides : str) :
        
        if reference.getValue(Config.ITERATIONS) is None :
            config = reference.clone()
            description = "Single Run"
                        
            config.replace_variables()
            config.override(overrides)
            self.simulate(config, description, "Single Run")
        else :
            keys = self.iterations.keys()
            values = self.iterations.values()
            columns = [0] * len(keys)
            index = {key: i for i, key in enumerate(keys)}
            
            StatsHandler.set_headers(list(keys))
                       
            for kombination in product(*values) : 
                config = reference.clone()

                description = ""
                scenario_name = "\""
                for key, value in zip(keys,kombination) :
                    
                    config.setValue(key, value)
                    columns[index[key]] = value
                    value = round(value,2) if isinstance(value, float) else value
                    description = description + f"{key}:{value} "
                    scenario_name = scenario_name + f"{value} "
                scenario_name +=  "\""
                
                config.replace_variables()
                config.override(overrides)
                StatsHandler.add_row(columns)
                self.simulate(config, description, scenario_name)
                
                       
        print("------------------------------------------------------------------------------------------------")   
           
       
    def simulate(self, config : Config, description : str, scenario_name : str) :
        
                
        Output.add_result(Output.SCENARIO_IDS, scenario_name)
        
        simulation = Simulation()
        data = simulation.init(config)
        Output.add_result(Output.DESCRIPTION,description)
        Output.add_result(Output.SCENARIO_NAME,scenario_name)
            
        simulation.run(data, config)
        
        Output.next_scenario()    
        
    def parse_iterations(self, config): 
        
        self.iterations = {}
        input = config.getValue(Config.ITERATIONS) 
        if input is None :
            return
        
        for key in input.keys():
            self.iterations[key] = self.parse(input[key])
            
        
    def get_iterations(self):
        return self.iterations
     
    def parse(self, input : list[any]) -> list[any]:
        output = []
        
        pattern = r"\s*\(\s*([+-]?(\d+(\.\d+)?|\.\d+))?\s+\.\.\.\s+([+-]?(\d+(\.\d+)?|\.\d+))?\s*\,\s*([+-]?(\d+(\.\d+)?|\.\d+))?\s*\)"


        for item in input:
            
            # Bereichs-Ausdrücke im Format "(start ... stop, step)" erkennen
            if isinstance(item, str) :
                match = re.search(pattern, item)
                if match is not None : 
  
                    start = self.convert(match.group(1)) 
                    stop = self.convert(match.group(4))
                    step = self.convert(match.group(7))
                    while start <= stop :
                        output.append(start)
                        start = round(start + step,10)
                else :
                    logging.info(f"Invalid syntax for range {item} in input {input}. Expected \"(start ... stop, step)\"")
            else:
                # Andere Werte übernehmen
                output.append(item)
                
        return output

    def convert(self, value: str) :
        value = float(value)
        value = int(value) if value.is_integer() else round(value,10)
        return value
            
            





