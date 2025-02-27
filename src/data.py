

import logging

from config import Config


class Data:
    
    __mapping = {
            Config.TAXES_INCOME : "income_taxrate",
            Config.TAXES_CAPITAL : "capital_taxrate",

            Config.PENSION_PRIVATE_CONTRIBUTION : "pk_contribution",
            Config.PENSION_PRIVATE_INTEREST : "pk_interest",
            
            Config.MONEYFLOWS_SAVINGS : "savings",
            Config.MONEYFLOWS_SPENDINGS : "spending",
            Config.MONEYFLOWS_EXTRA : "extra",
                        
            Config.CALCULATION_SINGLE_PERFORMANCE : "performance",
            Config.CALCULATION_SINGLE_INFLATION : "inflation"
        }
    
    
    __wealth = 0.0
    __spending = 0.0
    __private_pension = 0.0
    __legal_pension = 0.0
    
    _threshold_months = 0.0
    
    __performance = 0.0
    __inflation = 0.0
    __income_taxrate = 0.0
    __capital_taxrate = 0.0
    
    __pk_capital = 0.0
    __pk_contribution = 0.0
    __pk_interest = 0.0
    
    __savings = 0.0
    
    __lumpsum = 0.0
    __extra = 0.0
    
    __yearly_income = 0.0
    
    __start_age = None
    __end_age   = None
    __actual_age = None
    
    __actual_month = None
    __start_simulation_month = None
    __end_simulation_month = None
    
    
    def __init__(self, start_age : float, end_age : float, start_month  : int = Config.DEFAULT_STARTMONTH ) :
        self.__start_simulation_month = start_month
        self.__actual_month = start_month
        self.__end_simulation_month = start_month + round((end_age - start_age)*Config.MONTHS)
        self.__start_age = start_age
        self.__end_age = end_age
        self.__actual_age = start_age
        
        
    def set_value(self, key, value):
        attr = self.__mapping[key]
        if (hasattr(self, f"set_{attr}")) :
            setter = getattr(self,  f"set_{attr}")
            try:
              setter(float(value))
            except TypeError:
               setter(value)     
        else:
            logging.error(f"Invalid key: {key} attr: {attr} for class Data")
    
    def get_wealth(self) -> float:
        return self.__wealth
    
    def set_wealth(self, value : float):
        value = 0.0 if (value is None) else value
        self.__wealth = value
    
    def get_spending(self) -> float:
        return self.__spending
    
    def set_spending(self, value :float) :
        value = 0.0 if (value is None) else value
        self.__spending = value
        
    def get_threshold_months(self) -> int:
        return self._threshold_months
    
    def set_threshold_months(self, month : int):
        month = 0 if (month is None) else month
        self._threshold_months = month
    
    def get_private_pension(self) -> float:
        return self.__private_pension
    
    def set_private_pension(self, value : float):
        value = 0.0 if (value is None) else value
        self.__private_pension = value
    
    def get_legal_pension(self) -> float:
        return self.__legal_pension
    
    def set_legal_pension(self, value : float):
        value = 0.0 if (value is None) else value
        self.__legal_pension = value
    
    def get_performance(self) -> float:
        return self.__performance
    
    def set_performance(self, value : float):
        value = 0.0 if (value is None) else value
        self.__performance = value
    
    def get_inflation(self) -> float:
        return self.__inflation
    
    def set_inflation(self, value : float):
        value = 0.0 if (value is None) else value
        self.__inflation = value
    
    def get_income_taxrate(self) -> float:
        return self.__income_taxrate
    
    def set_income_taxrate(self, value : float):
        value = 0.0 if (value is None) else value
        self.__income_taxrate = value
    
    def get_capital_taxrate(self) -> float:
        return self.__capital_taxrate
    
    def set_capital_taxrate(self, value : float):
        value = 0.0 if (value is None) else value
        self.__capital_taxrate = value
    
    def get_pk_capital(self) -> float:
        return self.__pk_capital
    
    def set_pk_capital(self, value : float):
        value = 0.0 if (value is None) else value
        self.__pk_capital = value
    
    def get_pk_contribution(self) -> float:
        return self.__pk_contribution
    
    def set_pk_contribution(self, value : float):
        value = 0.0 if (value is None) else value
        self.__pk_contribution = value
    
    def get_pk_interest(self) -> float:
        return self.__pk_interest
    
    def set_pk_interest(self, value : float):
        value = 0.0 if (value is None) else value
        self.__pk_interest = value
    
    def get_savings(self) -> float:
        return self.__savings
    
    def set_savings(self, value : float):
        value = 0.0 if (value is None) else value
        self.__savings = value
    
    def get_lumpsum(self) -> float:
        return self.__lumpsum
    
    def set_lumpsum(self, value : float):
        value = 0.0 if (value is None) else value
        self.__lumpsum = value
    
    def get_extra(self) -> float:
        return self.__extra
    
    def set_extra(self, value : float):
        value = 0.0 if (value is None) else value
        self.__extra = value
       
    def get_yearly_income(self) -> float:
        return self.__yearly_income
    
    def set_yearly_income(self, value : float):
        value = 0.0 if (value is None) else value
        self.__yearly_income = value
        
    def get_actual_month(self) -> int:
        return self.__actual_month
    
    def set_actual_month(self, value : int):
        self.__actual_month = int(value)
                
        months_since_start = value - self.get_start_simulation_month()
        self.__actual_age =  self.get_start_age() + months_since_start/Config.MONTHS
        
    def get_start_simulation_month(self) -> int:
        return self.__start_simulation_month
        
    def get_end_simulation_month(self) -> int:
        return self.__end_simulation_month
        
    def get_start_age(self) -> int:
        return self.__start_age
 
    def get_end_age(self) -> int:
        return self.__end_age
    
    def get_actual_age(self) -> float:
        return self.__actual_age
        
    def get_mapping_keys(self) -> set:
        return self.__mapping.keys()
    
    def time_to_sell(self) -> bool:
        wealth = self.get_wealth() - self.get_threshold_months()*self.get_spending()
        if (wealth < 0.0):
            return True
        return False
