import json

class JSONReader:
    GENERAL_KEY = "General"
    BEFORE_KEY = "Before"
    EARLY_KEY = "Early"
    LEGAL_KEY = "Legal"
    PROPERTY_KEY = "Property"
    CALCULATION_KEY = "Calculation"


    

    def __init__(self, file_path):
        self.file_path = file_path
        self.data = self.read_json()

    def read_json(self):
        with open(self.file_path, 'r') as file:
            return json.load(file)

    def get_general_info(self):
        return self.data.get(JSONReader.GENERAL_KEY, {})

    def get_before_info(self):
        return self.data.get("Before", {})

    def get_early_info(self):
        return self.data.get("Early", {})

    def get_legal_info(self):
        return self.data.get("Legal", {})

    def get_property_info(self):
        return self.data.get("Property", {})

    def get_calculation_info(self):
        return self.data.get("Calculation", {})
    
        def set_value(self, key, value):
        self.data[key] = value

    def get_value(self, key):
        return self.data.get(key, {}

# Example usage:
# reader = JSONReader('path_to_your_json_file.json')
# general_info = reader.get_general_info()
# print(general_info)