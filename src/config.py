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
    GENERAL_INFLATION = "General.Inflation"
    GENERAL_PERFORMANCE = "General.Performance"
    
    TAXES_TAXRATE = "Taxes.TaxRate"
    TAXES_INCOME = "Taxes.Income"
    TAXES_CAPITAL = "Taxes.Capital"
    TAXES_PENSIONCAPITAL = "Taxes.PensionCapital"
    TAXES_SALES = "Taxes.Sales"
    TAXES_SALESTAXREDUCTION = "Taxes.SalesTaxReduction"
    

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

    CALCULATION_HISTORICAL = "Calculation.Historical"
    CALCULATION_HISTORICAL_STARTAGE = "Calculation.Historical.StartAge"
    CALCULATION_HISTORICAL_ENDAGE = "Calculation.Historical.EndAge"
    CALCULATION_HISTORICAL_STARTMONTH = "Calculation.Historical.StartMonth"
    CALCULATION_HISTORICAL_PORTFOLIOBALANCE = "Calculation.Historical.PortfolioBalance"
    CALCULATION_HISTORICAL_DATA = "Calculation.Historical.Data"
    CALCULATION_HISTORICAL_YEAR = "Calculation.Historical.Year"
    
    CALCULATION_SCENARIOS = "Calculation.Scenarios"
    CALCULATION_SCENARIOS_NAME = "Name"
    CALCULATION_SCENARIOS_DESCRIPTION = "Description"
    CALCULATION_SCENARIOS_PARAMETERS = "Parameters"

    DEFAULT_STARTAGE = 50.0
    DEFAULT_MAXPERIOD = 30.0
    DEFAULT_LEGALAGE = 65.0
    
    DEFAULT_REALESTATE_THRESHOLDYEARS = 2
    DEFAULT_REALESTATE_BUYAFTERSELL = True

    
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
        
        
    def getNode(self, path: str):
        """
        Retrieves a nested value from the configuration data based on a dot-separated path.

        This function traverses the nested dictionary structure of the configuration data
        using the provided path. Each part of the path separated by dots represents a level
        in the nested structure.

        Args:
            path (str): A dot-separated string representing the path to the desired node
                        in the configuration data.

        Returns:
            The value at the specified path in the configuration data. If the path is empty
            or None, returns None. If the path is valid, returns the corresponding value,
            which could be a nested dictionary, a list, or a primitive value.

        Raises:
            KeyError: If any part of the path does not exist in the nested structure.
        """
        if path == '' or path is None:
            return None

        keys = path.split('.')
        current =  self.__data

        for key in keys:
            current = current[key]
        return current
    
            
    def getValue(self, path : str, defaultValue=None) :
        """
        Retrieves a nested value from the configuration data based on a dot-separated path.

        This function traverses the nested dictionary structure of the configuration data
        using the provided path. Each part of the path separated by dots represents a level
        in the nested structure.

        Args:
            path (str): A dot-separated string representing the path to the desired node
                        in the configuration data.
            defaultValue: If any part of the path does not exist in the nested structure it returns the defaultValue
            
        Returns:
            The value at the specified path in the configuration data. If the path is empty
            or None, returns None. If the path is valid, returns the corresponding value,
            which could be a nested dictionary, a list, or a primitive value. For primitive values it will try to convert the value to a number.
            
        """   
        try:
            node = self.getNode(path)
            return self.best_guess_for_number(node)
        except KeyError:
            return self.best_guess_for_number(defaultValue)
        
    
    def getActualValue(self, month: int, path: str, defaultValue=None) -> float:
        """
        Retrieves the actual value for a given month based on a configuration path.

        This function looks up a value in the configuration based on the provided path,
        and returns the appropriate value for the specified month. If the value is a
        dictionary of time-based entries, it finds the most recent applicable value.

        Args:
            month (int): The month for which to retrieve the value.
            path (str): The configuration path to look up.
            defaultValue (Any, optional): The default value to return if no value is found. Defaults to None.

        Returns:
            float: The actual value for the specified month. If the value is not time-based,
                   it returns the direct value. For time-based values, it returns the most
                   recent applicable value converted to a number if possible.
        """
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
    
    
    def interpolate(self, x: float, path: str, defaultValue=None) -> float:
        """
        Interpolates a value based on a given x-coordinate and a configuration path.

        This function retrieves a set of key-value pairs from the configuration using the provided path,
        and performs linear interpolation to estimate the y-value corresponding to the given x-value.

        Args:
            x (float): The x-coordinate for which to interpolate the y-value.
            path (str): The configuration path to retrieve the interpolation data.
            defaultValue (Any, optional): The default value to return if no data is found at the given path. Defaults to None.

        Returns:
            float: The interpolated y-value corresponding to the input x-value.
                   If the input data is not a dictionary or is None, returns the best numeric guess of the input value.
                   If x is outside the range of the data, returns the y-value of the nearest data point.
                   If there's only one data point, returns that y-value.

        """
        value = self.getValue(path, defaultValue)

        if value is None or not isinstance(value, dict):
            return self.best_guess_for_number(value)

        keys = sorted(value.keys(), key=lambda x: float(x))
        previous_x = float(keys[0])
        previous_y = self.best_guess_for_number(value[keys[0]])
        for key in keys:
            next_x = float(key)
            next_y = self.best_guess_for_number(value[key])
            if next_x >= x:
                break
            else:
                previous_x = next_x 
                previous_y = next_y
        if next_x == previous_x:
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
                current[keys[i]] = value
             #   logging.debug(f"i: {i} key: {keys[i]} keys: {keys} current: {current} __data: {self.__data}")
                return old_value
            
    def setValues(self, values : dict) :
        values_config = Config(values)
        for key in values_config.defined_keys():
            if values_config.exists(key):
                value = values_config.getValue(key)
                self.setValue(key, value)
            

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
        """
        Attempts to convert a given value to the most appropriate numeric type (int or float).

        This function tries to interpret the input as a number. If the input is a string
        representation of an integer or float, it will be converted to the corresponding
        numeric type. If conversion is not possible, the original value is returned.

        Args:
            value: The value to be converted. Can be of any type.

        Returns:
            int: If the value represents an integer (no decimal part).
            float: If the value represents a floating-point number.
            Any: The original value if it cannot be converted to a number.

        Note:
            - For string inputs, it uses "." as the decimal separator.
            - If the input is already a numeric type, it will be returned as-is.
        """
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