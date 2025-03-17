
import copy
import logging
import uuid
from typing import List
from config import Config
from data import Data
from output import Output




class Mortage :
    
    PERIOD = 4
    
    DEFAULT_AFFORDABILITY_SUSTAINABILITY = 1.0/3.0
    DEFAULT_AFFORDABILITY_MORTAGEINTEREST = 0.05
    DEFAULT_AFFORDABILITY_CAPITALCONTRIBUTION = 0.03
    DEFAULT_AFFORDABILITY_FIXCOSTS = 0.01  
    DEFAULT_MORTAGE_TERM = 10
    
    
    def __init__(self, property_config : Config = None) :
        
        if property_config is None : 
            property_config = Config()
        
        self.set_value(property_config.getValue(Property.MORTAGE_VALUE, 0.0))
        self.set_interest(property_config.getValue(Property.MORTAGE_INTEREST, Mortage.DEFAULT_AFFORDABILITY_MORTAGEINTEREST))
        self.set_start_age(property_config.getValue(Property.MORTAGE_STARTAGE, None))
        self.set_term(property_config.getValue(Property.MORTAGE_TERM, Mortage.DEFAULT_MORTAGE_TERM))
        self.set_amortization(property_config.getValue(Property.MORTAGE_AMORTIZATION,0.0))
        
    
    def get_value(self) -> float :
        return self.__value
    
    def set_value(self, value : float) :
        self.__value = value
        
    def get_interest(self) -> float :
        return self.__interest
    
    def set_interest(self, interest : float) :
        self.__interest = interest
        
    def get_start_age(self) -> float :
        return self.__start_age
    
    def set_start_age(self, start_age : float) :
        self.__start_age = start_age
        
    def get_term(self) -> float :
        return self.__term
    
    def set_term(self, term : float) :
        self.__term = term
        
    def get_end_age(self) -> float :
        return self.get_start_age() + self.get_term()
        
    def get_amortization(self) -> float :
        return self.__amortization
    
    def set_amortization(self, amortization : float) :
        self.__amortization = amortization
        
    def get_costs(self) -> float :
        interest = (1.0 + self.get_interest())**(1.0/ Config.MONTHS) - 1.0
        return self.get_value()*interest + self.get_amortization()/Mortage.PERIOD
        

class Property :
    
    NAME = "Name"
    STATUS = "Status"
    WORTH = "Worth"
    PRICE  = "Price"
    BUYAGE = "BuyAge"
    SELLAGE = "SellAge"
    FIXCOSTS = "FixCosts"
    RENTALINCOME = "RentalIncome"
    MORTAGE = "Mortage"
    MORTAGE_VALUE = "Mortage.Value"
    MORTAGE_INTEREST = "Mortage.Interest"
    MORTAGE_STARTAGE = "Mortage.StartAge"
    MORTAGE_TERM = "Mortage.Term"
    MORTAGE_AMORTIZATION = "Mortage.Amortization"
    
    OWNED = "Owned"
    PLANNED = "Planned"
    SOLD =  "Sold"
    RENTED = "Rented"
    PLANNED_FOR_RENT = "PlannedForRent"
    
    OWN_FUNDS = 0.2
    
    
    def __init__(self, property_config : Config) :
        
        self.__id = uuid.uuid4()
        self.__name =  property_config.getValue(Property.NAME,f"Name-{self.get_id()}")
        self.set_status(property_config.getValue(Property.STATUS, Property.PLANNED))
        self.set_price(property_config.getValue(Property.PRICE,0.0))
        self.set_worth(property_config.getValue(Property.WORTH,self.get_price()))
        self.set_buy_age(property_config.getValue(Property.BUYAGE,Config.MAX_AGE))
        self.set_sell_age(property_config.getValue(Property.SELLAGE, Config.MAX_AGE))
        self.set_rental_income(property_config.getValue(Property.RENTALINCOME,0.0))
        self.set_fix_costs(property_config.getValue(Property.FIXCOSTS, self.get_price()*Mortage.DEFAULT_AFFORDABILITY_FIXCOSTS/Config.MONTHS))
        if (self.get_status() == Property.OWNED or self.get_status() == Property.PLANNED) :
            self.set_mortage(Mortage(property_config))
        else :
            self.__mortage = None
        

    
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
        
    def set_price(self, price : float) :
        self.__price = price
    
    def get_worth(self) -> float :
        return self.__worth
    
    def set_worth(self, worth : float) :
        self.__worth = worth
    
    def get_buy_age(self) -> float :
        return self.__buy_age
    
    def set_buy_age(self, buy_age : float) :
        self.__buy_age = buy_age
        
    def get_sell_age(self) -> float :
        return self.__sell_age
        
    def set_sell_age(self, sell_age : float) :
         self.__sell_age = sell_age
    
    def get_mortage(self) -> Mortage :
        return self.__mortage
    
    def set_mortage(self, mortage : Mortage) :
        self.__mortage = mortage
        
    def get_fix_costs(self) -> float :
        return self.__fix_costs
    
    def set_fix_costs(self, fix_costs : float) :
        fix_costs = Mortage.DEFAULT_AFFORDABILITY_FIXCOSTS*self.get_price()/Config.MONTHS if fix_costs is None else fix_costs
        self.__fix_costs = fix_costs
        
    def get_rental_income(self) -> float :
        return self.__rental_income
        
    def set_rental_income(self, rental_income : float) :
        rental_income = 0.0 if (rental_income is None) else rental_income
        self.__rental_income = rental_income
    
    def get_property_costs(self) -> float :
        mortage_costs = 0.0 if self.get_mortage() is None else self.get_mortage().get_costs()
        return self.get_fix_costs() + mortage_costs
    
    
    
class PropertyManager :
    
    __properties = []
    __expenses = {}
    
    @staticmethod
    def reset() -> None :
        PropertyManager.__properties = []
        PropertyManager.__expenses = {}
        
    
    @staticmethod
    def add_property(property : Property) :
        PropertyManager.__properties.append(property)
        if property.get_status() == Property.OWNED or property.get_status() == Property.RENTED:
            PropertyManager.add_expenses(property)
       
           
    @staticmethod
    def remove_property(property : Property) :
        PropertyManager.__properties.remove(property)  
        PropertyManager.remove_expenses(property)   
        
           

    @staticmethod
    def get_properties_expenses() -> float :
        expenses = 0.0
        for expense in PropertyManager.__expenses.values() :
            expenses += expense
            
        return expenses
    
    @staticmethod
    def add_expenses(property : Property) :
       PropertyManager.__expenses[property.get_id()] = property.get_property_costs() - property.get_rental_income()
       
    @staticmethod
    def remove_expenses(property : Property) :
       PropertyManager.__expenses[property.get_id()] = 0.0
        
    @staticmethod
    def get_property_for_sale(count : int = 0 ) -> Property :
        properties =  PropertyManager.__sort(PropertyManager.__filter(PropertyManager.__properties,Property.OWNED),False)
        return None if len(properties) < count+1 else properties[count] 
   
    @staticmethod 
    def nothing_to_sell() -> bool :
        return True if PropertyManager.get_property_for_sale() is None else False
    
    @staticmethod 
    def nothing_to_buy() -> bool :
        return True if PropertyManager.get_property_to_buy() is None else False
    
    @staticmethod
    def get_property_to_buy(count : int = 0 ) -> Property :  
        properties =  PropertyManager.__sort(PropertyManager.__filter(PropertyManager.__properties,Property.PLANNED),False)
        return None if len(properties) < count+1 else properties[count] 

            
    def get_property(id : str) -> Property :
        for property in PropertyManager.__properties :
            if property.get_id() == id :
                return property
        return None        
       
    @staticmethod
    def __filter(input : list[Property], status : str) -> list[Property] :
        if len(input) == 0 : 
           return []
        return list(filter(lambda obj: obj.get_status() == status, input))
    
    
    @staticmethod
    def __sort(input : list[Property], low2high : bool) -> list[Property] :
        if len(input) == 0:
            return []
        return sorted(input, key=lambda obj: (obj.get_buy_age(),  obj.get_worth() if low2high else -1.0*obj.get_worth() ))   # sort by time to sell (Buy_age and then for price. Less worth first)

        
    @staticmethod
    def sell(property : Property, data: Data, config: Config) -> bool:
        from tax import TaxHandler
        
        if property.get_status() != Property.OWNED :
            logging.debug(f"Cannot sell property {property.get_name()} as it is no longer available.")
            return False
        # add inflation correction
        property.set_worth(property.get_worth()*data.get_inflation_correction())
        property.set_status(Property.SOLD)
        PropertyManager.remove_expenses(property)
        mortage = 0.0 if property.get_mortage() is None else property.get_mortage().get_value()
        profit = property.get_worth() - property.get_price()
        tax  = TaxHandler.sales_tax(config, property) 
        
        data.set_wealth(data.get_wealth() + property.get_worth() - mortage - tax) 
        logging.info (f"Sell {property.get_name()} --> Age: {data.get_actual_age():5.2f} Wealth: {data.get_wealth():7.0f} CHF Worth: {property.get_worth() : 7.0f} CHF Profit: {profit-tax:7.0f} CHF")
        Output.add_result(Output.SELL_PROPERTY, f"Age: {data.get_actual_age():.2f}", f"{Output.SELL_PROPERTY[1]} {property.get_name()}")
        Output.add_sell(data.get_historical_year(), property.get_name(), data.get_actual_age())
        
        
     
    
    @staticmethod   
    def buy(property : Property, data : Data, config : Config) -> bool :
        if property.get_status() != Property.PLANNED :
            logging.debug(f"Cannot buy property {property.get_name()} as it is no longer available.")
            return False
        
        price = property.get_price()
        
        property.set_price(property.get_price()*data.get_inflation_correction())

        mortage =  PropertyManager.mortage(property, data, config)
              
        if mortage is None :
            logging.debug(f"No mortage from the banks for property {property.get_name()} due to lack of wealth and income.")  # if wealth is not enough to afford mortgage, we can't buy property.  # if income is not enough to afford mortgage, we can't buy property.  # if both are not enough, we can't buy property.  # if mortgage is already paid off, we can't buy property.
            property.set_price(price)
            return False
        else :   
            new_wealth =  data.get_wealth() - (property.get_price() - mortage.get_value())
            
            if (new_wealth < 0.0) :
                logging.debug(f"Mortage would be granted from the banks for property {property.get_name()}, but still not enough wealth.")
                return False
                      
            property.set_mortage(mortage)
            property.set_status(Property.OWNED)  # mark as owned
            property.set_buy_age(config.month2age(data.get_actual_month()))
            PropertyManager.add_expenses(property)
            data.set_wealth(new_wealth)
            
        logging.info (f"Buy {property.get_name()} --> Age: {data.get_actual_age():5.2f} Wealth: {data.get_wealth():7.0f} CHF Price: {property.get_price() : 7.0f} CHF Mortage: {property.get_mortage().get_value():7.0f} CHF")
        Output.add_result(Output.BUY_PROPERTY, f"Age: {data.get_actual_age():.2f}", f"{Output.BUY_PROPERTY[1]} {property.get_name()}")
  
        
        return True

    @staticmethod
    def renew_mortage(property : Property, data : Data, config : Config) -> bool :
        if property.get_status() != Property.OWNED :
            logging.debug(f"Cannot renew {property.get_name()} as it is no longer owned by yourself.")
            return False
        
        new_mortage =  PropertyManager.mortage(property, data, config)
        
        if (new_mortage is None) :
            logging.debug(f"Mortgage cant be renewed for {property.get_name()} due to lack of wealth and income.")
            return False
        else :
            amortization = property.get_mortage().get_value() - new_mortage.get_value()
            property.set_mortage(new_mortage)
            PropertyManager.add_expenses(property)
            data.set_wealth(data.get_wealth() - amortization)
            logging.info (f"Mortage {property.get_name()} --> Age: {data.get_actual_age():5.2f} Wealth: {data.get_wealth():7.0f} CHF Amortization: {amortization : 7.0f} CHF ")
        return True
        
        
    @staticmethod
    def mortage(property : Property,  data : Data, config : Config) -> Mortage :
        
        new_mortage = copy.deepcopy(property.get_mortage())
        
        max_mortage = PropertyManager.max_mortage(property, data, config)
        max_mortage = min(new_mortage.get_value(), max_mortage)  # mortage is never greater than 80%of the property price or the previous mortage
        if property.get_status() == Property.OWNED :
            own_funds = 0.0
        else:
            own_funds = property.get_price() * Property.OWN_FUNDS
        
        old_mortage = property.get_mortage()
        new_mortage.set_value(max_mortage)
        amortization = old_mortage.get_value() - new_mortage.get_value()
        if data.get_wealth() < own_funds + amortization  :
            return None
        else :
            new_mortage.set_value(max_mortage)
            
        new_mortage.set_start_age(data.get_actual_age())
        
        return new_mortage

    @staticmethod
    def rent(property : Property, data : Data) -> bool :
        if (property is None) :
            for property in PropertyManager.get_properties(Property.PLANNED_FOR_RENT) :
                PropertyManager.rent(property, data)
            return True 
           
        if (property.get_status() != Property.PLANNED_FOR_RENT) :
            logging.debug(f"Cannot rent property {property.get_name()} as it is no longer planned for rent.")
            return False
        
        property.set_status(Property.RENTED )
        PropertyManager.add_expenses(property)
        logging.info (f"Rent {property.get_name()} --> Age: {data.get_actual_age():5.2f} Wealth: {data.get_wealth():7.0f} CHF Rent: {-1.0*property.get_rental_income() : 5.0f} CHF ")
        return True

    @staticmethod
    def unrent(data : Data, config : Config) -> bool :
        properties = PropertyManager.get_properties(Property.RENTED)
        
        for property in properties :
            property.set_status(Property.PLANNED_FOR_RENT)
            PropertyManager.remove_expenses(property)
            logging.info (f"Canceled {property.get_name()} --> Age: {data.get_actual_age():5.2f} Wealth: {data.get_wealth():7.0f} CHF Rent: {-1.0*property.get_rental_income() : 5.0f} CHF ")
            
        return True
    
    
    @staticmethod 
    def max_mortage(property : Property, data : Data, config : Config  ) -> float :
        sustanability = config.getValue(Config.REALESTATE_AFFORDABILITY_SUSTAINABILITY,Mortage.DEFAULT_AFFORDABILITY_SUSTAINABILITY)
        interest = config.getValue(Config.REALESTATE_AFFORDABILITY_MORTAGEINTEREST, Mortage.DEFAULT_AFFORDABILITY_MORTAGEINTEREST)
        capital_contribution = config.getValue(Config.REALESTATE_AFFORDABILITY_CAPITALCONTRIBUTION, Mortage.DEFAULT_AFFORDABILITY_CAPITALCONTRIBUTION)
        fix_costs = property.get_fix_costs()*Config.MONTHS
        mortage = property.get_mortage().get_value() if property.get_mortage() is not None else 0.0
        
        wealth  = data.get_wealth()
        income = (data.get_legal_pension() + data.get_private_pension())*Config.MONTHS
        price = property.get_price()
        
        if property.get_status() == Property.OWNED :
            renew = True
        else : 
            renew = False

        new_wealth = wealth    
        new_max_mortage = 0.0

        max_legal_mortage = property.get_price()*(1.0-Property.OWN_FUNDS)
        requested_mortage = min(mortage, max_legal_mortage)  # the requested mortage must not exceed the legal limit of 80% of the property price
        i = 0
        while (True) :
            max_mortage = (sustanability * (income + new_wealth * capital_contribution) - fix_costs) / interest   
            max_mortage = min(max_mortage, requested_mortage)
            if abs(new_max_mortage - max_mortage) < 0.001 :
                return max_mortage
            
            if (renew) : 
                amortization =  mortage - max_mortage # in CH you cant get more wealth by increasing ypur mortage
                new_wealth = max(0, wealth - amortization)  # make sure not to go into negative wealth
            else :
                new_wealth = max(0, wealth - (price - max_mortage))  # make sure not to go into negative wealth
                
            new_max_mortage = max_mortage  # update the new max_mortage before the next iteration
            i += 1
            if i > 1000 :
                logging.error(f"Too many iterations in amortization calculation for property {property.get_name()}")
                return -1  # we've gone too far in the loop, something is wrong.  Returning -1 to indicate failure.
            
        return -1

    @staticmethod
    def get_properties(type : str, low2high : bool = None) -> List[Property] :
        low2high = True if low2high is None else low2high
        return PropertyManager.__sort(PropertyManager.__filter(PropertyManager.__properties, type),low2high)
    
    
    @staticmethod
    def get_income() -> float :
       properties = PropertyManager.get_properties()
       income = 0.0
       for property in properties :
        if property.get_status() == Property.RENTED :
            income += max (0.0,property.get_rental_income())
            
    
       return income
        



    