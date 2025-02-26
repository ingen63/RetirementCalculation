
from abc import ABC
import logging
import time
from data import Data
from property import Property, PropertyManager
from config import Config
from tax import TaxHandler


class Event(ABC):
    
    
    __month = 0
    
    def __init__(self, month : int):
        self.__month = month
        
    
    def before_method(self, config: Config, data : Data) -> bool:
        return True
        
    
    def after_method(self, config: Config, data : Data) -> bool:
        return True

    
    def get_month(self) -> int :
        return self.__month
    
    def get_name(self) -> str :
        return "Event"
    
    
class StartSimulationEvent(Event):
    
    def get_name(self) -> str :
        return "StartSimulationEvent"
    
    def before_method(self, config: Config, data : Data) -> bool:
        
        # calculate initial wealth
        data.set_wealth(config.getValue(Config.GENERAL_WEALTH,0.0))
        
        # calculate initial private pension capital
        data.set_pk_capital(config.getValue(Config.PENSION_PRIVATE_CAPITAL,0.0))

        
        # calculate initial savings
        data.set_pk_contribution(config.getActualValue(self.get_month(), Config.PENSION_PRIVATE_CONTRIBUTION,0.0))
        
        data.set_savings(config.getActualValue(self.get_month(), Config.MONEYFLOWS_SAVINGS,0.0))
        data.set_inflation(config.getActualValue(self.get_month(), Config.CALCULATION_SINGLE_INFLATION,0.0))
        
        data.set_performance(config.getActualValue(self.get_month(), Config.CALCULATION_SINGLE_PERFORMANCE,0.0))
        
        data.set_threshold_months(round(config.getValue(Config.REALESTATE_THRESHOLDYEARS, Config.DEFAULT_REALESTATE_THRESHOLDYEARS)*Config.MONTHS))
        
        return True
      
class EndSimulationEvent(Event):
    
    __ms = time.time()*1000
    
    def get_name(self) -> str :
        return "EndSimulationEvent"
       
    def after_method(self, config, data) -> bool:
        self.__ms = time.time()*1000 - self.__ms
        logging.info(f"Finished simulation after {self.__ms} ms")
        return True
        


class ChangeValueEvent(Event):
    
    __key = None
    
    def get_name(self) -> str :
        return f"ChangeValueEvent {self.get_key()}"
    
    def __init__(self, month : int, key : str):
        super().__init__(month)
        self.__key = key
        
    def get_key(self) -> str :
        return self.__key
        
    def before_method(self, config, data)  -> bool:
        value = config.getActualValue(self.get_month(), self.__key)   
        if self.__key == Config.MONEYFLOWS_EXTRA :
            data.set_extra(config.best_guess_for_number(value))
        else:
            data.set_value(self.__key, value)
        return True

    def after_method(self, config, data):
        if self.__key == Config.MONEYFLOWS_EXTRA :
            data.set_extra(0.0)
            

    
class EarlyRetirmentEvent(Event) :
    
    def get_name(self) -> str :
        return "EarlyRetirementEvent"
    
    def before_method(self, config: Config, data : Data)  -> bool :
        
        self.__private_pension(config, data)
        
        data.set_spending(config.getActualValue(self.get_month(), Config.MONEYFLOWS_SPENDINGS,0.0))
        data.set_savings(0.0)
        sum = data.get_wealth() + data.get_lumpsum()
        data.set_wealth(sum)
        
        logging.info(f"Early Retirement: Wealth: {data.get_wealth():.2f} Severance Pay: {data.get_extra():.2f} Lumpsum:  {data.get_lumpsum():.2f}  Private Pension: {data.get_private_pension():.2f} ")
        return True
                       
      
    def after_method(self, config, data) -> bool:
        
        # set one time payments back to 0
        data.set_lumpsum(0.0)
        return True
        
       
    def  __private_pension(self, config : Config, data : Data) :
            
        # calculate private pension    
        pk_capital = data.get_pk_capital()
        lumpsum_ratio = config.getValue(Config.PENSION_PRIVATE_LUMPSUMRATIO)
        conversion_rate = config.getValue(Config.PENSION_PRIVATE_CONVERSIONRATE)
        

         
        pension = (pk_capital * (1.0-lumpsum_ratio) * conversion_rate)/Config.MONTHS        # monthly pension
        lumpsum = lumpsum_ratio * pk_capital   
        lumpsum_tax = TaxHandler.lumpsum_tax(config, lumpsum)  
        lumpsum -= lumpsum_tax
                
        logging.debug(f"Private Pension Capital: {pk_capital:.2f}, Lumpsum: {lumpsum_ratio:.2f}, Conversion Rate: {conversion_rate:.2f}")   
         
        data.set_lumpsum(lumpsum) 
        data.set_private_pension(pension)
        data.set_pk_capital(0.0)
        data.set_pk_contribution(0.0)
        

class LegalRetirmentEvent(Event) :
    
    def get_name(self) -> str :
        return "LegalRetirementEvent"
    
    def before_method(self, config: Config, data : Data) -> bool:
        
        data.set_legal_pension(config.getActualValue(self.get_month(), Config.PENSION_LEGAL))
      
        logging.info(f"Legal Retirement: Wealth: {data.get_wealth():.2f} Legal Pension: {data.get_legal_pension():.2f}")
        
class SellPropertyEvent(Event) : 
    
    _id   = None
    _name = None
    
    def get_name(self) -> str :
        return "SellPropertyEvent"
    
    def __init__(self, month : int, property: Property ):
        super().__init__(month)
        self.__id = property.get_id()
        self.__name = property.get_name()
    
    def before_method(self, config: Config, data : Data) -> bool: 
        property = PropertyManager.get_property(self.__id)
        if (property is not None):
             return PropertyManager.sell(property, data)
        logging.debug(f"Property {self.__name} is no longer available.")
        return False

            
        
class BuyPropertyEvent(Event) : 
    
    _id   = None
    _name = None
    
    def get_name(self) -> str :
        return "SellPropertyEvent"
    
    def __init__(self, month : int, property: Property ):
        super().__init__(month)
        self.__id = property.get_id()
        self.__name = property.get_name()
    
    def after_method(self, config: Config, data : Data) : 
        return_value = False
        property = PropertyManager.get_property(self.__id)
        if (property is not None):
            return_value =  PropertyManager.buy(property, data, config)
            if (return_value is True) :
                mortgage_renewal_month =  config.age2months(data.get_actual_age()+property.get_mortage().get_term()) 
                EventHandler.add_event(RenewMortageEvent(mortgage_renewal_month, property))
        logging.debug(f"Property {self.__name} is no longer available.")
        return False
      
class RenewMortageEvent(Event):  
    _id   = None
    _name = None
    
    def get_name(self) -> str :
        return "SellPropertyEvent"
    
    
    def __init__(self, month : int, property: Property ):
        super().__init__(month)
        self.__id = property.get_id()
        self.__name = property.get_name()
        
        
    def before_method(self, config: Config, data : Data) -> bool: 
        return_value = False
        property = PropertyManager.get_property(self.__id)
        if (property is not None):
             return_value =  PropertyManager.renew_mortage(property, data, config)
             if (return_value is True) :
                mortage_renewal_month =  config.age2months(data.get_actual_age()+property.get_mortage().get_term()) 
                EventHandler.add_event(RenewMortageEvent(mortage_renewal_month, property))
        logging.debug(f"Property {self.__name} is no longer available.")
        return return_value
    

        
class EventHandler() :
    
    __events = {}
    
    @staticmethod
    def add_event(event : Event):
        month = event.get_month()
        if (month is None) :
            logging.warning(f"Event {event.get_name()} has no month assigned.")
            return
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