import json
import copy
import re


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
    MONEYFLOWS_INCOME = "MoneyFlows.Income"
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
    
    DEFAULT_TAXES_PENSIONCAPITAL = [-9.6001E-15, 8.034e-8,4.0908e-2]
    
    DEFAULT_STARTMONTH = 1
    DEFAULT_ENDMONTH = DEFAULT_MAXPERIOD*MONTHS + DEFAULT_STARTMONTH
    
    MAX_AGE = 120
    
    LOGGER_SUMMARY= "logger.summary"
        
  
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
    
    def replace_variables(self):
        # replace variables in the config
        keys = self.defined_keys()

        for key in list(keys):
            values = self.getValue(key)
            if isinstance(values, dict):
                iteration_dict = values.copy()
                
                for sub_key in iteration_dict:
                    new_key = self.__replace_variable(sub_key)
                    if new_key is not None and new_key != sub_key:
                        value = values[sub_key]
                        del values[sub_key]
                        values[new_key] = value

            else:
                value = self.__replace_variable(values)
                if value is not None and value != values:
                    self.setValue(key, value)

                   
        

    def __replace_variable(self, key):
        if not isinstance(key, str): 
            return None
           
        match = re.search(r'\{(.*?)\}', key)
        if match :
            replacement = match.group(1)
            return str(self.getValue(replacement))
          
        return key 
        
        
    def getNode(self, path : str):
        if path == '' or path is None:
            return None
        
        keys = path.split('.')
        current =  self.__data

        for key in keys:
            current = current[key]
        return current
    
            
    def getValue(self, path : str, defaultValue=None) :   
        try:
            node = self.getNode(path)
            return self.best_guess_for_number(node)
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
    
    
    def interpolate(self, x : float, path : str, defaultValue=None) -> float:
        
                
        value = self.getValue(path, defaultValue)
        
        if value is None or not isinstance(value, dict) :
            return self.best_guess_for_number(value)
        
        keys = sorted(value.keys())
        previous_x = float(keys[0])
        previous_y = self.best_guess_for_number(value[keys[0]])
        for key in keys:
            next_x = float(key)
            next_y = self.best_guess_for_number(value[key])
            if next_x >= x :
                break
            else :            
                previous_x = next_x 
                previous_y = next_y
        if  next_x == previous_x : 
            return previous_y
         
        fraction = (next_x - x)/(next_x - previous_x)
        return previous_y*fraction + next_y*(1.0-fraction)

         
        

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
        

    def custom_split(self, path : str):
    # Regulärer Ausdruck zum Finden der Teile außerhalb geschweifter Klammern
        parts = re.split(r'(\{.*?\})', path)  # Teile anhand der Klammern aufteilen
        result = []
        for part in parts:
            if part.startswith("{") and part.endswith("}"):
                result.append(part)  # Ganze Klammern beibehalten
            else:
                result.extend(part.split('.'))  # Split bei Punkten außerhalb Klammern
        return [item for item in result if item]  # Leere Strings entfernen
    
 
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
         
    def list_available_keys(self, data : dict, prefix : str) -> list:
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
        

        
    def defined_keys(self):
        data = []
        for variable  in Config.__dict__:
            if variable.isupper() and not(variable.startswith('__') and not variable.endswith('__')):
                key = self.__getattribute__(variable)
                if isinstance(key,str) and key[0].isalpha() and key[0].isupper() :
                   data.append(key)
         
         

        # Filtern der Leaves
        leaves = [item for item in data if not any(item + "." == other[:len(item) + 1] for other in data)]

        return leaves
       
        
    
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