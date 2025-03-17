
import logging
import time
from data import Data
from event import BuyPropertyEvent, ChangeValueEvent, EarlyRetirmentEvent, EndSimulationEvent, EventHandler, LegalRetirmentEvent, MoneyFlowExtraEvent, RenewMortageEvent, RentPropertyEvent, SellPropertyEvent, StartSimulationEvent
from config import Config
from output import Output
from property import Property, PropertyManager
from tax import TaxHandler


class Simulation :
    
    output = Output()

    def   init(self, config : Config,  historical_year: int = None) -> Data :
        
        EventHandler.reset_events()
        PropertyManager.reset()
        data = Data(config.getStartAge(), config.getEndAge(), config.getStartMonth())
        data.set_historical_year(historical_year)

        EventHandler.add_event(StartSimulationEvent(config.getStartMonth()))

        # create all change events
        keys = data.get_change_value_event()
        for key in keys:
            values = config.getValue(key)
            if (isinstance(values,dict)) :
                for age in values.keys() :
                    change_event_month = config.getStartMonth() if config.best_guess_for_number(age) < data.get_start_age() else config.age2months(age)
                    EventHandler.add_event(ChangeValueEvent(change_event_month, key))
            else :
                data.set_value(key, config.best_guess_for_number(values)) 
                
        values = config.getValue(Config.MONEYFLOWS_EXTRA)
        if (isinstance(values,dict)) :
            for age in values.keys():
                change_event_month = config.getStartMonth() if config.best_guess_for_number(age) < data.get_start_age() else config.age2months(age)
                EventHandler.add_event(MoneyFlowExtraEvent(change_event_month,float(values[age])))
        else :
            EventHandler.add_event(MoneyFlowExtraEvent(config.getStartMonth(),float(values)))
               
                     # Early retirement
        early_retirment_month = config.age2months(config.getEarlyRetirementAge())
        EventHandler.add_event(EarlyRetirmentEvent(early_retirment_month))

        # Legal retirement
        legal_retirment_month = config.age2months(config.getLegalRetirementAge())
        EventHandler.add_event(LegalRetirmentEvent(legal_retirment_month))   
               
        # initialize properties
        properties = config.getValue(Config.REALESTATE_PROPERTIES,[])
        
        for property in properties:
            PropertyManager.add_property(Property(Config(property)))
            
        for property in PropertyManager.get_properties(Property.OWNED) :
            if (property.get_sell_age() is not None) :
                EventHandler.add_event(SellPropertyEvent(config.age2months(property.get_sell_age()), property))
            renew_mortage_age = property.get_mortage().get_start_age() + property.get_mortage().get_term()
            EventHandler.add_event(RenewMortageEvent(config.age2months(renew_mortage_age), property))
        for property in PropertyManager.get_properties(Property.PLANNED) :
            if (property.get_buy_age() is not None) :
                EventHandler.add_event(BuyPropertyEvent(config.age2months(property.get_buy_age()), property))
                
        for property in PropertyManager.get_properties(Property.PLANNED_FOR_RENT) :
            if (property.get_buy_age() is not None) :
                EventHandler.add_event(RentPropertyEvent(config.age2months(property.get_buy_age()), property))

        EventHandler.add_event(EndSimulationEvent(config.getEndMonth()))
        
        EventHandler.init(config, data)
        
        if (data.get_historical_year() is not None) :
            for property in PropertyManager.get_properties(Property.OWNED) :
                Output.add_sell(data.get_historical_year(), property.get_name(),Output.NEVER)
            for property in PropertyManager.get_properties(Property.PLANNED):
                Output.add_sell(data.get_historical_year(), property.get_name(), Output.NEVER)

        return data


    def run(self, data : Data, config : Config) :
        
        
        logging.info(f"Simulation started -->  {Output.get_name()} Age {data.get_start_age(): 5.2f} End Age: {data.get_end_age() : 5.2f}")
        
        Output.add_result(Output.START_AGE, f"{data.get_start_age():.2f}")
        Output.add_result(Output.LEGAL_RETIREMENT_AGE, f"{config.getLegalRetirementAge():.2f}")
        Output.add_result(Output.EARLY_RETIREMENT_AGE, f"{config.getEarlyRetirementAge():.2f}")

        
        actual_month = data.get_actual_month()
        end_months = data.get_end_simulation_month()

        start_time = time.time()*1000.0
        

        for month in range(actual_month, end_months+1):
            data.set_actual_month(month)
            EventHandler.before(month, config, data)
            
            wealth_trend = self.__one_month(month, data, config)
            
            EventHandler.after(month, config, data)
            new_wealth = data.get_wealth()
            projected_wealth = new_wealth + wealth_trend*data.get_threshold_months()
            if (projected_wealth <= 0.0) :
                if PropertyManager.nothing_to_sell() is False:
                    logging.info(f"Need to sell properties with age {data.get_actual_age()}")
                    EventHandler.add_event(SellPropertyEvent(month+1, PropertyManager.get_property_for_sale()))
            if (new_wealth <= 0.0) :
                logging.info(f"Simulation finished with age {data.get_actual_age()} with no money left.")
                break
        
        end_time = time.time()*1000.0   
        logging.info(f"Simulation finished after {end_time - start_time} ms")
        logging.getLogger(Config.LOGGER_SUMMARY).info(f"Simulation finished at age of {data.get_actual_age()} with wealth of {data.get_wealth() : .0f}")
        
        Output.add_result(Output.TIME_TO_GO, f"{data.get_actual_age():.2f}")
        Output.add_result(Output.REMAINING_WEALTH,f"{max(0.0,data.get_wealth()):,.0f} CHF")
    
    
    def __one_month(self, month : int, data : Data, config : Config) :
        
        if month % Config.MONTHS == 0 :
            data.push_inflation() # push inflation to history for later inflation corrections
            data.push_performance() # push performance to history for later performance corrections
            
        # adjust spendigs accodording to inflation
        spending = data.get_spending()
        spending *= (1.0 + data.get_inflation())**((month % Config.MONTHS)/Config.MONTHS)
        
        income = data.get_income()
                 
        legal_pension = data.get_legal_pension()
        if month % Config.MONTHS == 0 : # Legal pension is adjusted once a year for inflation       
            legal_pension *= (1.0 + data.get_inflation())
        
        private_pension = data.get_private_pension()
        monthly_performance = ((1.0 + data.get_performance())**(1.0/Config.MONTHS)) - 1
            
        yearly_income = data.get_yearly_income() + private_pension   + legal_pension  + income
        total_deductions =  spending + PropertyManager.get_properties_expenses()
          
        total_income = private_pension + legal_pension + income
        wealth_trend = total_income - total_deductions + data.get_wealth()*monthly_performance
            
        wealth = data.get_wealth() + data.get_savings() + total_income - total_deductions
        wealth *=  (1.0 + monthly_performance)
        pk_capital = data.get_pk_capital() + data.get_pk_contribution()
  
        if month % Config.MONTHS == 0 : # Income Tax and Capital Tax are applied once a year at december
            
            pk_capital  = pk_capital * (1.0 + data.get_pk_interest())
            capital_tax = TaxHandler.capital_tax(config, wealth)
            income_tax = TaxHandler.income_tax(config, yearly_income)
            wealth -=  (capital_tax + income_tax)
            yearly_income = 0.0 # reset income for the next year
            
                           

       
            logging.info(f"Age: {data.get_actual_age():5.2f}, Wealth: {wealth:7.0f} CHF, Total Income: {data.get_actual_income() :6.0f} CHF, Total Expenses: {total_deductions : 6.0f} CHF, Performance: {data.get_performance()*100 : 5.2f} % Inflation: {data.get_inflation()*100 : 5.2f}")
           
            
        data.set_wealth(wealth)
        data.set_pk_capital(pk_capital)
        data.set_legal_pension(legal_pension)
        data.set_yearly_income(yearly_income)
        
        return wealth_trend
   