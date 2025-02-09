
from src.util.utils import Utils
    

def test_convert_to_monthly_list_positive_years():
    years = 2
    input_list = [1200, 2400]
    expected_output = [1200.0] * 12 + [2400.0] * 12
    monthly_list = Utils.convert_to_monthly_list(years, input_list, False)
    assert monthly_list == expected_output
    

    years = 2.5
    input_list = [100, 200, 300]
    expected_output = [100.0] * 12 + [200.0] * 12 + [300] * 6
    monthly_list = Utils.convert_to_monthly_list(years, input_list, False)
    assert monthly_list == expected_output

    years = 2+8/12+0.0000000001
    input_list = [100, 200, 300]
    expected_output = [100.0] * 12 + [200.0] * 12 + [300] * 8
    monthly_list = Utils.convert_to_monthly_list(years, input_list)
    assert monthly_list == expected_output


def test_convert_to_monthly_list_zero_years():
    years = 0
    input_list = [1200, 2400]
    expected_output = []
    monthly_list = Utils.convert_to_monthly_list(years, input_list)
    assert monthly_list == expected_output


def test_convert_to_monthly_list_negative_years():
    years = -1
    input_list = [1200, 2400]
    expected_output = []
    monthly_list = Utils.convert_to_monthly_list(years, input_list)
    assert monthly_list == expected_output


def test_convert_to_monthly_list_years_exceeding_input_list():
    years = 3
    input_list = [1200, 2400]
    expected_output = []
    monthly_list = Utils.convert_to_monthly_list(years, input_list)
    assert monthly_list == expected_output
    
    years = 2.0000000001
    input_list = [1200, 2400]
    expected_output = []
    monthly_list = Utils.convert_to_monthly_list(years, input_list)
    assert monthly_list == expected_output


def test_convert_to_monthly_list_empty_input_list():
    years = 2
    input_list = []
    expected_output = []
    monthly_list = Utils.convert_to_monthly_list(years, input_list)
    assert monthly_list == expected_output
  
   
        
 
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
        assert Utils.years_to_months(6.99999/12) == 6

def test_month_to_years():
        assert Utils.month_to_years(12) == 1
        assert Utils.month_to_years(30) == 2.5
        assert Utils.month_to_years(0) == 0
        assert Utils.month_to_years(-12) == 0
        assert Utils.month_to_years(21) == 1.75
        assert Utils.month_to_years(1) == 1/12
        assert Utils.month_to_years(2) == 2/12
        
