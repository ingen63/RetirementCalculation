

class Utils:
    

    MONTH = 12
    
        
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
    def years_to_months(years : float) -> int:
        """
        Converts the number of years to months and rounds down to the nearest integer.

        Args:
            years (int): The number of years.

        Returns:
            int: The number of months in the given number of years.
        """
        return round(years * Utils.MONTH)
    
    @staticmethod
    def month_to_years(month : int) -> float:
        return month/Utils.MONTH
        
    
    
