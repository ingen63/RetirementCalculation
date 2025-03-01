


from config import Config


class TaxHandler:
    
    @staticmethod
    def income_tax(config : Config, income : float) -> float :
        local_tax_adjustment = config.getValue(Config.TAXES_TAXRATE, 2.0)
        tax_rate = config.interpolate(income, Config.TAXES_INCOME)
        return tax_rate * local_tax_adjustment * income
    
    
    @staticmethod
    def capital_tax(config : Config, capital : float) -> float :
        local_tax_adjustment = config.getValue(Config.TAXES_TAXRATE, 2.0)
        tax_rate = config.interpolate(capital, Config.TAXES_CAPITAL)
        return tax_rate *local_tax_adjustment* capital
    
    @staticmethod
    def lumpsum_tax(config : Config, lumpsum : float) -> float :
        parameters = config.getValue(Config.TAXES_PENSIONCAPITAL, Config.DEFAULT_TAXES_PENSIONCAPITAL)
        return lumpsum*(lumpsum*lumpsum*parameters[0] + lumpsum*parameters[1] + parameters[2])