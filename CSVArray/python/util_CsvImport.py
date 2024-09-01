import os
import pya
import datetime
import numpy as np
import pandas as pd

class CsvImport(object):
    def __init__(self):
        super(CsvImport, self).__init__()
        self.init_setup()
        
    def init_setup(self):
        self.layout  = None
        self.cell    = None
        self.df      = None
        self.warning = ""
        self.error   = ""
        self.validator   = {
#            "cell"     : {"required" : False, "dtype" :  "string",  "low" : None, "high" : None, "default" :   ""},  
#            "shape"    : {"required" : False, "dtype" :  "string",  "low" : None, "high" : None, "default" :   ""},  
#            "label"    : {"required" : False, "dtype" :  "string",  "low" : None, "high" : None, "default" :   ""}, 
            
#            "layer"    : {"required" : False, "dtype" :   "int32",  "low" :    0, "high" :  1e4, "default" :    0},  
#            "datatype" : {"required" : False, "dtype" :   "int32",  "low" :    0, "high" :  1E4, "default" :    0},  
            
            "x"        : {"required" :  True, "dtype" : "float32",  "low" : -1E6, "high" :  1E6, "default" :    0}, 
            "y"        : {"required" :  True, "dtype" : "float32",  "low" : -1E6, "high" :  1E6, "default" :    0}, 
            "width"    : {"required" : False, "dtype" : "float32",  "low" :    0, "high" :  1E6, "default" :    0}, 
            "height"   : {"required" : False, "dtype" : "float32",  "low" :    0, "high" :  1E6, "default" :    0}, 
            "rotate"   : {"required" : False, "dtype" : "float32",  "low" : -1E6, "high" :  1E6, "default" :    0}, 
            "mirror"   : {"required" : False, "dtype" :    "bool",  "low" : None, "high" : None, "default" :False},  
        }
        self.header_list  = list(self.validator.keys())
        self.dtype_table  = {self.validator[header]["dtype"] for header in self.validator}
        self.bool_table   = {"TRUE" : True, "FALSE" : False, "1" : True, "0" : False}   
       
    def open_csv(self, f_path):
        if f_path is None : return None
        df = pd.read_csv(f_path)
        df = df.filter(items = self.header_list)
        self.df, self.warning, self.error = self.process_raw_csv(df)
    
    def process_raw_csv(self, df):
        error_msgs   = []     
        warning_msgs = []
        for header in self.validator:
            try:
                column  = df[header]
                dtype   = self.validator[header]["dtype"]
                default = self.validator[header]["default"]
                low     = self.validator[header]["low"]
                high    = self.validator[header]["high"]
                 
                if dtype in ["float32", "int32"]:
                    column = pd.to_numeric(column, errors='coerce')
                    column = column.replace(np.nan, default, regex=True)
                    column.clip(low, high)
                    if dtype == "int32":
                        column = column.astype("int32")
        
                elif dtype == "bool":           
                    column = column.astype("string").str.upper().apply(lambda x: self.bool_table.get(x, default))
        
                else:
                    column = column.astype("string")
                df[header] = column
                
            except KeyError as e:
                required    = self.validator[header]["required"]        
                default     = self.validator[header]["default"]
                df[header]  = default
                (error_msgs if required else warning_msgs).append(f"field : {header} not exist")
                
            except Exception as e:
                required    = self.validator[header]["required"]        
                default     = self.validator[header]["default"]
                df[header]  = default
                (error_msgs if required else warning_msgs).append(f"field : {header}, error : {e}")
                
        return df, ",".join(warning_msgs), ",".join(error_msgs)



if __name__ == "__main__": 
    p  = CsvImport()

     

