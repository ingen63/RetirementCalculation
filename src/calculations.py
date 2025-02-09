import logging
from src.util.config import Config
from src.util.utils import Utils


class Calculations:


    def calculate_pre_retirement_wealth(self, early_retirement_age, data):
        """
        Calculate the pre-retirement wealth and private pension capital.
        This method calculates the total wealth and private pension capital
        accumulated from the start year to the end year before retirement.
        It takes into account monthly savings, investment performance,
        and private pension contributions and interest.
        Args:
            start (int): The starting year of the calculation.
            end (int): The ending year of the calculation (retirement year).
            data (Config): An object containing various financial data required
                         for the calculation.
        Returns:
            int: The year at which the calculation ends (retirement year).
        """
        years_until_retirement = early_retirement_age - data.getValue(Config.GENERAL_AGE)
        
        if years_until_retirement <= 0:
            return
        
        # monthly calculation for investment performance
        wealth = data.getValue(Config.GENERAL_WEALTH)
        savings = data.getValue(Config.BEFORE_MONTHLY_SAVINGS)
        performance =  data.getValue(Config.CALCULATION_PERFORMANCE)

    
        (actual_year,actual_month) = data.getSimulationTime()
        months = actual_month+Utils.years_to_months(years_until_retirement)
        
        logging.debug(f"Actual Year: {actual_year}, Actual Month: {actual_month}, Years: {years_until_retirement}, Months: {months}")
        # monthly calculation for wealth performance
        for month in range(actual_month, months):
            wealth = (wealth + savings) * (1.0 + performance[month])

        # yearly calculation for private pension performance
        private_pension_capital = data.getValue(Config.GENERAL_PRIVATEPENSIONCAPITAL)
        private_pension_contribution =  data.getValue(Config.BEFORE_MONTHLY_PRIVATEPENSIONCONTRIBUTION) * Utils.MONTH
        private_pension_interest = data.getValue(Config.BEFORE_PRIVATEPENSIONINTEREST)
        for year in range(int(years_until_retirement)):
            private_pension_capital = ( private_pension_capital + private_pension_contribution) * (1.0 + private_pension_interest)

        data.setValue(Config.GENERAL_WEALTH, wealth)
        data.setValue(Config.GENERAL_PRIVATEPENSIONCAPITAL, private_pension_capital)
        data.setSimulationTime(month)


    def early_retirement(self, start, end, data):
        years= end - start
        if years <= 0:
            years = 0

        private_pension = data.getValue(Config.EARLY_PRIVATEPENSION) / Utils.MONTH
        inflation = Utils.convert_to_monthly_list(years,data.getValue(Config.CALCULATION_INFLATION))
        performance = Utils.convert_to_monthly_list(years,data.getValue(Config.CALCULATION_PERFORMANCE))
        
        wealth = data.getValue(Config.GENERAL_WEALTH) + data.getValue(Config.EARLY_SEVERANCEPAY)

        expenses = (data.getValue(Config.GENERAL_SPENDING) - data.getValue(Config.EARLY_SPENDINGCUT)) / Utils.MONTH  # TODO add monthly mortage or rent to the expenses
        income_tax_rate = data.getValue(Config.GENERAL_INCOMETAXRATE)
        capital_tax_rate = data.getValue(Config.GENERAL_CAPITALTAXRATE)

        legal_pension = 0

        years, wealth, expenses, legal_pension = self._wealth_withdraw(
            years,
            wealth,
            expenses,
            private_pension,
            legal_pension,
            income_tax_rate,
            capital_tax_rate,
            inflation,
            performance,
        )

        return years, wealth

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
    
    