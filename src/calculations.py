import logging
from src.util.config import Config
from src.util.utils import Utils


class Calculations:


    def calculate_pre_retirement(self, start : float, end : float, data : Config) :
        """
        Calculate the pre-retirement wealth and private pension capital.
        This method calculates the total wealth and private pension capital
        accumulated from the start year to the end year before retirement.
        It takes into account monthly savings, investment performance,
        and private pension contributions and interest.
        Args:
            start (float): The starting year of the calculation.
            end (float): The ending year of the calculation (retirement year).
            data (Config): An object containing various financial data required
                         for the calculation.
        Returns:
            int: The year at which the calculation ends (retirement year).
        """
        period = end - start
        if period <= 0:
            return
        
        # monthly calculation for investment performance
        wealth = data.getValue(Config.GENERAL_WEALTH)
        savings = data.getValue(Config.BEFORE_SAVINGS)
        performance =  data.getValue(Config.CALCULATION_PERFORMANCE)
        pk_capital = data.getValue(Config.PENSION_PRIVATE_CAPITAL)
        pk_contribution =  data.getValue(Config.PENSION_PRIVATE_CONTRIBUTION)
        pk_interest = data.getValue(Config.PENSION_PRIVATE_INTEREST)

    
        actual_month = data.getSimulationTime()
        months = actual_month+Utils.years_to_months(period)
        
        # monthly calculation for wealth performance
        max_period = data.getValue(Config.GENERAL_MAXPERIOD)
        for month in range(actual_month, months): 
            wealth = (wealth + Utils.getActualValue(month,savings)) * (1.0 + Utils.getActualValue(month, performance))
            pk_capital += Utils.getActualValue(month,pk_contribution)
            
             
            if month % Utils.MONTH == 11 : # Interest is applied once a year at december
                pk_capital  = pk_capital * (1.0 + Utils.getActualValue(month,pk_interest))
              
            if (month > max_period) : 
                 break
            # logging.debug(f"Month: {month}, Wealth: {wealth}, Private Pension Capital: {pk_capital}")    

        

        data.setValue(Config.GENERAL_WEALTH, wealth)
        data.setValue(Config.PENSION_PRIVATE_CAPITAL, pk_capital)
        data.setSimulationTime(month+1)


    def calculate_retirement(self, start, end, data):
        
        period = end - start
        if period <= 0:
            period = 0   
            
        actual_month = data.getSimulationTime()
        early_pension_month = Utils.years_to_months(data.offset(data.getEarlyRetirementAge()))
        legal_pension_month = Utils.years_to_months(data.offset(data.getLegalRetirementAge()))
               
        
        self.calculate_pension(data)  # calculate your private pension contributions and lump sum 
         
        self.set_spendings(data)  # calculate your expenses 
          
        legal_pension = data.getValue(Config.PENSION_LEGALADJUSTED) 
        private_pension = data.getValue(Config.PENSION_PRIVATE_PENSION)            
        inflation = data.getValue(Config.CALCULATION_INFLATION,0.0)
        performance = data.getValue(Config.CALCULATION_PERFORMANCE,0.0)
        expenses = data.getValue(Config.CALCULATION_SPENDING)
        properties_expenses = self.calculate_properties_expenses(data)
        
        # deduct once a year
        income_tax_rate = data.getValue(Config.GENERAL_INCOMETAXRATE,0.0)
        capital_tax_rate = data.getValue(Config.GENERAL_CAPITALTAXRATE,0.0)

        months = actual_month+Utils.years_to_months(period)
        
        # monthly calculation for wealth performance
        max_period = Utils.years_to_months(data.offset(data.getMaxPeriod()))
        wealth = data.getValue(Config.GENERAL_WEALTH)
        previous_wealth = wealth
        yearly_income = 0.0
        for month in range(actual_month, months): 
            # TODO inflation calculation has to be adjusted as inflation must be calculated per month as it might change from month to month.
            
            # check if early_retirewment starts
            if (month == early_pension_month):   # the month you will be early retired the lumpsum payment and severence pay will be due
                wealth = wealth + data.getValue(Config.EARLY_SEVERANCEPAY) + data.getValue(Config.PENSION_PRIVATE_LUMPSUM)
     
            actual_legal_pension = Utils.getActualValue(month, legal_pension)
            actual_private_pension = Utils.getActualValue(month, private_pension)
            actual_expenses = Utils.getActualValue(month, expenses)
            
            yearly_income +=  (actual_private_pension + actual_legal_pension)   # calculate ywearly income contriobution for later tax calcluations
            
            total_deductions =   actual_expenses + properties_expenses
            total_income = actual_private_pension + actual_legal_pension +  wealth*Utils.getActualValue(month, performance)
            
            wealth = wealth + total_income - total_deductions
            
            if month % Utils.MONTH == 11 : # Income Tax and Capital Tax are applied once a year at december
                wealth = wealth  - yearly_income*income_tax_rate
                wealth = wealth * (1.0 - capital_tax_rate)
                yearly_income = 0.0  # reset income for the next year
                
                # now adjust for inflation
                actual_inflation = Utils.getActualValue(month, inflation)
                new_expenses = Utils.adjust_for_inflation(month, actual_expenses, actual_inflation)
                if (new_expenses != actual_expenses ) :
                    expenses[month+1] = new_expenses

                new_legal_pension = Utils.adjust_for_inflation(month, actual_legal_pension, actual_inflation)
                if (new_legal_pension > 0) :
                    legal_pension[month+1] = new_legal_pension
            
            if wealth < 0 or month > max_period :
                wealth = previous_wealth
                month = month -1
                break
            previous_wealth = wealth
            
        logging.info(f"At age of {data.getValue(Config.GENERAL_AGE)+Utils.month_to_years(month+1)} your wealth will be {wealth:.2f}")    

        data.setValue(Config.GENERAL_WEALTH, wealth)
        data.setSimulationTime(month+1)
        
    def set_spendings(self, data):
        early_expenses = data.convert_to_monthly_list(Config.EARLY_SPENDING, False, data.getEarlyRetirementAge())
        if (data.exists(Config.LEGAL_SPENDING)) :
            legal_expenses = data.convert_to_monthly_list(Config.LEGAL_SPENDING, False, data.getLegalRetirementAge())
        else:
            legal_expenses = {}
        
        data.setValue(Config.CALCULATION_SPENDING, early_expenses | legal_expenses)
    
    def calculate_pension(self,data):
            
        # calculate private pension    
        pk_capital = data.getValue(Config.PENSION_PRIVATE_CAPITAL)
        lumpsum_ratio = data.getValue(Config.PENSION_PRIVATE_LUMPSUMRATIO)
        lumpsum_taxrate = data.getValue(Config.PENSION_PRIVATE_LUMPSUMTAXRATE)
        conversion_rate = data.getValue(Config.PENSION_PRIVATE_CONVERSIONRATE)
        
    #    logging.debug(f"Private Pension Capital: {pk_capital:.2f}, Lumpsum: {lumpsum:.2f}, Lumpsum Tax Rate: {lumpsum_taxrate:.2f}, Conversion Rate: {conversion_rate:.2f}")   
         
        pension = (pk_capital * (1.0-lumpsum_ratio) * conversion_rate)/Utils.MONTH        # monthly pension
        lumpsum = lumpsum_ratio * pk_capital * (1.0 - lumpsum_taxrate)                    # lumpsum pension  
         
    #    logging.debug(f"Pension: {pension:.2f}, Lumpsum: {lumpsum:.2f}")
        data.setValue(Config.TMP, pension)
        data.setValue(Config.PENSION_PRIVATE_PENSION, data.convert_to_monthly_list(Config.TMP, False, data.getEarlyRetirementAge()))  # set monthly pension
        data.setValue(Config.PENSION_PRIVATE_LUMPSUM, lumpsum)
        
    # calculate legal pension
        legal_pension = data.convert_to_monthly_list(Config.PENSION_LEGAL, False, data.getLegalRetirementAge())
        data.setValue(Config.PENSION_LEGALADJUSTED, legal_pension)
         
         
             
         
    def calculate_properties_expenses(self, data):
        
         return 0.0 # TODO: Implement this method to calculate property expenses based on current properties
         
        
  
         
    
    