


import logging
import uuid
from typing import List
from src.data import Data
from src.util.config import Config
from src.util.utils import Utils


class Mortage :
    
    PERIOD = 4
    
    DEFAULT_AFFORDABILITY_SUSTAINABILITY = 1.0/3.0
    DEFAULT_AFFORDABILITY_MORTAGEINTEREST = 0.05
    DEFAULT_AFFORDABILITY_CAPITALCONTRIBUTION = 0.03
    DEFAULT_AFFORDABILITY_FIXCOSTS = 0.01
    
    DEFAULT_MORTAGE_TERM = 10
    
    
    
    __value = 0.0
    __interest = 0.0
    __start = 0.0
    __term = 0.0
    __regular_amortization = 0.0
        
    
    def get_value(self) -> float :
        return self.__value
    
    def set_value(self, value : float) :
        self.__value = value
        
    def get_interest(self) -> float :
        return self.__interest
    
    def set_interest(self, interest : float) :
        self.__interest = interest
        
    def get_start(self) -> float :
        return self.__start
    
    def set_start(self, start : float) :
        self.__start = start
        
    def get_term(self) -> float :
        return self.__term
    
    def set_term(self, term : float) :
        self.__term = term
        
    def get_end(self) -> float :
        return self.get_start() + self.get_term()
        
    def get_regular_amortization(self) -> float :
        return self.__regular_amortization
    
    def set_regular_amortization(self, amortization : float) :
        self.__regular_amortization = amortization
        
    def get_costs(self) -> float :
        interest = (1.0 + self._get_interest())**(1.0/ Mortage.PERIOD) 
        return (self.get_value()*interest + self.get_regular_amortization())/Mortage.PERIOD

    def regular_amortization(self) -> float :
        value = self.get_value()
        value = value - self.get_regular_amortization()
        self.set_value(max(value, 0.0)) 
        

class Property :
    
    NAME = "Name"
    WORTH = "Worth"
    PRICE  = "Price"
    BUY = "Buy"
    SELL = "Sell"
    MORTAGE = "Mortage"
    FIXCOSTS = "FixCosts"
    PLANNED_REGULAR_AMORTIZATION = "Regular_Amortization"
    MORTAGE_INTEREST = "MortageInterest"
    MORTAGE_START = "MortageStart"
    MORTAGE_TERM = "MortageTerm"
   
    
    OWNED = "Owned"
    PLANNED = "Planned"
    SOLD =  "Sold"
    
    OWN_FUNDS = 0.2
    
    
    __id = None
    __name = None
    __status = None
    __price  = 0.0
    __worth = 0.0
    __buy_age = 0.0
    __sell_age = 0.0
    __mortage = None
    __fix_costs = 0.0
    __regular_amortization = 0.0
    __planned_mortage_interest = 0.0
    __planned_mortage_term = 0.0
    
    
    def __init__(self, config : Config, property_config : dict) :
        self.__id = uuid.uuid4()
        self.__name = property_config.get(Property.NAME,f"Property {id}")
        self.__price = property_config.get(Property.PRICE,1.0)
        self.__worth = property_config.get(Property.WORTH,self.get_price())
        self.__buy_age = property_config.get(Property.BUY,0.0)
        self.__sell_age = property_config.get(Property.SELL,config.getEndAge()+1)
        self.__planned_regular_amortization = property_config.get(Property.PLANNED_REGULAR_AMORTIZATION,0.0)
        self.__fix_costs = property_config.get(Property.FIXCOSTS, Mortage.DEFAULT_AFFORDABILITY_FIXCOSTS * self.get_price())
        self.__planned_mortage_interest = property_config.get(Property.MORTAGE_INTEREST, Mortage.DEFAULT_AFFORDABILITY_MORTAGEINTEREST)
        self.__planned_mortage_term = property_config.get(Property.MORTAGE_TERM, Mortage.DEFAULT_MORTAGE_TERM)
        
        if config.getStartAge() > self.get_buy_age() :
            self.set_status(Property.OWNED)
        else :
            self.set_status(Property.PLANNED)
            
        if (config.getStartAge()) > self.get_sell_age() :
            self.set_status(Property.SOLD)
    

    
    def get_id(self) -> str :
        return self.__id        
    
    def get_name(self) -> str :
        return self.__name
  
    def get_status(self) -> str :
        return self.__status
    
    def set_status(self, status : str) :
        self.__status = status
       
    def get_price(self) -> float :   
        return self.__price
    
    def get_worth(self) -> float :
        return self.__worth
    
    def set_worth(self, worth : float) :
        self.__worth = worth
    
    def get_buy_age(self) -> float :
        return self.__buy_age
        
    def get_sell_age(self) -> float :
        return self.__sell_age
        
    def get_mortage(self) -> Mortage :
        return self.__mortage
    
    def set_mortage(self, mortage : Mortage) :
        self.__mortage = mortage
        
    def get_fix_costs(self) -> float :
        return self.__fix_costs
    
    def set_fix_costs(self, fix_costs : float) :
        self.__fix_costs = fix_costs
        
    def get_planned_mortage_interest(self) -> float :
        return self.__planned_mortage_interest
    
    def  get_planned_mortage_term(self)  -> float :
        return self.__planned_mortage_term
    
    def get_planned_regular_amortization(self) -> float :
        return self.__planned_regular_amortization
        
    
    def calculate_property_costs(self) -> float :
        costs = self.get_fix_costs() + self.get_mortage().get_costs()
        return costs

    
    
    
class PropertyManager :
    
    __owned = []
    __planned = []
    __sold = []
    
    @staticmethod
    def reset() -> None :
        PropertyManager.__owned = []
        PropertyManager.__planned = []
        PropertyManager.__sold = []
    
    @staticmethod
    def add_property(property : Property) :
        if property.get_status() == Property.OWNED :
           PropertyManager.__owned.append(property)
        if property.get_status() == Property.PLANNED :
           PropertyManager.__planned.append(property)
        if property.get_status() == Property.SOLD :
           PropertyManager.__sold.append(property)
           
    @staticmethod
    def remove_property(property : Property) :
        if property.get_status() == Property.OWNED :
           PropertyManager.__owned.remove(property)
        if property.get_status() == Property.PLANNED :
           PropertyManager.__planned.remove(property)
        if property.get_status() == Property.SOLD :
           PropertyManager.__sold.remove(property)
    @staticmethod
    def get_property_for_sale() -> Property :
        if len(PropertyManager.__owned) == 0 :
            return None
        return PropertyManager.sort(PropertyManager.__owned)[0] 
    
    @staticmethod
    def get_property_to_buy() -> Property :
        if len(PropertyManager.__planned) == 0 :
            return None
        return PropertyManager.sort(PropertyManager.__planned)[0] 
            
       
    @staticmethod
    def sort(input : list[Property]) -> list[Property] :
        return sorted(input, key=lambda obj: (obj.get_buy_age(), 1.0/obj.get_worth() ))
    
    @staticmethod
    def sell(property : Property) -> None :
        if property.get_status() != Property.OWNED :
            return None
        
        mortage_value = 0
        if property.get_mortage() is not None :
            mortage_value = property.get_mortage().get_value()
            
        value = property.get_worth() - mortage_value
        PropertyManager.__owned.remove(property)
        
        property.set_status(Property.SOLD)  # mark as sold
        PropertyManager.__sold.append(property)
        
        return value
    
    @staticmethod   
    def buy(property : Property, data : Data, config : dict) -> bool :
        if property.get_status() != Property.PLANNED :
            return False
        
        mortage =  PropertyManager.mortage(property, data, config)
              
        if (mortage is None) :
            return False
        
        property.set_mortage(mortage)
        property.set_status(Property.OWNED)  # mark as owned
        property.set_buy_age((data.get_actual_month()-data.get_start_simulation_month())/Utils.MONTH + data.get_start_age())
        PropertyManager.__planned.remove(property)
        property.set_status(Property.OWNED)  # mark as owned
        PropertyManager.__owned.append(property)
        
        return True

        
    @staticmethod
    def mortage(property : Property,  data : Data, config : Config) -> Mortage :
        

        worth = property.get_worth()
        wealth = data.get_wealth()
        max_mortage = PropertyManager.max_mortage(property, data, config)
        
        renew = False if property.get_mortage() is None else True
        own_funds = 0.0 if renew  else worth * Property.OWN_FUNDS
        
        if (wealth < own_funds ) :  # not enough minimum own funds
            return None
        
        if (renew) :
            mortage = property.get_mortage()
            amortization = mortage.get_value() - max_mortage
            if (wealth - amortization) < 0.0 :
                return None
        
        mortage = Mortage()
        mortage.set_value(max_mortage)
        mortage.set_start(data.get_actual_age())
        mortage.set_interest(property.get_planned_mortage_interest())
        mortage.set_term(property.get_planned_mortage_term())
        
        return mortage


    @staticmethod 
    def max_mortage(property : Property, data : Data, config : Config  ) -> float :
        sustanability = config.getValue(Config.REALESTATE_AFFORDABILITY_SUSTAINABILITY,Mortage.DEFAULT_AFFORDABILITY_SUSTAINABILITY)
        interest = config.getValue(Config.REALESTATE_AFFORDABILITY_MORTAGEINTEREST, Mortage.DEFAULT_AFFORDABILITY_MORTAGEINTEREST)
        capital_contribution = config.getValue(Config.REALESTATE_AFFORDABILITY_CAPITALCONTRIBUTION, Mortage.DEFAULT_AFFORDABILITY_CAPITALCONTRIBUTION)
        fix_costs = property.get_fix_costs()
        mortage = property.get_mortage().get_value() if property.get_mortage() is not None else 0.0
        
        wealth  = data.get_wealth()
        income = (data.get_legal_pension() + data.get_private_pension())*Utils.MONTH
        
        new_wealth = wealth
        new_max_mortage = 0.0
        max_legal_mortage =   property.get_worth()*(1.0-Property.OWN_FUNDS)
        
        i = 0
        while (True) :
            max_mortage = (sustanability * (income + new_wealth * capital_contribution) - fix_costs) / interest   
           
            if abs(new_max_mortage - max_mortage) < 0.001 :
                return max_mortage if (max_mortage < max_legal_mortage) else max_legal_mortage  # if we've reached or exceeded the legal mortgage limit, return that instead of the calculated max mortage
            
            amortization = max(0,mortage - max_mortage)  # in CH you cant get more wealth by increasing ypur mortage
            new_wealth = max(0, wealth - amortization)  # make sure not to go into negative wealth
            new_max_mortage = max_mortage  # update the new max_mortage before the next iteration
            i += 1
            if i > 1000 :
                logging.error(f"Too many iterations in amortization calculation for property {property.get_name()}")
                return -1  # we've gone too far in the loop, something is wrong.  Returning -1 to indicate failure.
            
        return -1

    def get_owned_properties() -> List[Property] :
        return PropertyManager.sort(PropertyManager.__owned)
    
    def get_planned_properties() -> List[Property] :
        return PropertyManager.sort(PropertyManager.__planned)
    
    def get_sold_properties() -> List[Property] :
        return PropertyManager.sort(PropertyManager.__sold)


    