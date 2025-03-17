
class Output :
    
    NEVER = 1000
    
    SCENARIO_NAME = [0,"Scenario:"]
    DESCRIPTION = [1,"Description:"]
 
 
    EARLY_RETIREMENT_AGE = [1,"Early Retirement:"]
    PK_LUMPSUM_RATIO = [2,"Lumpsum Ratio:"]
    
    AVERAGE_PERFORMANCE = [10 ,"Average Performance:"]
    AVERAGE_INFLATION = [11 ,"Average Inflation:"]
   
    WITHDRAWAL_RATE = [13,"Withdrawal Rate:"]
    
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
    WEALTH = [55,"Wealth"]
        
    output = {}
    scenario = 1
    columns = 2
    
    ranking = {}
    
    @staticmethod
    def reset() :
        Output.output = {}
        Output.ranking = {}
        
        Output.scenario = 1
        Output.columns = 2
    
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
            
    @staticmethod
    def get_name() :
        return Output.output[Output.SCENARIO_NAME[1]][Output.scenario]
    
    @staticmethod
    def add_inflation(year : int, inflation : float) :
        Output.__add_ranking(Output.AVERAGE_INFLATION[1], year, inflation*100)


    @staticmethod
    def add_performance(year : int, performance : float) :
          Output.__add_ranking(Output.AVERAGE_PERFORMANCE[1], year, performance*100)
        
    @staticmethod
    def add_sell(year : int, name: str, age : float) :
        Output.__add_ranking(f"{Output.SELL_PROPERTY[1]} {name}", year, age) 
        
    @staticmethod
    def add_wealth(year : int, wealth : float) :
          Output.__add_ranking(Output.WEALTH[1], year, wealth)
    
    @staticmethod
    def add_property_name(name: str, property_name: str) :
        Output.property_names[name] = property_name
        
    @staticmethod
    def __add_ranking(type : str, year: int, value : any) :
        if Output.ranking.get(type) is None :
            Output.ranking[type] = {}
        Output.ranking[type][year] = value
        
    @staticmethod
    def print_ranking() :
        for key in Output.ranking.keys() :
            if key == Output.AVERAGE_INFLATION[1] :
                Output.__print_best_and_worth(key,dict(sorted(Output.ranking[key].items(), key=lambda item: item[1], reverse=False)))
            else :
                Output.__print_best_and_worth(key,dict(sorted(Output.ranking[key].items(), key=lambda item: item[1], reverse=True)))
            
        
            
    @staticmethod
    def __print_best_and_worth(type: str, sorted_dict: dict) :
        keys = list(sorted_dict.keys()) 
        length = len(keys)           
        if length < 6 :
            print("Not enough simulations to present a  ranking") 
            return
        worst = [-1, -2, -3]
        best = [0,1,2]

        s = f"{type :<20s}:  Worst years ("
        for i in worst :
            s +=  str(keys[length + i])+":"
            value = sorted_dict[keys[length + i]]
            if (value == Output.NEVER) :
                s += f"{'---':>12s}, "
            else :
                s += f"{value:12,.2f}, "
                
        s += ") Best years ("
        for i in best :
            s +=  str(keys[i])+":"
            value = sorted_dict[keys[i]]            
            if (value == Output.NEVER) :
                s += f"{'---':>12s}, "
            else :
                s += f"{value:12,.2f}, "
                
        s += ")"
                 
        print(s)
            

       

    