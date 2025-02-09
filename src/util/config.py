import json
import copy
import logging

from src.util.utils import Utils

class Config:


    GENERAL = "General"
    GENERAL_AGE = "General.Age"
    GENERAL_WEALTH = "General.Wealth"
    GENERAL_INCOMETAXRATE = "General.IncomeTaxRate"
    GENERAL_CAPITALTAXRATE = "General.CapitalTaxRate"

    PENSION = "Pension"
    PENSION_PRIVATE = "Pension.Private"
    PENSION_PRIVATE_CAPITAL = "Pension.Private.Capital"
    PENSION_PRIVATE_LUMPSUM = "Pension.Private.Lumpsum"
    PENSION_PRIVATE_LUMPSUMTAXRATE = "Pension.Private.LumpsumTaxrate"
    PENSION_PRIVATE_CONVERSIONRATE = "Pension.Private.ConversionRate"
    PENSION_PRIVATE_CONTRIBUTION = "Pension.Private.Contribution"
    PENSION_PRIVATE_INTEREST = "Pension.Private.Interest"
    PENSION_LEGAL = "Pension.Legal"

    BEFORE = "Before"
    BEFORE_MONTHLY = "Before.Monthly"
    BEFORE_MONTHLY_SAVINGS = "Before.Monthly.Savings"

    EARLY = "Early"
    EARLY_AGE = "Early.Age"
    EARLY_SEVERANCEPAY = "Early.SeverancePay"
    EARLY_SPENDING = "Early.Spending"

    LEGAL = "Legal"
    LEGAL_AGE = "Legal.Age"
    LEGAL_SPENDING = "Legal.Spending"

    REALESTATE = "RealEstate"
    REALESTATE_RENT = "RealEstate.Rent"
    REALESTATE_AFFORDABILITY = "RealEstate.Affordability"
    REALESTATE_AFFORDABILITY_SUSTAINABILITY = "RealEstate.Affordability.Sustainability"
    REALESTATE_AFFORDABILITY_MORTAGEINTEREST = "RealEstate.Affordability.MortageInterest"
    REALESTATE_AFFORDABILITY_CAPITALCONTRIBUTION = "RealEstate.Affordability.CapitalContribution"
    REALESTATE_AFFORDABILITY_EXTRACOSTS = "RealEstate.Affordability.ExtraCosts"
    REALESTATE_PRPOERTIES = "RealEstate.Prpoerties"

    CALCULATION = "Calculation"
    CALCULATION_METHOD = "Calculation.Method"
    CALCULATION_INFLATION = "Calculation.Inflation"
    CALCULATION_PERFORMANCE = "Calculation.Performance"
    CALCULATION_ACTUAL_YEAR = "Calculation.Actual.Year"
    CALCULATION_ACTUAL_MONTH = "Calculation.Actual.Month"
    CALCULATION_SINGLE = "Calculation.Single"
    CALCULATION_SINGLE_MAX = "Calculation.Single.Max"
    CALCULATION_SINGLE_INFLATION = "Calculation.Single.Inflation"
    CALCULATION_SINGLE_PERFORMANCE = "Calculation.Single.Performance"
    CALCULATION_HISTORICAL = "Calculation.Historical"
    CALCULATION_HISTORICAL_MAX = "Calculation.Historical.Max"
    CALCULATION_HISTORICAL_PORTFOLIOBALANCE = "Calculation.Historical.portfolioBalance"
    CALCULATION_HISTORICAL_HISTORICALDATA = "Calculation.Historical.historicalData"


    def __init__(self):
            self.__data = {} 
        
            
    def load(self, file_path):
        with open(file_path, 'r') as file:
            self.__data = json.load(file)
     
    def loads(self, json_data):
        self.__data = json.loads(json_data)       
    
            
    def initialize(self):
        """
        Initializes the configuration for the retirement calculation.

        This method sets up the initial values for the calculation based on the 
        selected calculation method. If the calculation method is "Single", it 
        calculates the maximum number of years for the simulation, the inflation rate, and 
        the performance rate. These values are then converted to monthly lists 
        and stored in the configuration.

        The method also initializes the year and month to 0.

        Returns:
            None
        """


        if self.getValue(Config.CALCULATION_METHOD) == "Single":
           years = self.getValue(Config.CALCULATION_SINGLE_MAX)-self.getValue(Config.GENERAL_AGE)
           inflation = self.getValue(Config.CALCULATION_SINGLE_INFLATION)
           performance = self.getValue(Config.CALCULATION_SINGLE_PERFORMANCE)
           self.setValue(Config.CALCULATION_INFLATION, Utils.convert_to_monthly_list(years,Utils.create_yearly_list(years,inflation), True))
           self.setValue(Config.CALCULATION_PERFORMANCE, Utils.convert_to_monthly_list(years,Utils.create_yearly_list(years, performance),True))

        self.setSimulationTime(0)
        
     
    def setSimulationTime(self, month):
        """
        Sets the simulation time by updating the calculation year and month.

        Args:
            month (int): The number of month since start of the simulation. The value is starting with 0.

        This method updates the configuration with the provided year and 
        calculates the corresponding month value using the `years_to_months` 
        utility function.
        """
        self.setValue(Config.CALCULATION_ACTUAL_YEAR, Utils.month_to_years(month))
        self.setValue(Config.CALCULATION_ACTUAL_MONTH, int(month))
    
        
    def getSimulationTime(self):
        """
        Retrieves the simulation time.

        Returns:
            tuple: A tuple containing the actual year and month for the calculation.
        """
        return self.getValue(Config.CALCULATION_ACTUAL_YEAR), self.getValue(Config.CALCULATION_ACTUAL_MONTH)        

    def getValue(self, path):
        """
        Retrieve a value from a nested dictionary using a dot-separated path.
        Args:
            path (str): A dot-separated string representing the keys to traverse  in the nested dictionary.
        Returns:
        The value corresponding to the specified path if found, otherwise None.
         """
 
        keys = path.split('.')
        current =  self.__data
        try:
            for key in keys:
                current = current[key]
            return current
        except KeyError:
            logging.debug(f"KeyError: {path} not found")
            return None

    def setValue(self, path, value):
        """
        Sets the value at the specified path in the nested dictionary.
        Args:
            path (str): The dot-separated path indicating where to set the new value.
            value (Any): The new value to set at the specified path.
        Returns:
            Any: The old value at the specified path if it existed, otherwise None.
        """
        
        if path == '' or path is None:
            return None
        
        keys = path.split('.')
        current = self.__data
        
        for key in keys:
            if key == keys[-1]:
                old_value =  current[key] if key in current else None
            #    logging.debug(f"Setting value at {path} to {key}: {value}. Old value was {old_value}")
                current[key] = value
                return old_value
            
            if key not in current:
                current[key] = {}
            current = current[key]

    def exists(self, path):
        """
        Check if a given dot-separated path exists in the configuration data.

        Args:
            path (str): Dot-separated string representing the path to check in the configuration data.

        Returns:
            bool: True if the path exists in the configuration data, False otherwise.
        """
        if not path:
            return False
        
        keys = path.split('.')
        current = self.__data
        for key in keys:
            if key not in current:
                return False
            current = current[key]
        return True
    
    
    def delete(self, path):
        """
        Deletes a value from the nested dictionary based on the given dot-separated path.
        Args:
            path (str): The dot-separated path indicating the key to delete.
        Returns:
            The deleted value if the key was found and deleted, otherwise None.
        Logs:
            A debug message indicating the deletion of the value at the specified path.
        """
        if not path:
            return False
        
        keys = path.split('.')
        current = self.__data
        for key in keys:
            if key == keys[-1]:
                old_value =  current[key] if key in current else None
                logging.debug(f"Deleting value at {path} with key {key}:{old_value}")
                del current[key]
                return old_value
                
            if key not in current:
                return None
            current = current[key]
        return None

    
 
    def clone(self):
        """
        Creates a deep copy of the current Config instance.

        Returns:
            Config: A new instance of Config with a deep copy of the original data.
        """
        data_copy =  copy.deepcopy(self.__data)
        data = Config()
        data.__data =   data_copy
        return data

  
    def list_available_keys(self, data, prefix):
        keys = []

        for key in data:
            full_key = f"{prefix}.{key}" if prefix else key
            logging.debug(f"Found key: {full_key}")
            if isinstance(data[key], dict):
                keys.append(full_key)
                keys.extend(self.list_available_keys(data[key], full_key))
            else:
                keys.append(full_key)
        return keys
 
    def dump_data(self):
        data = self.__data
        keys = self.list_available_keys(data,'')
        for key in keys:
            if '.' not in key:
               print("")
            variable = key.upper().replace('.', '_')
            print(f"    {variable} = \"{key}\"")
        