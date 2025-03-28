

from config import Config
from iterations import Iterations


def test_parse() :
    a = [1, 2.1, "(60.0 ... 64.0,2)"]
    
    iteratons = Iterations()
    
    assert iteratons.parse(a) == [1,2.1, 60, 62, 64]
    
    assert iteratons.parse(["(60 ... 62,1)"]) == [60, 61, 62]
    assert iteratons.parse(["(  60 ... 62 , 1)"]) == [60, 61, 62]
    assert iteratons.parse(["(  60 ...  62  ,  1)"]) == [60, 61, 62]
    assert iteratons.parse(["( 60... 62 , 1)"]) == []
    assert iteratons.parse(["( 60 ...62 , 1)"]) == []
    
    assert iteratons.parse(["(60.1 ... 62.1,1)"]) == [60.1, 61.1, 62.1]
    assert iteratons.parse(["(60.1 ... 62.3, 1.1)"]) == [60.1, 61.2, 62.3]
    
    
def test_parse_iteratons() :
    config = Config()
    config.setValue("Test.Test","test")
    
    iterations = Iterations()
    iterations.parse_iterations(config)
    assert iterations.get_iterations() == {}
    
    config.setValue(Config.ITERATIONS, { "Test1" : [1 , 1]})
    iterations.parse_iterations(config)
    assert iterations.get_iterations() == {"Test1": [1, 1]}
    
    config.setValue(Config.ITERATIONS, { "Test1" : [1 , 2, "(10 ... 11, 1)"] })
    iterations.parse_iterations(config)
    assert iterations.get_iterations() == {"Test1": [1, 2, 10 , 11]}
    
    config.setValue(Config.ITERATIONS, { "Test1" : [1 , 2], "Test2" : [ "(10.0 ... 11.0, 0.5)" ] })
    iterations.parse_iterations(config)
    assert iterations.get_iterations() == {"Test1": [1, 2], "Test2" : [10, 10.5 , 11]}
    
    config.setValue(Config.ITERATIONS, { "Test1" : ["(1 ... 2,1)"], "Test2" : [ "(10.0 ... 11.0, 0.5)" ] })
    iterations.parse_iterations(config)
    assert iterations.get_iterations() == {"Test1": [1, 2], "Test2" : [10, 10.5 , 11]}
    
    config.setValue(Config.ITERATIONS, { "Pension.EarlyRetirement" : ["(62.0 ... 63.5, 0.5)"], "WealthManagement.HistoricalYear":  ["(1985 ... 1987, 1)"]})
    iterations.parse_iterations(config)
    assert iterations.get_iterations() == { "Pension.EarlyRetirement" : [62.0, 62.5, 63, 63.5], "WealthManagement.HistoricalYear":  [1985, 1986, 1987]}
    