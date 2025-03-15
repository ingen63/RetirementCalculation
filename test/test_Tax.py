import json
import pytest
from config import Config
from property import Property
from tax import TaxHandler


@pytest.fixture
def config():
    sample_data = {
        "Taxes" : {

            "Sales" : { "4000" : 0.1, "6000" : 0.15, "8000" : 0.2, "12000" : 0.25, "20000" : 0.3, "50000" : 0.35, "100000": 0.4, "10000000" : 0.4}, 
            "SalesTaxReduction": 0.44
    },
    }
    
    config = Config()
    config.loads(json.dumps(sample_data))
    return config



def test_tax_calculation(config):
    # Arrange
    
    value = 100.0
    default_taxrate = 0.5

    # Act
    assert TaxHandler.tax_calculation(config, "Taxes.Example", value, default_taxrate) == value*default_taxrate*2.0
    
    
    config.setValue("Taxes.TaxRate", 2.1),
    assert TaxHandler.tax_calculation(config, "Taxes.Example", value, default_taxrate) == value*default_taxrate*2.1
    
    config.setValue("Taxes.Example",{ "0": 0.0, "500" : 0.05, "1000" : 0.1, "2000" : 0.2, "4000" : 0.4})
    
    assert TaxHandler.tax_calculation(config, "Taxes.Example", 0, default_taxrate) == 0.0
    assert TaxHandler.tax_calculation(config, "Taxes.Example", 100, default_taxrate) == 100.0*0.01*2.1
    assert TaxHandler.tax_calculation(config, "Taxes.Example", 400, default_taxrate) == 400.0*0.04*2.1
    assert TaxHandler.tax_calculation(config, "Taxes.Example", 500, default_taxrate) == 500.0*0.05*2.1
    assert TaxHandler.tax_calculation(config, "Taxes.Example", 1000, default_taxrate) == 1000.0*0.1*2.1
    
    assert TaxHandler.tax_calculation(config, "Taxes.Example", -10, default_taxrate) == 0
    assert TaxHandler.tax_calculation(config, "Taxes.Example", 4000, default_taxrate) == 4000.0*0.4*2.1
    assert TaxHandler.tax_calculation(config, "Taxes.Example", 10000, default_taxrate) == 10000.0*0.4*2.1
    

#   "Sales" : { "4000" : 0.1, "6000" : 0.15, "8000" : 0.2, "12000" : 0.25, "20000" : 0.3, "50000" : 0.35, "100000": 0.4, "10000000" : 0.4}, 
def test_sales_tax(config):
    property = Property(Config({"Name": "House", "Worth": 4000, "Price" : 1000}))
    reduction = 1.0 - config.getValue("Taxes.SalesTaxReduction")
    assert TaxHandler.sales_tax(config, property) == round(3000.0*0.1*reduction,2)
    
    config.setValue("Taxes.SalesTaxReduction",0.0)
    reduction = 1.0 - config.getValue("Taxes.SalesTaxReduction")
    
    property.set_worth(5000)
    assert TaxHandler.sales_tax(config, property) == round(4000.0*0.1*reduction,2)
    
    property.set_worth(6000)
    assert TaxHandler.sales_tax(config, property) == round((4000.0*0.1+1000*0.15)*reduction,2)
    
    property.set_worth(12000)
    assert TaxHandler.sales_tax(config, property) == round((4000.0*0.1+6000*0.15+1000*0.2)*reduction,2)
    
    property.set_worth(101000)
    assert TaxHandler.sales_tax(config, property) == round(29400.0*reduction,2)
    
    property.set_worth(201000)
    assert TaxHandler.sales_tax(config, property) == round(69400.0*reduction,2)
    
    property.set_worth(501000)
    assert TaxHandler.sales_tax(config, property) == round(189400.0*reduction,2)
    
    config.setValue("Taxes.SalesTaxReduction",0.44)
    reduction = 1.0 - config.getValue("Taxes.SalesTaxReduction")
    
    property.set_price(745000.0)    
    property.set_worth(1590669.0)
    assert TaxHandler.sales_tax(config, property) == round(183493.86,2)
    
    config.setValue(Config.TAXES_SALES,None)
    assert TaxHandler.sales_tax(config, property) == 0.0
    
    
    
    