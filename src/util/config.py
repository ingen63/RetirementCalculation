import json
import copy

from src.util.utils import Utils

class Config:



    GENERAL = "General"
    GENERAL_STARTAGE = "General.StartAge"
    GENERAL_START_MONTH = "General.StartMonth"
    GENERAL_ENDAGE = "General.EndAge"
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

    DEFAULT_STARTAGE = 50.0
    DEFAULT_MAXPERIOD = 30.0
    DEFAULT_LEGALAGE = 65.0
    
    DEFAULT_STARTMONTH = 0
        
    __data = {}
    
            
    def load(self, file_path : str):
        with open(file_path, 'r') as file:
            self.__data = json.load(file)
     
    def loads(self, json_data : str):
        self.__data = json.loads(json_data)       
     
     
            
    def initialize(self):
                                

        if self.getValue(Config.CALCULATION_METHOD) == "Single":      
           self.setValue(Config.CALCULATION_INFLATION, self.getValue(Config.CALCULATION_SINGLE_INFLATION))
           self.setValue(Config.CALCULATION_PERFORMANCE, self.getValue(Config.CALCULATION_SINGLE_PERFORMANCE))


        # set default values
        self.setValue(Config.GENERAL_STARTAGE, self.getValue(Config.GENERAL_STARTAGE, Config.DEFAULT_STARTAGE))
        self.setValue(Config.LEGAL_AGE, self.getValue(Config.LEGAL_AGE, Config.DEFAULT_LEGALAGE))
        end_age = self.getValue(Config.GENERAL_ENDAGE)
        
        if end_age is None :
            end_age = self.getValue(Config.GENERAL_STARTAGE) + self.DEFAULT_MAXPERIOD
        
        self.setValue(Config.GENERAL_ENDAGE, end_age)
        self.__start_age = self.getValue(Config.GENERAL_STARTAGE)
        return self
        

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
        
    
    def getActualValue(self, month : int, path : str, defaultValue=None) -> float:
        
        value = self.getValue(path, defaultValue)
        
        if (value is None or not isinstance(value, dict)) :
            return value
        
        previous = defaultValue
        for key in sorted(value.keys()):   # find a better algorithm sort is n"log(n
            month_key = Utils.years_to_months(float(key) - self. __start_age) 
            if month >= month_key:  # the key is greater to the month so we can return the previous value
                previous = value[key]
            else :
                return previous
        return previous
    

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
        
        
    
    def getStartAge(self) -> float:
        return self.getValue(Config.GENERAL_STARTAGE, Config.DEFAULT_STARTAGE)
    
    def getStartMonth(self) -> int :
        return self.getValue(Config.GENERAL_STARTMONTH, Config.DEFAULT_STARTMONTH)
     
    def getLegalRetirementAge(self) -> float :
        return self.getValue(Config.LEGAL_AGE, Config.DEFAULT_LEGALAGE)
    
    def getEarlyRetirementAge(self) -> float :
        return self.getValue(Config.EARLY_AGE, Config.DEFAULT_LEGALAGE)