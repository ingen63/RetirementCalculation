import json
import copy
import logging

from src.util.utils import Utils

class Config:



    GENERAL = "General"
    GENERAL_START = "General.Start"
    GENERAL_END = "General.End"
    GENERAL_AGE = "General.Age"
    GENERAL_MAXPERIOD = "General.MaxPeriod"
    GENERAL_WEALTH = "General.Wealth"
    GENERAL_INCOMETAXRATE = "General.IncomeTaxRate"
    GENERAL_CAPITALTAXRATE = "General.CapitalTaxRate"

    PENSION = "Pension"
    PENSION_PRIVATE = "Pension.Private"
    PENSION_PRIVATE_CAPITAL = "Pension.Private.Capital"
    PENSION_PRIVATE_LUMPSUMRATIO = "Pension.Private.LumpsumRatio"
    PENSION_PRIVATE_LUMPSUM = "Pension.Private.Lumpsum"
    PENSION_PRIVATE_LUMPSUMTAXRATE = "Pension.Private.LumpsumTaxrate"
    PENSION_PRIVATE_CONVERSIONRATE = "Pension.Private.ConversionRate"
    PENSION_PRIVATE_CONTRIBUTION = "Pension.Private.Contribution"
    PENSION_PRIVATE_INTEREST = "Pension.Private.Interest"
    PENSION_PRIVATE_PENSION = "Pension.Private.Pension"
    PENSION_LEGAL = "Pension.Legal"
    PENSION_LEGALADJUSTED = "Pension.LegalAdjusted"

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
    CALCULATION_SPENDING = "Calculation.Spending"
    CALCULATION_ACTUAL_MONTH = "Calculation.Actual.Month"
    CALCULATION_SINGLE = "Calculation.Single"
    CALCULATION_SINGLE_INFLATION = "Calculation.Single.Inflation"
    CALCULATION_SINGLE_PERFORMANCE = "Calculation.Single.Performance"
    CALCULATION_HISTORICAL = "Calculation.Historical"
    CALCULATION_HISTORICAL_MAX = "Calculation.Historical.Max"
    CALCULATION_HISTORICAL_PORTFOLIOBALANCE = "Calculation.Historical.portfolioBalance"
    CALCULATION_HISTORICAL_HISTORICALDATA = "Calculation.Historical.historicalData"

    TMP = "Tmp"

    __DEFAULT_START_YEAR = 2013
    __DEFAULT_START_AGE = 50.0
    __DEFAULT_MAXPERIOD = 50*Utils.MONTH
    __DEFAULT_LEGAL_AGE = 65.0
    
    __monthly_lists = {BEFORE_SAVINGS : False, 
                       PENSION_PRIVATE_CONTRIBUTION : False, 
                       PENSION_PRIVATE_INTEREST : False, 
                       CALCULATION_SINGLE_INFLATION : True, 
                       CALCULATION_SINGLE_PERFORMANCE : True,
                       EARLY_SPENDING : False, 
                       LEGAL_SPENDING : False
                    }
    
    __data = {}
    __initialized = False
 
            
    def load(self, file_path : str):
        with open(file_path, 'r') as file:
            self.__data = json.load(file)
     
    def loads(self, json_data : str):
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
            if key == Config.EARLY_SPENDING : 
                self.convert_to_monthly_list(key,monthly_lists[key], self.getEarlyRetirementAge())
            elif key == Config.LEGAL_SPENDING : 
                self.convert_to_monthly_list(key,monthly_lists[key], self.getLegalRetirementAge())
            else :
                self.convert_to_monthly_list(key,monthly_lists[key])
                                        

        if self.getValue(Config.CALCULATION_METHOD) == "Single":      
           self.setValue(Config.CALCULATION_INFLATION, self.getValue(Config.CALCULATION_SINGLE_INFLATION))
           self.setValue(Config.CALCULATION_PERFORMANCE, self.getValue(Config.CALCULATION_SINGLE_PERFORMANCE))


        # set the maximum simulation period
        period = self.getValue(Config.GENERAL_END) - self.getValue(Config.GENERAL_START)
        self.setValue(Config.GENERAL_MAXPERIOD, Utils.years_to_months(period))
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

    def getValue(self, path : str, defaultValue=None) :
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

    def setValue(self, path : str, value):
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
        
        
        for i in range(len(keys)):
           # logging.debug(f"i: {i} key: {keys[i]} keys: {keys} current: {current} __data: {self.__data}")
             
            if i < len(keys)-1:
                if (keys[i] in current): # key exists in current
                    current = current[keys[i]]
                else: # key does not exist in current create a new dictionary
                    current[keys[i]] = {}
                    current = current[keys[i]]
            else:
                old_value = None
                if (keys[i] in current): # key exists in current
                    old_value = current[keys[i]]
                current[keys[i]] = value
             #   logging.debug(f"i: {i} key: {keys[i]} keys: {keys} current: {current} __data: {self.__data}")
                return old_value
            

    def exists(self, path : str):
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
    
    
    def delete(self, path : str):
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
    
    def clear(self):
        """
        Deletes all values from the configuration data.
        """
        self.__data = {}
        self.__initialized = False
        


    
 
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
  
    
    
    def convert_to_monthly_list(self, input_key : str, monthly_rate : bool, start_year : float = 0.0):
        """
        Converts a dictionary of values to a monthly list based on the given parameters.

        This function takes a dictionary of values, a boolean indicating whether the values are monthly rates, 
        and an optional start year. It converts the dictionary to a monthly list, adjusting the keys to represent 
        the number of months since the start year or age, and applying the monthly rate conversion if necessary.

        Parameters:
        - input_key (str): The key for the input data in the configuration.
        - monthly_rate (bool): A boolean indicating whether the input values are monthly rates.
        - start_year (float, optional): The start year for the conversion. Defaults to 0.0.

        Returns:
        - dict: A dictionary representing the monthly list of values.
        """
        year = int(self.getValue(Config.GENERAL_START,2013))
        age = float(self.getValue(Config.GENERAL_AGE, 50))
        input = self.getValue(input_key,{year : 0})
        if start_year == 0 :
            start_year = year
        output = {}

        input = input if isinstance(input, dict) else {start_year : input}
        for key in input: 
            float_key = float(key) if isinstance(key,str) else key     # if key is a string convert it to float
            float_key = self.offset(float_key)
         #   offset = year if float_key > Utils.MAGIC_YEAR else age  # nobody has an age over 200 so the offset is the actual year
            new_key = Utils.years_to_months(float_key) 
            value = input[key]
            value = (1+value)**(1.0/Utils.MONTH)-1.0 if (monthly_rate) else value        
            output[max(0,new_key)] = value

        return output
      
     
    def offset(self, year: float) -> float:
        """
        Calculate the offset between a given year and either the start year or start age.

        This function determines whether the input represents a calendar year or an age,
        and calculates the difference between it and the corresponding start value.

        Args:
            year (float): The year or age to calculate the offset for.

        Returns:
            float: The calculated offset.
                   If the input is greater than MAGIC_YEAR, it returns the difference
                   between the input and the start year.
                   Otherwise, it returns the difference between the input and the start age.
        """
        if (year > Utils.MAGIC_YEAR):
            return year - self.getStartYear()
        else:
            return year - self.getStartAge()
        

         
    def list_available_keys(self, data, prefix):
        keys = []

        for key in data:
            full_key = f"{prefix}.{key}" if prefix else key
            # logging.debug(f"Found key: {full_key}")
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
        
        
        
    def getStartYear(self) :
        return self.getValue(Config.GENERAL_START,self.__DEFAULT_START_YEAR)
    
    def getStartAge(self) :
        return self.getValue(Config.GENERAL_AGE,self.__DEFAULT_START_AGE)
    
    def getMaxPeriod(self) :
        return self.getValue(Config.GENERAL_MAXPERIOD,self.__DEFAULT_MAXPERIOD)   
     
    def getLegalRetirementAge(self) :
        return self.getValue(Config.LEGAL_AGE, self.__DEFAULT_LEGAL_AGE)
    
    def getEarlyRetirementAge(self) :
        return self.getValue(Config.EARLY_AGE, self.__DEFAULT_LEGAL_AGE)