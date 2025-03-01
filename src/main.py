
import logging
import argparse
from config import Config
from simulation import Simulation


def main(file : str, log_level : int, overrides : str) :
    
    intialize_logging(log_level)
    
    if (file is None) :
        file = "./data/config.json"
    config = Config().load(file)
    override(config, overrides)
    
    simulation = Simulation()
    data = simulation.init(config)
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
    
    