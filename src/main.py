
from src.util.config import Config
from src.calculations import Calculation

def main():
    config = Config()
    
    config.load("data/config.json")
    data = config.clone().initialize()
    
    calculation = Calculation()
    
    calculation.calculate_pre_retirement(data)
    
    