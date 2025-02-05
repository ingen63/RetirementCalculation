import json
import os

class Config:

    BEFORE_MONTHLY_PRIVATEPENSIONCONTRIBUTION = "Before.Monthly.PrivatePensionContribution"
    BEFORE_MONTHLY_SAVINGS = "Before.Monthly.Savings"
    BEFORE_PRIVATEPENSIONINTEREST = "Before.PrivatePensionInterest"
    CALCULATION_HISTORICAL_MAX = "Calculation.Historical.Max"
    CALCULATION_HISTORICAL_HISTORICALDATA = "Calculation.Historical.historicalData"
    CALCULATION_HISTORICAL_PORTFOLIOBALANCE = "Calculation.Historical.portfolioBalance"
    CALCULATION_METHOD = "Calculation.Method"
    CALCULATION_SINGLE_INFLATION = "Calculation.Single.Inflation"
    CALCULATION_SINGLE_MAX = "Calculation.Single.Max"
    CALCULATION_SINGLE_PERFORMANCE = "Calculation.Single.Performance"
    EARLY_AGE = "Early.Age"
    EARLY_PRIVATEPENSION_AVAILABLE = "Early.PrivatePension.Available"
    EARLY_PRIVATEPENSION_CAPITAL_PERCENTAGE = "Early.PrivatePension.Capital.Percentage"
    EARLY_PRIVATEPENSION_CAPITAL_TAX = "Early.PrivatePension.Capital.Tax"
    EARLY_PRIVATEPENSION_PENSION = "Early.PrivatePension.Pension"
    EARLY_SEVERANCEPAY = "Early.SeverancePay"
    EARLY_SPENDINGCUT = "Early.SpendingCut"
    GENERAL_AGE = "General.Age"
    GENERAL_CAPITALTAXRATE = "General.CapitalTaxRate"
    GENERAL_INCOMETAXRATE = "General.IncomeTaxRate"
    GENERAL_PRIVATEPENSIONCAPITAL = "General.PrivatePensionCapital"
    GENERAL_SPENDING = "General.Spending"
    GENERAL_WEALTH = "General.Wealth"
    LEGAL_AGE = "Legal.Age"
    LEGAL_LEGALPENSION = "Legal.LegalPension"
    LEGAL_SPENDINGCUT = "Legal.SpendingCut"
    PROPERTY_ACTUAL_MORTAGE = "Property.Actual.Mortage"
    PROPERTY_ACTUAL_MORTAGEINTEREST = "Property.Actual.MortageInterest"
    PROPERTY_ACTUAL_MORTAGESTART = "Property.Actual.MortageStart"
    PROPERTY_ACTUAL_MORTAGETERM = "Property.Actual.MortageTerm"
    PROPERTY_ACTUAL_OWNED = "Property.Actual.Owned"
    PROPERTY_ACTUAL_SELL = "Property.Actual.Sell"
    PROPERTY_ACTUAL_WORTH = "Property.Actual.Worth"
    PROPERTY_AFFORDABILITY_CAPITALCONTRIBUTION = "Property.Affordability.CapitalContribution"
    PROPERTY_AFFORDABILITY_EXTRACOSTS = "Property.Affordability.ExtraCosts"
    PROPERTY_AFFORDABILITY_MORTAGEINTEREST = "Property.Affordability.MortageInterest"
    PROPERTY_AFFORDABILITY_SUSTAINABILITY = "Property.Affordability.Sustainability"
    PROPERTY_RENT = "Property.Rent"
    PROPERTY_REPLACEMENT_MORTAGE = "Property.Replacement.Mortage"
    PROPERTY_REPLACEMENT_MORTAGEINTEREST = "Property.Replacement.MortageInterest"
    PROPERTY_REPLACEMENT_MORTAGETERM = "Property.Replacement.MortageTerm"
    PROPERTY_REPLACEMENT_PLANNED = "Property.Replacement.Planned"
    PROPERTY_REPLACEMENT_SELL = "Property.Replacement.Sell"
    PROPERTY_REPLACEMENT_WORTH = "Property.Replacement.Worth"




    def __init__(self, file_path):
        with open(file_path, 'r') as file:
            self.__data = json.load(file)

    def getValue(self, path):
        keys = path.split('.')
        current =  self.__data
        for key in keys:
            current = current[key]
        return current

    def setValue(self, path, new_value):
        keys = path.split('.')
        current = self.__data
        for key in keys[:-1]:
            current = current[key]
        old_value = current[keys[-1]]
        current[keys[-1]] = new_value
        return old_value

    def __listAvailableKeys(self, prefix=''):

        keys = []
        data = self.__data
        for key in data:
            full_key = f"{prefix}.{key}" if prefix else key
            if isinstance(data[key], dict):
                keys.extend(self.list_available_keys(data[key], full_key))
            else:
                keys.append(full_key)
        return keys

    def dump_data(self):
        keys = self.__listAvailableKeys('')
        for key in sorted(keys):
            variable = key.upper().replace('.', '_')
            print(f"our ${variable} = \"{key}\";")

# Example usage:

config = Config('./data/config.json')
print(config.getValue(Config.BEFORE_MONTHLY_PRIVATEPENSIONCONTRIBUTION))
