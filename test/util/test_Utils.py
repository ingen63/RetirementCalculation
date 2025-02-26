
from src.util.utils import Utils
    

        
 
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
    
    

def test_month_to_years():
        assert Utils.month_to_years(12) == 1
        assert Utils.month_to_years(30) == 2.5
        assert Utils.month_to_years(0) == 0
        assert Utils.month_to_years(-12) == -1
        assert Utils.month_to_years(21) == 1.75
        assert Utils.month_to_years(1) == 1/12
        assert Utils.month_to_years(2) == 2/12
        