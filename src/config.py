import json
import copy


class Config:
    
    MONTHS = 12

    GENERAL = "General"
    GENERAL_STARTAGE = "General.StartAge"
    GENERAL_STARTMONTH = "General.StartMonth"
    GENERAL_ENDAGE = "General.EndAge"
    GENERAL_WEALTH = "General.Wealth"
    
    TAXES_TAXRATE = "Taxes.TaxRate"
    TAXES_INCOME = "Taxes.Income"
    TAXES_CAPITAL = "Taxes.Capital"
    TAXES_PENSIONCAPITAL = "Taxes.PensionCapital"
    

    PENSION = "Pension"
    PENSION_EARLYRETIREMENT = "Pension.EarlyRetirement"
    PENSION_LEGALRETIREMENT = "Pension.LegalRetirement"
    PENSION_PRIVATE = "Pension.Private"
    PENSION_PRIVATE_CAPITAL = "Pension.Private.Capital"
    PENSION_PRIVATE_LUMPSUMRATIO = "Pension.Private.LumpsumRatio"
    PENSION_PRIVATE_CONVERSIONRATE = "Pension.Private.ConversionRate"
    PENSION_PRIVATE_CONTRIBUTION = "Pension.Private.Contribution"
    PENSION_PRIVATE_INTEREST = "Pension.Private.Interest"
    PENSION_PRIVATE_PENSION = "Pension.Private.Pension"
    PENSION_LEGAL = "Pension.Legal"

    MONEYFLOWS = "MoneyFlows"
    MONEYFLOWS_SAVINGS = "MoneyFlows.Savings"
    MONEYFLOWS_SPENDINGS = "MoneyFlows.Spendings"
    MONEYFLOWS_EXTRA = "MoneyFlows.Extra"
    
    REALESTATE = "RealEstate"
    REALESTATE_THRESHOLDYEARS = "RealEstate.ThresholdYears"
    REALESTATE_BUYAFTERSELL = "RealEstate.BuyAfterSell"
    REALESTATE_AFFORDABILITY = "RealEstate.Affordability"
    REALESTATE_AFFORDABILITY_SUSTAINABILITY = "RealEstate.Affordability.Sustainability"
    REALESTATE_AFFORDABILITY_MORTAGEINTEREST = "RealEstate.Affordability.MortageInterest"
    REALESTATE_AFFORDABILITY_CAPITALCONTRIBUTION = "RealEstate.Affordability.CapitalContribution"
    REALESTATE_AFFORDABILITY_FIXCOSTS = "RealEstate.Affordability.FixCosts"
    REALESTATE_PROPERTIES = "RealEstate.Properties"

    CALCULATION = "Calculation"
    CALCULATION_METHOD = "Calculation.Method"
    CALCULATION_SINGLE = "Calculation.Single"
    CALCULATION_SINGLE_INFLATION = "Calculation.Single.Inflation"
    CALCULATION_SINGLE_PERFORMANCE = "Calculation.Single.Performance"
    CALCULATION_HISTORICAL = "Calculation.Historical"
    CALCULATION_HISTORICAL_PORTFOLIOBALANCE = "Calculation.Historical.portfolioBalance"
    CALCULATION_HISTORICAL_HISTORICALDATA = "Calculation.Historical.historicalData"
    CALCULATION_SCENARIOS = "Calculation.Scenarios"

    DEFAULT_STARTAGE = 50.0
    DEFAULT_MAXPERIOD = 30.0
    DEFAULT_LEGALAGE = 65.0
    
    DEFAULT_REALESTATE_THRESHOLDYEARS = 2
    DEFAULT_REALESTATE_BUYAFTERSELL = True
    
    DEFAULT_STARTMONTH = 1
    DEFAULT_ENDMONTH = DEFAULT_MAXPERIOD*MONTHS + DEFAULT_STARTMONTH
        
  
    def __init__(self, data = None ):
        if (data is None) : 
            data = {}
        self.__data = data
    
            
    def load(self, file_path : str):
        with open(file_path, 'r') as file:
            self.__data = json.load(file)
        return self
     
    def loads(self, json_data : str):
        self.__data = json.loads(json_data)
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
            return self.best_guess_for_number(current)
        except KeyError:
        #    logging.debug(f"KeyError: {path} not found returning default value: {defaultValue}")
            return self.best_guess_for_number(defaultValue)
        
    
    def getActualValue(self, month : int, path : str, defaultValue=None) -> float:
        
        value = self.getValue(path, defaultValue)
        
        if value is None or not isinstance(value, dict) :
            return value
        
        previous = defaultValue
        for key in sorted(value.keys()):   # find a better algorithm sort is n"log(n
            month_key = self.age2months(float(key)) 
            if month >= month_key:  # the key is greater to the month so we can return the previous value
                previous = value[key]
            else :
                return self.best_guess_for_number(previous)
        return self.best_guess_for_number(previous)
    

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
                current[keys[i]] = self.best_guess_for_number(value)
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
  
    def best_guess_for_number(self, value):
    
        try:
            keys = value.split(".")
            number = keys[0]
            decimal = None
            if (len(keys) > 1):
                decimal = keys[1]
            try:
                if decimal is None or decimal == "0":
                   return int(number)
                else:
                    return float(value)
            except ValueError:
                return value
        except (ValueError, AttributeError):
            return value

    
    
    def age2months(self, age) -> int:
        years_since_start = self.best_guess_for_number(age) - self.getStartAge()
        return self.getStartMonth() + round(years_since_start*Config.MONTHS)
    
    def month2age(self, month) -> float:
        months_since_start = month - self.getStartMonth()
        return self.getStartAge() + months_since_start/Config.MONTHS
         
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
        
     
    def to_json(self):
        data = {}
        for key  in Config.__dict__:
            if key.isupper() and not(key.startswith('__') and not key.endswith('__')):
                keys = key.split('_')
                current = data
                for k in keys[:-1]:
                    if k not in current:
                        current[k] = {}
                    current = current[k]
                key = self.__getattribute__(key)
                if (isinstance(key, str)):
                   current[keys[-1]] = self.getValue(key, {})
                
        return json.dumps(data, indent=4)
        
    
    def getStartAge(self) -> float:
        return self.getValue(Config.GENERAL_STARTAGE, Config.DEFAULT_STARTAGE)
    
    def getStartMonth(self) -> int :       
        return self.getValue(Config.GENERAL_STARTMONTH, Config.DEFAULT_STARTMONTH)
    
    def getEndAge(self) -> float :
        return self.getValue(Config.GENERAL_ENDAGE, self.getStartAge()+Config.DEFAULT_MAXPERIOD)
    
    def getEndMonth(self) -> int :
        return self.age2months(self.getEndAge())
     
    def getLegalRetirementAge(self) -> float :
        return self.getValue(Config.PENSION_LEGALRETIREMENT, Config.DEFAULT_LEGALAGE)
    
    def getEarlyRetirementAge(self) -> float :
        return self.getValue(Config.PENSION_EARLYRETIREMENT, Config.DEFAULT_LEGALAGE)