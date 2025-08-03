
import logging
import argparse
import time
from config import Config
from iterations import Iterations
from output import Output

def main(file : str, log_level : int, overrides : str) :
    
    start_time = time.time()*1000
    intialize_logging(log_level)
    
    logging.info("------------------------------------------------------------------------")
    logging.info("          R E T I R E M E N T   S I M U L A T I O N   T O O L           ")
    logging.info("------------------------------------------------------------------------")

    
    if (file is None) :
        file = "./data/config.json"
        
    config = Config().load(file)
    iterations = Iterations()
    iterations.parse_iterations(config)
    iterations.iterate(config, overrides)
        
        
        
    print("------------------------------------------------------------------------------------------------")
    print()
    Output.print(list(range(1,Output.scenario+1)))
    print()
    print("------------------------------------------------------------------------------------------------")
    Output.print_ranking()
    print("------------------------------------------------------------------------------------------------")
    # [best,worth] = Output.get_best_and_worth(f"{Output.SELL_PROPERTY[1]} Haus", 1)
    [best,worth] = Output.get_best_and_worth(f"{Output.TOTAL_ASSETS[1]}", 1)

    Output.print( worth + best)
    print("------------------------------------------------------------------------------------------------")
    
    end_time = time.time()*1000
    duration = end_time - start_time
    if (duration < 1000) :
        print(f"Overall execution time {duration} ms")
    else:
        print(f"Overall execution time {duration/1000:.2f} sec")
        
   #   StatsHandler.shows_statistics()    
    
    
    
            
            
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
    
    