
import logging


class Output :
    
    NEVER = -1
    
    SCENARIO_NAME = [-11,"Scenario:"]
    DESCRIPTION = [-12,"Description:"]
 
 
    EARLY_RETIREMENT_AGE = [1,"Early Retirement:"]
    PK_LUMPSUM_RATIO = [2,"Lumpsum Ratio:"]
    HISTORICAL_YEAR = [5,"Historical Year"]
    
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
    TOTAL_ASSETS = [56,"Total Assets"]
    
    SCENARIO_IDS = [-1,"Scenario Identifiers"]
        
    output = {}
    scenario = 1
 
    ranking = {}
    
    @staticmethod
    def reset() :
        Output.output = {}
        Output.ranking = {}

        Output.scenario = 1
    
    @staticmethod
    def next_scenario() : 
        Output.scenario += 1
        for key in Output.output.keys() :
            Output.output[key].append("")
          
    @staticmethod    
    def add_result(type : list, value : str, key : str = None ) :
        if key is None :
            key = type[1] 
        if value is None or not isinstance(value,str) :
            raise TypeError(f"Value {value} must be of type str")
        if key not in Output.output : 
            Output.output[key] = ["" for i in range(Output.scenario+1)]
            Output.output[key][0] = type
        Output.output[key][Output.scenario] = value
 
    @staticmethod
    def print(index :list) : 
        if len(index) == 0 :
            return
        
        sorted_output = dict(sorted(Output.output.items(), key=lambda item: item[1][0][0]))
        for key in sorted_output.keys():
            if (sorted_output[key][0][0] > 0) :
                print(f"{key :<25s}", end=",")
                for i in index:
                    print(f"{sorted_output[key][i] :>28s}", end=",")
                print()
            
            
            
    @staticmethod
    def get_name() :
        if Output.output.get(Output.SCENARIO_NAME[1]) is None:
            Output.add_result(Output.SCENARIO_NAME,"No scenario selected")
        
        return Output.output[Output.SCENARIO_NAME[1]][Output.scenario]
    
    @staticmethod
    def get_scenario_id() :
        key = Output.SCENARIO_IDS[1]
        return Output.output[key][Output.scenario] if Output.output.get(key) is not None else f"Scenario {Output.scenario}"
    
    @staticmethod
    def add_inflation_ranking(inflation : float, scenario_id : str = None) :
        Output.add_ranking(Output.AVERAGE_INFLATION, scenario_id,  inflation*100)


    @staticmethod
    def add_performance_ranking(performance : float, scenario_id : str = None) :
        Output.add_ranking(Output.AVERAGE_PERFORMANCE, scenario_id, performance*100)
        
    @staticmethod
    def add_sell_ranking(name: str, age : float, scenario_id : str = None) :
        Output.add_ranking(Output.SELL_PROPERTY, scenario_id, age, name) 
        
    @staticmethod
    def add_wealth_ranking(wealth : float, scenario_id : str = None) :
        Output.add_ranking(Output.WEALTH, scenario_id, wealth)
    
    @staticmethod
    def add_total_assests_ranking(total_asset : float, scenario_id : str = None) :
        Output.add_ranking(Output.TOTAL_ASSETS, scenario_id, total_asset)
        
    @staticmethod
    def add_ranking(type : list, scenario_id : str, value : float, name : str = None) :
        if (scenario_id is None) :
            scenario_id = Output.get_scenario_id()
        
        if value is None or not (isinstance(value,float) or isinstance(value,int) ) :
            raise TypeError(f"Value {value} must be of type float")
        
        key = type[1] if (name is None) else f"{type[1]} {name}"
        if Output.ranking.get(key) is None :
            Output.ranking[key] = {}
        Output.ranking[key][Output.scenario] = value
        
    @staticmethod
    def print_ranking() :
        for key in Output.ranking.keys() :
            if key == Output.AVERAGE_INFLATION[1] :
                s = Output.best_and_worth_string(key,3,False)
            else :
                s = Output.best_and_worth_string(key,3,True)
            if s is not None :
                print(s)
    
    @staticmethod       
    def get_best_and_worth(type : str = None, places : int = 1, order_reverse : bool = True):
        if type is None :
            type =  Output.TOTAL_ASSETS
        
        if Output.ranking.get(type) is None :
            logging.debug(f"No ranking for type {type} available.") 
            return [[],[]]
        
        scenarios = list(dict(sorted(Output.ranking[type].items(), key=lambda item: item[1], reverse=order_reverse)).keys())
         
        if len(scenarios) < 2*places :       
            logging.debug(f"Not enough data for type {type} available, to present the best and worst {places} values.") 
            if places == 1 :
                return [[],[]]
            return Output.get_best_and_worth(type,places-1, order_reverse)

        best = []
        worst = []
        for i in reversed(range(len(scenarios)-places, len(scenarios))): 
            worst.append(scenarios[i])
        for i in range(places) :
            best.append(scenarios[i])
        return [best, worst] 
           
    @staticmethod    
    def best_and_worth_string(type : str, places : int = 3, order_reverse : bool = True) -> str : 
        
        rankings = Output.ranking.get(type)
        if rankings is None :
            logging.debug(f"No ranking for type {type} available.") 
            return ""
                
        [best,worst] = Output.get_best_and_worth(type, places, order_reverse)
        if len(best) == 0 or len(worst) == 0 :
            return None
        
        s = f"{type :<20s}:  Worst scenario ("
        for key in worst :
            s += Output.__ranking_key_value(key, rankings[key])
                
        s += ") Best scenario ("
        for key in best :
            s += Output.__ranking_key_value(key, rankings[key])  
        
        s += ")"
        return s
        
    def __ranking_key_value(key: str, value: float) -> str :
        scenario = Output.output[Output.SCENARIO_IDS[1]][key]
        s =  str(scenario)+":"
        if (value == Output.NEVER) :
            s += f"{'---':>12s}, "
        else :
            s += f"{value:12,.2f}, "
        return s
    
            

       

    