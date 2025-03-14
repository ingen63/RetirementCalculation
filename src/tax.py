
from config import Config
from property import Property


class TaxHandler:
    
    @staticmethod
    def income_tax(config : Config, income : float) -> float :
        return TaxHandler.__tax_calculation(config, Config.TAXES_INCOME, income)
    
    
    @staticmethod
    def capital_tax(config : Config, capital : float) -> float :
        return TaxHandler.__tax_calculation(config, Config.TAXES_CAPITAL, capital)

    
    @staticmethod
    def lumpsum_tax(config : Config, lumpsum : float) -> float :
        return TaxHandler.__tax_calculation(config, Config.TAXES_PENSIONCAPITAL, lumpsum)
    
    @staticmethod
    def __tax_calculation(config : Config, tax_type : str, value : float, default_taxrate : float = 0.0) -> float :
        local_tax_adjustment = config.getValue(Config.TAXES_TAXRATE, 2.0)
        tax_rate = config.interpolate(value, tax_type, default_taxrate)
        return tax_rate *local_tax_adjustment* value
        
    
    def sales_tax(config : Config, property : Property) -> float :
        profit = property.get_worth() - property.get_price()
        
        tax_rates = config.getValue(Config.TAXES_SALES)
        keys = list(tax_rates.keys())
        keys.sort(key=lambda obj: (config.best_guess_for_number(obj)))
        tax = 0.0
        for key in keys:
            float_key = config.best_guess_for_number(key)
            if (profit < float_key) :
                tax += tax_rates[key] * profit
                break
            else :
                tax += tax_rates[key] * float_key
                profit -= float_key

        tax = tax * (1.0-config.getValue(Config.TAXES_SALESTAXREDUCTION, 0.0))
        return tax
        
        
        