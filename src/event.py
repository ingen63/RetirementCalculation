
from abc import ABC
import logging
import time
from src.data import Data
from src.util.config import Config
from src.util.utils import Utils




class Event(ABC):
    
    
    __month = 0
    
    def __init__(self, month : int):
        self.__month = month
        
    
    def before_method(self, config: Config, data : Data) :
        pass
        
    
    def after_method(self, config: Config, data : Data) :
        pass
    
    def get_month(self) -> int :
        return self.__month
    
    def get_name(self) -> str :
        return "Event"
    
    
class StartSimulationEvent(Event):
    
    def get_name(self) -> str :
        return "StartSimulationEvent"
    
    def before_method(self, config: Config, data : Data) :
        
        # calculate initial wealth
        data.set_wealth(config.getValue(Config.GENERAL_WEALTH,0.0))
        
        # calculate initial private pension capital
        data.set_pk_capital(config.getValue(Config.PENSION_PRIVATE_CAPITAL,0.0))

        
        # calculate initial savings
        data.set_pk_contribution(config.getActualValue(self.get_month(), Config.PENSION_PRIVATE_CONTRIBUTION,0.0))
        
        data.set_savings(config.getActualValue(self.get_month(), Config.BEFORE_SAVINGS,0.0))
        data.set_inflation(config.getActualValue(self.get_month(), Config.CALCULATION_INFLATION,0.0))
        
        data.set_performance(config.getActualValue(self.get_month(), Config.CALCULATION_PERFORMANCE,0.0))
      
class EndSimulationEvent(Event):
    
    __ms = time.time()*1000
    
    def get_name(self) -> str :
        return "EndSimulationEvent"
       
    def after_method(self, config, data):
        self.__ms = time.time()*1000 - self.__ms
        logging.info(f"Finished simulation after {self.__ms} ms")
        


class ChangeValueEvent(Event):
    
    __key = None
    
    def get_name(self) -> str :
        return f"ChangeValueEvent {self.get_key()}"
    
    def __init__(self, month : int, key : str):
        super().__init__(month)
        self.__key = key
        
    def get_key(self) -> str :
        return self.__key
        
    def before_method(self, config, data):
    
        value = config.getActualValue(self.get_month(), self.__key)
        data.set_value(self.__key, value)

    
class EarlyRetirmentEvent(Event) :
    
    def get_name(self) -> str :
        return "EarlyRetirementEvent"
    
    def before_method(self, config: Config, data : Data) :
        
        self.__private_pension(config, data)
        
        data.set_extra(config.getValue(Config.EARLY_SEVERANCEPAY))
        data.set_spending(config.getActualValue(self.get_month(), Config.EARLY_SPENDING))
        data.set_savings(0.0)
        sum = data.get_wealth() + data.get_extra() + data.get_lumpsum()
        data.set_wealth(sum)
                       
      
    def after_method(self, config, data):
        
        # set one time payments back to 0
        data.set_lumpsum(0.0)
        data.set_extra(0.0)
        
       
    def  __private_pension(self, config : Config, data : Data) :
            
        # calculate private pension    
        pk_capital = data.get_pk_capital()
        lumpsum_ratio = config.getValue(Config.PENSION_PRIVATE_LUMPSUMRATIO)
        lumpsum_taxrate = config.getValue(Config.PENSION_PRIVATE_LUMPSUMTAXRATE)
        conversion_rate = config.getValue(Config.PENSION_PRIVATE_CONVERSIONRATE)
        
        logging.debug(f"Private Pension Capital: {pk_capital:.2f}, Lumpsum: {lumpsum_ratio:.2f}, Lumpsum Tax Rate: {lumpsum_taxrate:.2f}, Conversion Rate: {conversion_rate:.2f}")   
         
        pension = (pk_capital * (1.0-lumpsum_ratio) * conversion_rate)/Utils.MONTH        # monthly pension
        lumpsum = lumpsum_ratio * pk_capital * (1.0 - lumpsum_taxrate)                    # lumpsum pension  
         
        data.set_lumpsum(lumpsum) 
        data.set_private_pension(pension)
        data.set_pk_capital(0.0)
        data.set_pk_contribution(0.0)
        

class LegalRetirmentEvent(Event) :
    
    def get_name(self) -> str :
        return "LegalRetirementEvent"
    
    def before_method(self, config: Config, data : Data) :
        
        data.set_legal_pension(config.getActualValue(self.get_month(), Config.PENSION_LEGAL))
        data.set_spending(config.getActualValue(self.get_month(),Config.LEGAL_SPENDING))
        
   
        
class EventHandler() :
    
    __events = {}
    
    @staticmethod
    def add_event(event : Event):
        month = event.get_month()
        if month not in EventHandler.__events:
            EventHandler.__events[month] = []
        EventHandler.__events[month].append(event)
    
    @staticmethod
    def get_events(month : int) -> list:
        return EventHandler.__events.get(month,[])
    
    @staticmethod
    def reset_events():
        EventHandler.__events = {}
       
    @staticmethod    
    def get_all_events() -> dict:
        return EventHandler.__events
        
    @staticmethod
    def before(month: int,  config: Config, data : Data): 
        events = EventHandler.get_events(month)
        
        for event in events:
            event.before_method(config, data)
            
    @staticmethod
    def after(month: int,  config: Config, data : Data): 
        events = EventHandler.get_events(month)        
        for event in events:
            event.after_method(config, data)