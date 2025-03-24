from itertools import product
import logging
import re

from config import Config
from output import Output
from simulation import Simulation

class Iterations :
    
    def __init__(self):
        self.iterations = {}
   
   
   
    def iterate(self, reference : Config, overrides : str) :
        
        if reference.getValue(Config.ITERATIONS) is None :
            config = reference.clone()
            config.replace_variables()
            config.override(overrides)
            description = "Single Run"
            self.simulate(config, description)
        else :
            keys = self.iterations.keys()
            values = self.iterations.values()
            
            for kombination in product(*values) : 
                config = reference.clone()
                config.replace_variables()
                config.override(overrides)
                description = ""
                for key, value in zip(keys,kombination) :
                    config.setValue(key, value)
                    value = round(value,2) if isinstance(value, float) else value
                    description = description + f"{key}:{value} "
                self.simulate(config, description)
                       
        print("------------------------------------------------------------------------------------------------")   
            
       
    def simulate(self, config : Config, description : str) :
        simulation = Simulation()
        data = simulation.init(config)
        Output.add_result(Output.DESCRIPTION,description)
        Output.add_result(Output.SCENARIO_NAME,description)
            
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
            
            





