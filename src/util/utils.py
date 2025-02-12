
import logging
import math


class Utils:
    
    MONTH = 12
    MAGIC_YEAR = 200
    
    @staticmethod
    def getActualValue(month : int, input_dict : dict) -> float:
        
        value = 0
        for key in sorted(input_dict.keys()):   # find a better algorithm soert is n"log(n)
            if key <= month:  # the key is less than or equal to the month so we can use it directly
                value = input_dict[key]
            else: 
               break
        return value
        
    @staticmethod
    def getValue(input : dict, key, defaultValue=0.0) :
        if key in input:
            return input[key]
        else:
            return defaultValue    
        
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
    def adjust_for_inflation(month : int, value : float, inflation : float):
        return value*((1+inflation)**month)
    
        
    @staticmethod
    def years_to_months(years : float) -> int:
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
    def month_to_years(month : int) -> float:
        if month <= 0:
            month=0
        return month/Utils.MONTH
        
    
    
