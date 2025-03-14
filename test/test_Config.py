import pytest


from config import Config



@pytest.fixture
def config():
    return Config()

def test_load(config):
  
    try: 
        config.load("./data/config.json")
    except Exception as e:
        pytest.fail(f"Load failed with exception: {e}")
    
                    

def test_getNode(config):


    assert config.setValue("Property.Actual.Sell", 100) is None
    assert config.getNode("Property.Actual.Sell") == 100
    

    assert config.setValue("Property.Actual.Sell", "100") == 100
    assert config.getNode("Property.Actual.Sell") == '100'
    
    try :
        config.getNode("Unknown.Affordability")
        pytest.fail("Expected an KeyError for non-existent key")
    except KeyError:
        pass
     
            

def test_getValue(config):


    assert config.setValue("Property.Actual.Sell", 100) is None
    assert config.getValue("Property.Actual.Sell") == 100
    
    assert config.getValue("Unknown.Affordability") is None
    assert config.getValue("Property.Unknown") is None
    assert config.getValue("Property.Unknown",5) == 5
    

def test_getActualValue(config):

    config.setValue(Config.GENERAL_STARTMONTH, 1)
    config.setValue(Config.GENERAL_STARTAGE, 50)
    config.setValue("Test.Branch.Float", 1.2)
    config.setValue("Test.Branch.Dict", {"50" : 5000, "60.1" : 6000, "70" : 7000})
    
    assert config.getActualValue((50-50)*12+1, "Test.Branch.Float") == 1.2
    assert config.getActualValue((50-50)*12+1, "Test.Branch.Dict") == 5000
    assert config.getActualValue((51-50)*12+1, "Test.Branch.Dict") == 5000
    assert config.getActualValue((40-50)*12+1, "Test.Branch.Dict") is None
    assert config.getActualValue((40-50)*12+1, "Test.Branch.Dict", 21.0) == 21.0
    assert config.getActualValue((60-50)*12+1, "Test.Branch.Dict", 21.0) == 5000
    assert config.getActualValue((60.1-50)*12+1, "Test.Branch.Dict", 21.0) == 6000
    assert config.getActualValue((70-50)*12+1, "Test.Branch.Dict", 21.0) == 7000  
    assert config.getActualValue((80-50)*12+1, "Test.Branch.Dict") == 7000
    assert config.getActualValue((90-50)*12+1, "Test.Branch.Unknonw") is None

def test_setValue(config):
    
    assert config.setValue("Test.Test.Test" , 1) is None
    assert config.getValue("Test.Test.Test") == 1
   
    assert config.setValue("Test.Test.Test" , 1.0) == 1
    assert config.getValue("Test.Test.Test") == 1.0
    
    assert config.setValue("Test.Test.Test" , "1.1") == 1.0
    assert config.getValue("Test.Test.Test") == 1.1
    
    assert config.setValue(None,None) is None
    assert config.setValue('',None) is None
    
    assert config.setValue("Property.Actual.Sell", 100) is None
    assert config.getValue("Property.Actual.Sell") == 100
    old_value = config.setValue("Property.Actual.Sell", 150)
    assert old_value == 100
    assert config.getValue("Property.Actual.Sell") == 150
    
    assert config.setValue(Config.CALCULATION, {}) is None
    assert config.setValue(Config.GENERAL_INFLATION , 0.01) is None
    assert config.getValue(Config.GENERAL_INFLATION) == 0.01


def test_delete(config):
   
    assert config.setValue("Property.Actual.Sell", 100) is None
    assert config.delete("Property.Actual.Sell") == 100
    
    config.delete("Property.Actual")
    assert config.getValue("Property.Actual") is None
    
    config.setValue("Property.Actual.Sell", 100)
    config.setValue("Property.Actual.Worth", 200)
    assert config.delete("Property.Actual") == { 'Sell':100, 'Worth': 200 } 
    
def test_clear(config):
    config.clear()
    
    assert config.getValue("General") is None
    

def test_clone(config):
    data_copy = config.clone()
    
    assert data_copy.getValue("Property.Actual.Sell") == config.getValue("Property.Actual.Sell")
    assert data_copy is not config
    
def test_dump(config):
    try: 
        config.load("./data/config.json")
    except Exception as e:
        pytest.fail(f"Initialization failed with exception: {e}")
    
    config.dump_data()
    
    
def test_age_and_month(config):
    
    config.setValue(Config.GENERAL_STARTMONTH, 0)
    
    assert config.getStartMonth() == 0
    assert config.getStartAge() == 50
    assert config.getEndAge() == 50+30
    assert config.getEndMonth() == 30*12
    
    config.setValue(Config.GENERAL_STARTMONTH, 1)
    
    assert config.getStartMonth() == 1
    assert config.getStartAge() == 50
    assert config.getEndAge() == 50+30
    assert config.getEndMonth() == 30*12 + 1
    
    config.setValue(Config.GENERAL_STARTAGE, 51)
    
    assert config.getStartMonth() == 1
    assert config.getStartAge() == 51
    assert config.getEndAge() == 51+30
    assert config.getEndMonth() == 30*12 + 1
    
    config.setValue(Config.GENERAL_ENDAGE, 61)
    
    assert config.getStartMonth() == 1
    assert config.getStartAge() == 51
    assert config.getEndAge() == 61
    assert config.getEndMonth() == 10*12+1
    
    
def test_best_guess_for_number(config): 
    
    assert config.best_guess_for_number(0) == 0
    assert config.best_guess_for_number(1) == 1
    assert config.best_guess_for_number(50) == 50 
    assert config.best_guess_for_number(-1) == -1
    assert config.best_guess_for_number(0.1) == 0.1
    assert config.best_guess_for_number(-0.5) == -0.5
    assert config.best_guess_for_number(50.5) == 50.5
    assert config.best_guess_for_number("1") == 1
    assert config.best_guess_for_number("-1") == -1
    assert config.best_guess_for_number("1.1") == 1.1
    assert config.best_guess_for_number("-1.1") == -1.1
    assert config.best_guess_for_number("1.0") == 1
    assert config.best_guess_for_number("-1.0") == -1
    assert config.best_guess_for_number("a1") == "a1"
    assert config.best_guess_for_number(None) is None
    assert config.best_guess_for_number(True) is True
    assert config.best_guess_for_number(False) is False
    assert config.best_guess_for_number([]) == []
    assert config.best_guess_for_number({}) == {}   
    assert config.best_guess_for_number(set([1,2,3])) == set([1,2,3])
    
    
def test_interpolate(config):
    config.setValue("Test",{"1.0":1.0, "2.0" : "2.0", "3.0" : "3.0"})
    
    assert 1.0 == config.interpolate(0, "Test")
    assert 1.0 == config.interpolate(0.99, "Test")    
    assert 1.1 == config.interpolate(1.1, "Test")
    assert 1.9 == config.interpolate(1.9, "Test")         
    assert 2.0 == config.interpolate(2.0, "Test")    
    assert 3.0 == config.interpolate(3.0, "Test")    
    assert 3.0 == config.interpolate(4.0, "Test")   
    
    config.setValue("Test",{"3.0":-3.0, "2.0" : "-2.0", "1.0" : "-1.0"})
    assert -1.0 == config.interpolate(0, "Test")
    assert -1.0 == config.interpolate(0.99, "Test")    
    assert -1.1 == config.interpolate(1.1, "Test")
    assert -1.9 == config.interpolate(1.9, "Test")         
    assert -2.0 == config.interpolate(2.0, "Test")    
    assert -3.0 == config.interpolate(3.0, "Test")    
    assert -3.0 == config.interpolate(4.0, "Test")   
    
    config.setValue("Test","10")
    assert 10.0 == config.interpolate(0, "Test")
    assert 10.0 == config.interpolate(5, "Test")    
    assert 10.0 == config.interpolate(11, "Test")    
    

