
import logging
import math


class Utils:
    
    MONTH = 12

    @staticmethod
    def __create_yearly_list(years, value):
        """
        Create a list of yearly values.

        Args:
            years (int): The number of years.
            value (float): The value to be repeated yearly.

        Returns:
            list: A list of yearly values until retirement. If the number of years until retirement
                  is less than or equal to 0, an empty list is returned.
        """
        if years <= 0:
            return []

        years = math.ceil(years)
        logging.debug(f"Creating yearly list with {years+1} years and value {value}")
        return [value] * years
    

    
    @staticmethod
    def getActualValue(month, input_dict):
        
        value = 0
        for key in sorted(input_dict.keys()):   # find a better algorithm soert is n"log(n)
            if key <= month:  # the key is less than or equal to the month so we can use it directly
                value = input_dict[key]
            else: 
               break
        return value
            
        
    @staticmethod
    def positive(text, *values):
        """
        Checks if all provided values are positive.

        Args:
            text (str): A message to display if a negative value is found.
            *values (float): Variable length argument list of values to check.

        Returns:
            bool: True if all values are positive, False if any value is negative.
        """
        for value in values:
            if value < 0:
                print(f"Invalid negative value: {value:.2f} found! {text}")
                return False
        return True
    
    
    
    @staticmethod
    def not_null(text, *values):
        """
        Checks if the provided values are not zero.

        Args:
            text (str): A description or identifier for the context in which this check is being performed.
            *values: A variable number of values to be checked.

        Returns:
            bool: True if none of the values are zero, False otherwise.

        Prints:
            A message indicating which method (identified by `text`) found an invalid zero value.
        """
        for value in values:
            if value == 0:
                print(f"Invalid zero value in method {text} found!")
                return False
        return True

    @staticmethod
    def years_to_months(years):
        """
        Converts the number of years to months and rounds down to the nearest integer.

        Args:
            years (int): The number of years.

        Returns:
            int: The number of months in the given number of years.
        """
        if years <= 0:
            years=0

        return round(years * Utils.MONTH)
    
    @staticmethod
    def month_to_years(month):
        if month <= 0:
            month=0
        return month/Utils.MONTH
        
    
    
