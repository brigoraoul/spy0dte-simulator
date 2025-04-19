import pytest
from utils.options_helper import calculate_spread_strike_prices

@pytest.mark.parametrize("index_price, spread_type, expected", [
    (4012, "Bull Put", (4010, 3990)),  
    (4008, "Bull Put", (4010, 3990)),  
    (3995, "Bull Put", (3995, 3975)),  

    (4012, "Bear Call", (4010, 4030)), 
    (4008, "Bear Call", (4010, 4030)), 
    (3995, "Bear Call", (3995, 4015)), 
])
def test_calculate_spread_valid_cases(index_price, spread_type, expected):
    assert calculate_spread_strike_prices(index_price, spread_type) == expected

def test_calculate_spread_invalid_spread_type():
    with pytest.raises(ValueError, match="Invalid spread type. Use 'Bull Put' or 'Bear Call'."):
        calculate_spread_strike_prices(4000, "Invalid Type")
