import json
import copy
import logging

from src.util.utils import Utils

class Config:


    GENERAL = "General"
    GENERAL_START = "General.Start"
    GENERAL_END = "General.End"
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
    BEFORE_SAVINGS = "Before.Savings"

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
    REALESTATE_PROPERTIES = "RealEstate.Properties"

    CALCULATION = "Calculation"
    CALCULATION_METHOD = "Calculation.Method"
    CALCULATION_INFLATION = "Calculation.Inflation"
    CALCULATION_PERFORMANCE = "Calculation.Performance"
    CALCULATION_ACTUAL_MONTH = "Calculation.Actual.Month"
    CALCULATION_SINGLE = "Calculation.Single"
    CALCULATION_SINGLE_INFLATION = "Calculation.Single.Inflation"
    CALCULATION_SINGLE_PERFORMANCE = "Calculation.Single.Performance"
    CALCULATION_HISTORICAL = "Calculation.Historical"
    CALCULATION_HISTORICAL_MAX = "Calculation.Historical.Max"
    CALCULATION_HISTORICAL_PORTFOLIOBALANCE = "Calculation.Historical.portfolioBalance"
    CALCULATION_HISTORICAL_HISTORICALDATA = "Calculation.Historical.historicalData"

    __monthly_lists = {BEFORE_SAVINGS : False, PENSION_PRIVATE_CONTRIBUTION : False, PENSION_PRIVATE_INTEREST : False, CALCULATION_SINGLE_INFLATION : True, CALCULATION_SINGLE_PERFORMANCE : True }
    __data = {}
    __initialized = False

    #def __init__(self):
    #        self.__data = {} 
    #    
            
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
        if self.__initialized: 
            raise Exception("Object was already initialized.")
        self.__initialized = True
        
        monthly_lists = self.__monthly_lists
        for key in monthly_lists:
            self.convert_to_monthly_list(key,monthly_lists[key])
                                        

        if self.getValue(Config.CALCULATION_METHOD) == "Single":      
           self.setValue(Config.CALCULATION_INFLATION, self.getValue(Config.CALCULATION_SINGLE_INFLATION))
           self.setValue(Config.CALCULATION_PERFORMANCE, self.getValue(Config.CALCULATION_SINGLE_PERFORMANCE))

        self.setSimulationTime(0)
        return self
        
    
     
    def setSimulationTime(self, month):
        """
        Sets the simulation time by updating the calculation year and month.

        Args:
            month (int): The number of month since start of the simulation. The value is starting with 0.

        This method updates the configuration with the provided year and 
        calculates the corresponding month value using the `years_to_months` 
        utility function.
        """
        self.setValue(Config.CALCULATION_ACTUAL_MONTH, int(month))
    
        
    def getSimulationTime(self):
        """
        Retrieves the simulation time.

        Returns:
            the actual month for the calculation. It starts with 0.
        """
        return int(self.getValue(Config.CALCULATION_ACTUAL_MONTH))  

    def getValue(self, path, defaultValue=None):
        """
        Retrieve a value from a nested dictionary using a dot-separated path.
        Args:
            path (str): A dot-separated string representing the keys to traverse  in the nested dictionary.
        Returns:
        The value corresponding to the specified path if found, otherwise None.
         """
 
        if path == '' or path is None:
            return None
        
        keys = path.split('.')
        current =  self.__data
        try:
            for key in keys:
                current = current[key]
            return current
        except KeyError:
        #    logging.debug(f"KeyError: {path} not found returning default value: {defaultValue}")
            return defaultValue

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
             #   logging.debug(f"Deleting value at {path} with key {key}:{old_value}")
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
  
    
    
    def convert_to_monthly_list(self, input_key, monthly_rate = False):

        year = int(self.getValue(Config.GENERAL_START,2013))
        age = float(self.getValue(Config.GENERAL_AGE, 50))
        input = self.getValue(input_key,{year : 0})
        output = {}

        input = input if isinstance(input, dict) else {year : input}
        for key in input: 
            int_key = int(key) if isinstance(key,str) else key     # if key is a string convert it to int
            offset = year if int_key > 200 else age                 # nobody has an age over 200 so the offset is the actual year
            new_key = Utils.years_to_months(int_key - offset) 
            value = input[key]
            value = (1+value)**(1.0/Utils.MONTH)-1.0 if (monthly_rate) else value        
            output[max(0,int(new_key))] = value
              
        self.setValue(input_key, output)
        
        return output  
      


    def yearly_list_callback(self, key):
        """
        Processes a yearly list or dictionary, adjusting keys based on a general age offset.

        This function retrieves a value associated with the given key and adjusts it
        based on an age offset. If the value is a dictionary, it creates a new dictionary
        with adjusted keys. If it's not a dictionary, it returns a single-item dictionary
        with an adjusted key.

        Args:
            key (str): The key to retrieve the value from the configuration.

        Returns:
            dict: A dictionary with adjusted keys. If the original value was a dictionary,
                  all keys are adjusted. If it was a single value, a dictionary with one
                  adjusted key-value pair is returned.

        Note:
            The key adjustment is done by subtracting the general age offset from each key.
        """
        value  = self.getValue(key)
        offset = round(float(self.getValue(Config.GENERAL_AGE)),2)
        new_dict = {}  
        if isinstance(value, dict):
            new_dict = {}
            for key in value.keys():
                logging.debug(f"Key {key} Offset: {offset}")
                new_key = float(key) - offset
                logging.debug("Test")
                new_dict[new_key] = value.get(key)
                logging.debug(f"Adjusted key: {new_key} to: {value[key]}")
            return new_dict

        return {int(key - offset): value}

        
                 
                 
         
         
         
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
        