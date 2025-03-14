
from abc import ABC
import logging
import time
from data import Data
from output import Output
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
        data.set_inflation(config.getActualValue(self.get_month(), Config.GENERAL_INFLATION,0.0))
        
        data.set_performance(config.getActualValue(self.get_month(), Config.GENERAL_PERFORMANCE,0.0))
        
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
        value = config.getActualValue(self.get_month(), self.get_key())   
        data.set_value(self.get_key(), value)
        return True
            
class MoneyFlowExtraEvent(Event):
    
    __value = 0.0
    
    def get_name(self) -> str :
        return f"MoneyFlowExtraEvent: {self.get_value()}"
    
    def __init__(self, month : int, value : float):
        super().__init__(month)
        self.__value = value
                
     
    def get_value(self) -> float :
        return self.__value
        
    def before_method(self, config, data)  -> bool:
        data.set_extra(data.get_extra() + self.get_value())
        data.set_wealth(data.get_wealth() + self.get_value())
        return True

    def after_method(self, config, data):
        data.set_extra(0.0)
        return True
    
class LumpsumEvent(Event):
    
    __ratio = 0.0
    
    def get_name(self) -> str :
        return f"LumpsumEvent: {self.get_ratio()}"
    
    def __init__(self, month : int, ratio : float):
        super().__init__(month)
        self.__ratio = ratio
                
     
    def get_ratio(self) -> float :
        return self.__ratio
        
    def before_method(self, config, data)  -> bool:
        lumpsum = self.get_ratio() * data.get_pk_capital()
        data.set_pk_capital(data.get_pk_capital() - lumpsum)
        lumpsum_tax = TaxHandler.lumpsum_tax(config, lumpsum)
        lumpsum -= lumpsum_tax
        data.set_lumpsum(lumpsum)
        data.set_wealth(data.get_wealth()+data.get_lumpsum())
        return True

    def after_method(self, config, data):
        data.set_lumpsum(0.0)
        return True
    
class EarlyRetirmentEvent(Event) :
    
    def get_name(self) -> str :
        return "EarlyRetirementEvent"
    
    def before_method(self, config: Config, data : Data)  -> bool :
        
        Output.add_result(Output.PK_CAPITAL, f"{data.get_pk_capital():.0f} CHF")
        Output.add_result(Output.PK_LUMPSUM_RATIO, f"{data.get_lumpsum_ratio()*100.0:.2f} %")
        Output.add_result(Output.INFLATION_RATE, f"{data.get_inflation()*100.0:.2f} %")
        Output.add_result(Output.INTEREST_RATE, f"{data.get_performance()*100.0:.2f} %")
        
        self.__private_pension(config, data)
        
        logging.info (f"Early Retirement: Wealth: {data.get_wealth():.2f} Severance Pay: {data.get_extra():.2f} Lumpsum:  {data.get_lumpsum():.2f}  Private Pension: {data.get_private_pension():.2f} ")
        logging.getLogger(Config.LOGGER_SUMMARY).info(f"Early Retirment with age of {data.get_actual_age():.2f} and wealth of {data.get_wealth():.0f} CHF with income of {data.get_actual_income():.0f} ")
        
        Output.add_result(Output.WEALTH_EARLY, f"{data.get_wealth():.0f} CHF")
        return True
                       
        
       
    def  __private_pension(self, config : Config, data : Data) :
            
        # calculate private pension    
        pk_capital = data.get_pk_capital()
        lumpsum_ratio = data.get_lumpsum_ratio()           
        conversion_rate = config.getValue(Config.PENSION_PRIVATE_CONVERSIONRATE)
         
        pension = (pk_capital * (1.0-lumpsum_ratio) * conversion_rate)/Config.MONTHS        # monthly pension
        data.set_pk_capital(pk_capital * lumpsum_ratio)
                
        logging.debug(f"Private Pension Capital: {pk_capital:.2f}, Lumpsum: {lumpsum_ratio:.2f}, Conversion Rate: {conversion_rate:.2f}")   
         
        data.set_private_pension(pension)
        data.set_pk_contribution(0.0)
        

class LegalRetirmentEvent(Event) :
    
    def get_name(self) -> str :
        return "LegalRetirementEvent"
    
    def before_method(self, config: Config, data : Data) -> bool:
        
        data.set_legal_pension(config.getActualValue(self.get_month(), Config.PENSION_LEGAL))
      
        logging.info(f"Legal Retirement: Wealth: {data.get_wealth():.2f} Legal Pension: {data.get_legal_pension():.2f}")
        logging.getLogger(Config.LOGGER_SUMMARY).info(f"Legal Retirment with age of {data.get_actual_age():.2f} and wealth of {data.get_wealth():.0f} CHF with income of {data.get_actual_income():.0f} ")
        
        Output.add_result(Output.WEALTH_LEGAL, f"{data.get_wealth():.0f} CHF")
        Output.add_result(Output.PENSION, f"{data.get_legal_pension()+data.get_private_pension():.0f} CHF")
        Output.add_result(Output.SPENDING, f"{data.get_spending()+PropertyManager.get_properties_expenses():.0f} CHF")
        
        
        property =  PropertyManager.get_property_for_sale()
        if property is not None :
            profit = property.get_worth() - property.get_price()
            profit -= TaxHandler.sales_tax(config, property)
        withdrawal_rate = Config.MONTHS * (data.get_spending() - (data.get_legal_pension() + data.get_private_pension())) / (profit + data.get_wealth())
        
        Output.add_result(Output.WITHDRAWAL_RATE, f"{withdrawal_rate*100.0:.2f} %")

        
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
             return PropertyManager.sell(property, data, config)
        logging.debug(f"Property {self.__name} is no longer available.")
        return False

    def after_method(self, config: Config, data : Data) -> bool:

        buy_now = config.getValue(Config.REALESTATE_BUYAFTERSELL) == "True" 
        if PropertyManager.nothing_to_sell() :
            if buy_now is True :
                if PropertyManager.nothing_to_buy() is False:
                    EventHandler.add_event(BuyPropertyEvent(self.get_month()+1, PropertyManager.get_property_to_buy()))
                else :   
                    return PropertyManager.rent(None, data) 
            else :
                return PropertyManager.rent(None, data) 
        return True
                
        
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
                PropertyManager.unrent(data, config)
                return return_value
            
            else :
                if PropertyManager.nothing_to_sell() :  
                    PropertyManager.rent(None, data)
                
        logging.debug(f"Property {self.__name} is no longer available.")
        return False
      
class RenewMortageEvent(Event):  
    _id   = None
    _name = None
    
    def get_name(self) -> str :
        return "RenewPropertyEvent"
    
    
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
                next_mortage_renewal_month =  config.age2months(data.get_actual_age()+property.get_mortage().get_term()) 
                EventHandler.add_event(RenewMortageEvent(next_mortage_renewal_month, property))
            else :  # renewal of mortage has failed, we have to sell the property
                return_value = PropertyManager.sell(property, data, config)
        return return_value
    
class RentPropertyEvent(Event) : 
    
    _id   = None
    _name = None
    
    def get_name(self) -> str :
        return "SellRentPropertyEvent"
    
    def __init__(self, month : int, property: Property ):
        super().__init__(month)
        self.__id = property.get_id()
        self.__name = property.get_name()
    
    def before_method(self, config: Config, data : Data) -> bool: 
        property = PropertyManager.get_property(self.__id)
        if (property is not None):
             return PropertyManager.rent(property, data)
        logging.debug(f"Property {self.__name} is no longer available.")
        return False


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