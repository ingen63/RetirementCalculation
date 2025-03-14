
class Output :
    
    SCENARIO_NAME = [0,"Scenario:"]
    DESCRIPTION = [1,"Description:"]
 
 
    EARLY_RETIREMENT_AGE = [1,"Early Retirement:"]
    PK_LUMPSUM_RATIO = [2,"Lumpsum Ratio:"]
    
    INTEREST_RATE = [10, "Interest Rate:"]
    INFLATION_RATE = [11 ,"Inflation Rate:"]
    WITHDRAWAL_RATE = [12,"Withdrawal Rate:"]
    
    PENSION = [15,"Pension:", "CHF"]
    SPENDING = [16,"Spending", "CHF"]
    
    SELL_PROPERTY = [20,"Sell:"]
    BUY_PROPERTY = [20,"Buy:"]

    
    TIME_TO_GO = [30,"Time to go:"]
    REMAINING_WEALTH = [31,"Remaining Wealth:"]
    
    START_AGE = [50,"Simulation Start:"]
    LEGAL_RETIREMENT_AGE = [51,"Legal Retirement:"]
    PK_CAPITAL = [52,"Pension Capital:"]
    WEALTH_EARLY = [53,"Wealth (Early)"]
    WEALTH_LEGAL = [54,"Wealth (Legal)"]
        
    output = {}
    scenario = 1
    columns = 2
    
    
    @staticmethod
    def next_scenario() :
        Output.scenario += 1
        
    @staticmethod   
    def set_scenarios(num : int) :
        Output.columns = num+1
        
    @staticmethod    
    def add_result(type : list, value : str, key : str = None ) :
        if key is None :
            key = type[1] 
        if key not in Output.output : 
            Output.output[key] = ["" for i in range(Output.columns)]
            Output.output[key][0] = type
        Output.output[key][Output.scenario] = value
 
    @staticmethod
    def print() :
        
        sorted_output = dict(sorted(Output.output.items(), key=lambda item: item[1][0][0]))
        for key in sorted_output.keys():
            print(f"{key :<25s}", end=",")
            for i in range(1, Output.columns) :
                print(f"{sorted_output[key][i] :>28s}", end=",")
            print()
            
            
       

    