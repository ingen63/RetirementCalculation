


from config import Config


class TaxHandler:
    
    @staticmethod
    def income_tax(config : Config, income : float) -> float :
        return 0.*income
    
    
    @staticmethod
    def capital_tax(config : Config, capital : float) -> float :
        return 0.*capital
    
    @staticmethod
    def lumpsum_tax(config : Config, lumpsum : float) -> float :
        return 0.*lumpsum