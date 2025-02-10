
from src.util.config import Config
from src.util.utils import Utils
    



def test_convert_to_monthly_list():
   
    config = Config()
    config.setValue(Config.GENERAL_START,1000)
    config.setValue(Config.GENERAL_AGE,50)
    
    input_list = {1200 :12, 2400: 24}
    expected_output = {200*12 : 12, 1400*12 : 24} 
    __test_convert_to_monthly_list(config, input_list, expected_output) 
    
    input_list = {51 :51, 1002: 24}  # Mixed input age and years
    expected_output = {1*12 : 51, 2*12 : 24} 
    __test_convert_to_monthly_list(config, input_list, expected_output)   
    
    input_list = {1200 :12}
    expected_output = {200*12 : 12} 
    __test_convert_to_monthly_list(config, input_list, expected_output)  

    input_list = {}
    expected_output = {} 
    __test_convert_to_monthly_list(config, input_list, expected_output)  
    
    config.convert_to_monthly_list(None, False)
    
    
def __test_convert_to_monthly_list(config, input, expected):
    config.setValue('Test',input)
    monthly_list = config.convert_to_monthly_list('Test', False)
    assert monthly_list == expected
   
        
 
def test__positive_with_positive_values():
    assert Utils.positive("Test with positive values", 1, 2, 3) is True

def test__positive_with_negative_values():
    assert Utils.positive("Test with negative values", -1, 2, 3) is False

def test__positive_with_mixed_values():
    assert Utils.positive("Test with mixed values", 1, -2, 3) is False

def test__positive_with_zero_values():
    assert Utils.positive("Test with zero values", 0, 2, 3) is True

def test__positive_with_all_negative_values():
    assert Utils.positive("Test with all negative values", -1, -2, -3) is False

def test__not_null_positive_values():
    assert Utils.not_null("Test with positive values", 1, 2, 3) is True

def test_positive_with_negative_values():
    assert Utils.not_null("Test with negative values", -1, 2, 3) is True   

def test_positive_with_zero_values():
    assert Utils.not_null("Test with zero values", 0, 2, 3) is False
    
    
def test_years_to_months():
        assert Utils.years_to_months(1) == 12
        assert Utils.years_to_months(2.5) == 30
        assert Utils.years_to_months(0) == 0
        assert Utils.years_to_months(-1) == 0
        assert Utils.years_to_months(1.75) == 21
        assert Utils.years_to_months(6.99999/12) == 7

def test_month_to_years():
        assert Utils.month_to_years(12) == 1
        assert Utils.month_to_years(30) == 2.5
        assert Utils.month_to_years(0) == 0
        assert Utils.month_to_years(-12) == 0
        assert Utils.month_to_years(21) == 1.75
        assert Utils.month_to_years(1) == 1/12
        assert Utils.month_to_years(2) == 2/12
        


def test_getActualValue():
    input_dict = {5: 10, 12: 20, 24: 30}
 
    assert Utils.getActualValue(-1, input_dict) == 0
    assert Utils.getActualValue(0, input_dict)  == 0
    assert Utils.getActualValue(5, input_dict)  == 10
    assert Utils.getActualValue(11, input_dict) == 10
    assert Utils.getActualValue(12, input_dict) == 20
    assert Utils.getActualValue(13, input_dict) == 20
    assert Utils.getActualValue(24, input_dict) == 30
    assert Utils.getActualValue(25, input_dict) == 30
    assert Utils.getActualValue(36, {}) == 0