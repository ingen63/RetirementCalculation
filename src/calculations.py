import logging
from src.util.config import Config
from src.util.utils import Utils


class Calculations:


    def calculate_pre_retirement(self, start, end, data):
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


    def calculate_early_retirement(self, start, end, data):
        
        period = end - start
        if period <= 0:
            period = 0   
            
        
        self.calculate_pension(data)  # calculate your private pension contributions and lump sum 
          
        income = data.getValue(Config.PENSION_PRIVATE_PENSION)  
            
        inflation = data.getValue(Config.CALCULATION_INFLATION)
        performance = data.getValue(Config.CALCULATION_PERFORMANCE)
        expenses = data.getValue(Config.EARLY_SPENDING)
        properties_expenses = self.calculate_properties_expenses(data)
        
        # deduct once a year
        income_tax_rate = data.getValue(Config.GENERAL_INCOMETAXRATE)
        capital_tax_rate = data.getValue(Config.GENERAL_CAPITALTAXRATE)

        actual_month = data.getSimulationTime()
        months = actual_month+Utils.years_to_months(period)
        
   
       # logging.debug(f"Wealth: {data.getValue(Config.GENERAL_WEALTH)} Severancepay: {data.getValue(Config.EARLY_SEVERANCEPAY)} Lumpsum: {data.getValue(Config.PENSION_PRIVATE_LUMPSUM)}")    
        wealth = data.getValue(Config.GENERAL_WEALTH) + data.getValue(Config.EARLY_SEVERANCEPAY) + data.getValue(Config.PENSION_PRIVATE_LUMPSUM)
        

        
        # monthly calculation for wealth performance
        yearly_income = 0.0
        max_period = data.getValue(Config.GENERAL_MAXPERIOD)
        previous_wealth = wealth
        for month in range(actual_month, months): 
            yearly_income += income
            total_deductions = Utils.getActualValue(month,expenses)*((1+Utils.getActualValue(month, inflation))**month)  + properties_expenses
         #   logging.debug(f"     expenses: {Utils.getActualValue(month, expenses)} InflationFactor: {((1+Utils.getActualValue(month, inflation))**month)}")
            total_income = income  + wealth*Utils.getActualValue(month, performance)
         #   logging.debug(f"Month: {month}, Wealth: {wealth}  total_income: {total_income:.3f} total_deductions: {total_deductions:.3f} ")    
            wealth = wealth + total_income - total_deductions
            
            if month % Utils.MONTH == 11 : # Income Tax and Capital Tax are applied once a year at december
                wealth = wealth  - yearly_income*income_tax_rate
                wealth = wealth * (1.0 - capital_tax_rate)
                yearly_income = 0.0  # reset income for the next year
            
            if wealth < 0 or month > max_period :
                wealth = previous_wealth
                month = month -1
                break
            previous_wealth = wealth
            
        logging.info(f"At age of {data.getValue(Config.GENERAL_AGE)+Utils.month_to_years(month+1)} your wealth will be {wealth:.2f}")    

        data.setValue(Config.GENERAL_WEALTH, wealth)
        data.setSimulationTime(month+1)

    def wealth_withdraw(
        self,
        years_until_retirement,
        wealth,
        expenses,
        private_pension,
        legal_pension,
        income_tax_rate,
        capital_tax_rate,
        inflation,
        performance,
    ):
        total_months = int(years_until_retirement * Utils.MONTH)
        inflation = Utils.convert_to_monthly_list(years_until_retirement, inflation)
        performance = Utils.convert_to_monthly_list(years_until_retirement, performance)

        if (
            len(inflation) == 0
            or len(performance) == 0
            or wealth <= 0
            or years_until_retirement <= 0
        ):
            return 0.0, wealth, expenses, legal_pension

        for step in range(1, total_months + 1):
            expenses *= 1.0 + inflation[step - 1]
            wealth = (wealth - (expenses - private_pension - legal_pension)) * (
                1.0 + performance[step - 1]
            )

            if step % Utils.MONTH == 0:
                legal_pension *= (
                    1.0 + inflation[step - 1]
                ) ** Utils.MONTH  # adjust legal pension yearly
                wealth -= (
                    (private_pension + legal_pension) * income_tax_rate
                    + wealth * capital_tax_rate
                )  # yearly tax on private pension and wealth

            if wealth <= 0:  # wealth is depleted so there is need for action
                return step / Utils.MONTH, wealth, expenses, legal_pension

        return total_months / Utils.MONTH, wealth, expenses, legal_pension
    
    
    
    def calculate_pension(self,data):
            
        pk_capital = data.getValue(Config.PENSION_PRIVATE_CAPITAL)
        lumpsum_ratio = data.getValue(Config.PENSION_PRIVATE_LUMPSUMRATIO)
        lumpsum_taxrate = data.getValue(Config.PENSION_PRIVATE_LUMPSUMTAXRATE)
        conversion_rate = data.getValue(Config.PENSION_PRIVATE_CONVERSIONRATE)
        
    #    logging.debug(f"Private Pension Capital: {pk_capital:.2f}, Lumpsum: {lumpsum:.2f}, Lumpsum Tax Rate: {lumpsum_taxrate:.2f}, Conversion Rate: {conversion_rate:.2f}")   
         
        pension = (pk_capital * (1.0-lumpsum_ratio) * conversion_rate)/Utils.MONTH        # monthly pension
        lumpsum = lumpsum_ratio * pk_capital * (1.0 - lumpsum_taxrate)                    # lumpsum pension  
         
    #    logging.debug(f"Pension: {pension:.2f}, Lumpsum: {lumpsum:.2f}")
        data.setValue(Config.PENSION_PRIVATE_PENSION, pension)
        data.setValue(Config.PENSION_PRIVATE_LUMPSUM, lumpsum)
         
         
    def calculate_properties_expenses(self, data):
        
         return 0.0 # TODO: Implement this method to calculate property expenses based on current properties
         
        
  
         
    
    