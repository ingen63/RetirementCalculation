
from src.data import Data
from src.event import ChangeValueEvent, EarlyRetirmentEvent, EndSimulationEvent, EventHandler, LegalRetirmentEvent, StartSimulationEvent
from src.util.config import Config
from src.util.utils import Utils


class Simulation :

    def init(self, config : Config) -> Data :
        
        EventHandler.reset_events()
        data = Data()
        start_age = float(config.getStartAge())

        EventHandler.add_event(StartSimulationEvent(Config.DEFAULT_STARTMONTH))

        # Early retirement
        early_retirment_month = Utils.years_to_months(config.getValue(Config.EARLY_AGE) - start_age)
        EventHandler.add_event(EarlyRetirmentEvent(early_retirment_month))

        # Legal retirement
        legal_retirment_month = Utils.years_to_months(config.getValue(Config.LEGAL_AGE) - start_age)
        EventHandler.add_event(LegalRetirmentEvent(legal_retirment_month))


        # create all change events
        keys = data.get_mapping_keys()

        for key in keys:
            values = config.getValue(key)
            if (isinstance(values,dict)) :
                for age in values.keys():
                    change_event_month = Utils.years_to_months(float(age) - start_age)
                    EventHandler.add_event(ChangeValueEvent(change_event_month, key))
            else:
                month = 0
                if (key == Config.EARLY_SPENDING) :
                    month = Utils.years_to_months(config.getValue(Config.EARLY_AGE) - start_age)
                if (key == Config.LEGAL_SPENDING) :
                    month = Utils.years_to_months(config.getValue(Config.LEGAL_AGE) - start_age)
                
                EventHandler.add_event(ChangeValueEvent(month, key))


        end_simulation_month = Utils.years_to_months(float(config.getValue(Config.GENERAL_ENDAGE)) - start_age)  + 1
        EventHandler.add_event(EndSimulationEvent(end_simulation_month))
        data.set_end_simulation_month(end_simulation_month)

        return data


    def simulate(self, data : Data, config : Config) :
        
        actual_month = data.get_actual_month()
        end_months = data.get_end_simulation_month()


        for month in range(actual_month, end_months):
            EventHandler.before(month, config, data)
            
            self.__one_month(month, data)
            
            EventHandler.after(month, config, data)
            data.set_actual_month(month)




    def __pre_retirement(self, month : int, data : Data) :
        # monthly calculation for investment performance


            wealth = (data.get_wealth() + data.get_savings()) * ((1.0 + data.get_performance())**(1.0/Utils.MONTH))
            pk_capital = data.get_pk_capital() + data.get_pk_contribution()


            if month % Utils.MONTH == 11 : # Interest is applied once a year at december
                pk_capital  = pk_capital * (1.0 + data.get_pk_interest())
                
            # logging.debug(f"Month: {month}, Wealth: {wealth}, Private Pension Capital: {pk_capital}") 
            data.set_wealth(wealth)
            data.set_pk_capital(pk_capital)

    
    
    def __one_month(self, month : int, data : Data) :
        
        # adjust spendigs accodording to inflation
        spending = data.get_spending()
        spending *= (1.0 + data.get_inflation())**(1.0/Utils.MONTH)
                 
        legal_pension = data.get_legal_pension()
        private_pension = data.get_private_pension()
            
        yearly_income = data.get_yearly_income() + private_pension   + legal_pension 
        total_deductions =  spending + data.get_properties_expenses()
          
        total_income = private_pension + legal_pension
            
        wealth = data.get_wealth() + data.get_savings() + total_income - total_deductions
        wealth *=  ((1.0 + data.get_performance())**(1.0/Utils.MONTH))
        pk_capital = data.get_pk_capital() + data.get_pk_contribution()
  
        if month % Utils.MONTH == 11 : # Income Tax and Capital Tax are applied once a year at december
            
            pk_capital  = pk_capital * (1.0 + data.get_pk_interest())
            wealth = wealth * (1.0 - data.get_capital_taxrate())
            wealth = wealth  - yearly_income*data.get_income_taxrate()
            yearly_income = 0.0 # reset income for the next year
                           
            #  adjust for inflation every year         
            legal_pension *= ((1.0 + data.get_inflation())**(1.0/Utils.MONTH))
           
            
        data.set_wealth(wealth)
        data.set_pk_capital(pk_capital)
        data.set_spending(spending)
        data.set_legal_pension(legal_pension)
        data.set_yearly_income(yearly_income)
   