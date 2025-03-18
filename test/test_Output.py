from output import Output


def test_add_result():

    Output.reset()
    
    Output.add_result([1,"Test0"],"Value0")
    assert Output.output["Test0"][1] == "Value0"
    
    Output.next_scenario()
    Output.add_result([2,"Test1"],"Value1")
    assert Output.output["Test0"][1] == "Value0"
    assert Output.output["Test1"][1] == ""
    assert Output.output["Test0"][2] == ""
    assert Output.output["Test1"][2] == "Value1"
    
    Output.add_result([3,"Test2"],"TestKeyValue","TestKey")
    assert Output.output["Test0"][1] == "Value0"
    assert Output.output["Test1"][1] == ""
    assert Output.output["TestKey"][1] == ""
    assert Output.output["Test0"][2] == ""
    assert Output.output["Test1"][2] == "Value1"
    assert Output.output["TestKey"][2] == "TestKeyValue"
    
def test_next_scenario():
    
    Output.reset()
    
    Output.add_result([1,"Test0"],"Value0")
    Output.add_result([2,"Test1"],"Value1")
    
    assert Output.output["Test0"][1] == "Value0"
    assert Output.output["Test1"][1] == "Value1"
    
    Output.next_scenario()
    assert Output.output["Test0"][1] == "Value0"
    assert Output.output["Test1"][1] == "Value1"
    assert Output.output["Test0"][2] == ""
    assert Output.output["Test0"][2] == ""
    
    
def test_get_name():
    
    Output.reset()
    assert Output.get_name() is not None
    
    Output.add_result(Output.SCENARIO_NAME,"Scenario Name")
    assert Output.get_name() == "Scenario Name"
    

def test_add_ranking() :
    Output.reset()
    Output.add_ranking(Output.TOTAL_ASSETS[1], 2021, 10000)
    assert Output.ranking[Output.TOTAL_ASSETS[1]][2021] == 10000
    
    Output.add_ranking(Output.TOTAL_ASSETS[1], 2022, 12000)
    assert Output.ranking[Output.TOTAL_ASSETS[1]][2021] == 10000
    assert Output.ranking[Output.TOTAL_ASSETS[1]][2022] == 12000
    
def test_get_best_and_worth() :
    
    set_rankings("Test",range(0,10), [0] * 10)
    assert Output.get_best_and_worth("Test", 3) == [ [0, 1, 2], [9, 8, 7] ]
    assert Output.get_best_and_worth("Test", 3, False) == [ [0, 1, 2], [9, 8, 7] ]
    
    set_rankings("Test",range(0,10), range(0,10))
    
    assert Output.get_best_and_worth("Unknown", 1) == [[],[]]
    
    assert Output.get_best_and_worth("Test", 1) == [[9], [0]]
    assert Output.get_best_and_worth("Test", 2) == [[9, 8], [0, 1]]
    assert Output.get_best_and_worth("Test", 3) == [[9, 8, 7], [0, 1, 2]]
    assert Output.get_best_and_worth("Test", 3, False) == [ [0, 1, 2], [9, 8, 7]]
    
    set_rankings("Test",range(0,10), list(reversed(range(50,55))) + list(reversed(range(100,105))))
    
    assert Output.get_best_and_worth("Test", 3) == [ [5, 6, 7], [4, 3, 2] ]
    
    assert Output.get_best_and_worth("Test", 3, False) == [ [4, 3, 2], [5, 6, 7] ]
    
    
def test_print_best_and_worth():
    set_rankings("Test",range(2000,2010), list(reversed(range(50,55))) + list(reversed(range(100,105))))
    s = Output.best_and_worth_string("Test", 3) 
    print(s)  
        
    
def set_rankings(type : str, years : list, values : list) -> list[int] :
    Output.reset()
    for i in range(len(years)) :
        Output.add_ranking(type, years[i], float(values[i]))
    
