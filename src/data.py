

import logging
from config import Config

class Data:
    
    __change_value_events = {

            Config.PENSION_PRIVATE_CONTRIBUTION : "pk_contribution",
            Config.PENSION_PRIVATE_INTEREST : "pk_interest",
            
            Config.MONEYFLOWS_INCOME : "income",
            Config.MONEYFLOWS_SAVINGS : "savings",
            Config.MONEYFLOWS_SPENDINGS : "spending",          
                        
            Config.WEALTHMANAGEMENT_STOCKPERFORMANCE : "stock_performance",
            Config.WEALTHMANAGEMENT_BONDPERFORMANCE : "bond_performance",
            Config.WEALTHMANAGEMENT_INFLATION : "inflation",
            Config.WEALTHMANAGEMENT_PORTFOLIOBALANCE : "portfolio_balance"
        }
    
    
    

    
    
    def __init__(self, start_age : float, end_age : float, start_month  : int = Config.DEFAULT_STARTMONTH ) :
        self.__wealth = 0.0
        self.__spending = 0.0
        self.__income = 0.0
        self.__private_pension = 0.0
        self.__legal_pension = 0.0
        
        self._threshold_months = 0.0
        
        self.__portfolio_balance = 1.0
        self.__stock_performance = 0.0
        self.__bond_performance = 0.0
        self.__inflation = 0.0
        
        self.__pk_capital = 0.0
        self.__pk_contribution = 0.0
        self.__pk_interest = 0.0
        
        self.__savings = 0.0
        
        self.__lumpsum = 0.0
        self.__lumpsum_ratio = 0.0
        self.__extra = 0.0
        
        self.__yearly_income = 0.0
        
        self.__inflation_history = []
        self.__performance_history = []
        
        self.__start_simulation_month = start_month
        self.__actual_month = start_month
        self.__end_simulation_month = start_month + round((end_age - start_age)*Config.MONTHS)
        self.__start_age = start_age
        self.__end_age = end_age
        self.__actual_age = start_age
        

        
        self._total_assets = 0.0
        
        
    def set_value(self, key, value):
        attr = self.__change_value_events[key]
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
        return self.__spending*self.get_inflation_correction()
    
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
    
    def set_portfolio_balance(self, value : float) :
        value = 1.0 if (value is None) else value
        self.__portfolio_balance = value
    
    def get_performance(self) -> float:
        balance = self.__portfolio_balance
        return balance * self.__stock_performance +  self.__bond_performance * (1.0 - balance)
    
    
    def set_stock_performance(self, value : float) :
        value = 0.0 if (value is None) else value
        self.__stock_performance = value
        
    def set_bond_performance(self, value : float) :
        value = 0.0 if (value is None) else value
        self.__bond_performance = value
    
        
    def get_inflation(self) -> float:
        return self.__inflation
    
    def set_inflation(self, value : float):
        value = 0.0 if (value is None) else value
        self.__inflation = value
    
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
   
    def get_income(self) -> float:
        return self.__income
    
    def set_income(self, value : float):
        value = 0.0 if (value is None) else value
        self.__income = value
        
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
    
    def get_lumpsum_ratio(self) -> float:
        return self.__lumpsum_ratio
    
    def set_lumpsum_ratio(self, value : float):
        value = 0.0 if (value is None) else value
        self.__lumpsum_ratio = value
        
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
        return round(self.__start_age,10)
 
    def get_end_age(self) -> int:
        return round(self.__end_age,10)
    
    def get_actual_age(self) -> float:
        return round(self.__actual_age, 10)
        
    def get_change_value_event(self) -> set:
        return self.__change_value_events.keys()
    
    
    def time_to_sell(self) -> bool:
        
        wealth = self.get_wealth() + self.get_threshold_months()*(self.get_fixed_income() - self.get_spending())
        if (wealth < 0.0):
            return True
        return False
    
    def get_fixed_income(self) -> float :
        return self.get_private_pension() + self.get_legal_pension() + self.get_income()
        
    def get_actual_income(self) -> float: 
        income = self.get_fixed_income()
        income += self.get_wealth() * ((1+self.get_performance())**(1.0/Config.MONTHS) - 1.0)
        return income
    
    def get_total_assets(self) -> float:
        from property import PropertyManager
        return self.get_wealth() + PropertyManager.get_total_assets()
    
    def push_inflation(self) :
        self.__inflation_history.append(self.get_inflation())
        
    def get_inflation_correction(self) :
        correction = 1.0
        for i in range(len(self.__inflation_history)):
            correction *= (1.0+self.__inflation_history[i])         
        return correction
    
    def yearly_average_inflation(self) :
        if (len(self.__inflation_history) == 0) :
            return 0.0
        return self.get_inflation_correction()**(1.0/len(self.__inflation_history)) - 1.0
    
    def push_performance(self) :
        self.__performance_history.append(self.get_performance())
        
    def get_performance_correction(self) :
        correction = 1.0
        for i in range(len(self.__performance_history)):
            correction *= (1.0+self.__performance_history[i])
            
        return correction
    
    def yearly_average_performance(self) :
        if (len(self.__performance_history) == 0) :
            return 0.0
        return self.get_performance_correction()**(1.0/len(self.__performance_history)) - 1.0
    
    
    