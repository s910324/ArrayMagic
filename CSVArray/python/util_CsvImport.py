import os
import pya
import datetime
import numpy as np
import pandas as pd
import logging

log = logging.getLogger('CsvImport')
log.setLevel(logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)

class CsvImport(object):
    def __init__(self):
        super(CsvImport, self).__init__()
        self.init_setup()
        
    def init_setup(self):
        self.layout         = None
        self.cell           = None
        self.df             = None
        self.placement_type = None
        self.validator      = {}
        self.header_list    = []
        self.warning        = ""
        self.error          = ""

        self.pcell_text_validator   = { 
            "text"     : {"required" :  True, "dtype" :  "string",  "low" : None, "high" : None, "default" :   ""}, 
            "layer"    : {"required" :  True, "dtype" :   "int32",  "low" :    0, "high" :  1e4, "default" :    0},  
            "datatype" : {"required" :  True, "dtype" :   "int32",  "low" :    0, "high" :  1E4, "default" :    0},  
            "mag"      : {"required" : False, "dtype" : "float32",  "low" :    0, "high" :  1E6, "default" :    1}, 
            "inverse"  : {"required" : False, "dtype" :    "bool",  "low" : None, "high" :  1E6, "default" :False}, 
            "bias"     : {"required" : False, "dtype" : "float32",  "low" :    0, "high" :  1E6, "default" :    0}, 
            "cspacing" : {"required" : False, "dtype" : "float32",  "low" :    0, "high" :  1E6, "default" :    0}, 
            "lspacing" : {"required" : False, "dtype" : "float32",  "low" :    0, "high" :  1E6, "default" :    0}, 
            "x"        : {"required" :  True, "dtype" : "float32",  "low" : -1E6, "high" :  1E6, "default" :    0}, 
            "y"        : {"required" :  True, "dtype" : "float32",  "low" : -1E6, "high" :  1E6, "default" :    0}, 
            "rotate"   : {"required" : False, "dtype" : "float32",  "low" : -1E6, "high" :  1E6, "default" :    0}, 
            "mirror"   : {"required" : False, "dtype" :    "bool",  "low" : None, "high" : None, "default" :False},  
        }
        
        self.pcell_shape_validator   = {
            "shape"    : {"required" : False, "dtype" :  "string",  "low" : None, "high" : None, "default" :"Rect"}, 
            "layer"    : {"required" : False, "dtype" :   "int32",  "low" :    0, "high" :  1e4, "default" :     0},  
            "datatype" : {"required" : False, "dtype" :   "int32",  "low" :    0, "high" :  1E4, "default" :     0},  
            "x"        : {"required" : False, "dtype" : "float32",  "low" : -1E6, "high" :  1E6, "default" :     0}, 
            "y"        : {"required" : False, "dtype" : "float32",  "low" : -1E6, "high" :  1E6, "default" :     0}, 
            "width"    : {"required" : False, "dtype" : "float32",  "low" :    0, "high" :  1E6, "default" :     0}, 
            "height"   : {"required" : False, "dtype" : "float32",  "low" :    0, "high" :  1E6, "default" :     0}, 
            "rotate"   : {"required" : False, "dtype" : "float32",  "low" : -1E6, "high" :  1E6, "default" :     0}, 
            "mirror"   : {"required" : False, "dtype" :    "bool",  "low" : None, "high" : None, "default" : False},  
        }
        
        self.cell_validator   = {
            "x"        : {"required" :  True, "dtype" : "float32",  "low" : -1E6, "high" :  1E6, "default" :    0}, 
            "y"        : {"required" :  True, "dtype" : "float32",  "low" : -1E6, "high" :  1E6, "default" :    0}, 
            "rotate"   : {"required" : False, "dtype" : "float32",  "low" : -1E6, "high" :  1E6, "default" :    0}, 
            "mirror"   : {"required" : False, "dtype" :    "bool",  "low" : None, "high" : None, "default" :False},  
        }     
        
        self.text_validator   = {
            "text"     : {"required" :  True, "dtype" :  "string",  "low" : None, "high" : None, "default" :   ""}, 
            "layer"    : {"required" : False, "dtype" :   "int32",  "low" :    0, "high" :  1e4, "default" :    0},  
            "datatype" : {"required" : False, "dtype" :   "int32",  "low" :    0, "high" :  1E4, "default" :    0},  
            "x"        : {"required" :  True, "dtype" : "float32",  "low" : -1E6, "high" :  1E6, "default" :    0}, 
            "y"        : {"required" :  True, "dtype" : "float32",  "low" : -1E6, "high" :  1E6, "default" :    0}, 
        }   
          
        self.validators   = {
            "pcell_shape" : self.pcell_text_validator,
            "pcell_text"  : self.pcell_shape_validator,
            "cell"        : self.cell_validator,
            "text"        : self.text_validator,
        }

        self.bool_table   = {"TRUE" : True, "FALSE" : False, "1" : True, "0" : False} 
    
    def setValidator(self, f_path):  
        fname = os.path.basename(f_path).lower()
        self.placement_type = None
        print("OK")
        for placement_type in self.validators.keys():
            if fname.startswith(placement_type):
                self.placement_type = placement_type
                self.validator = self.validators[placement_type]
                self.header_list = list(self.validator.keys())
                log.debug(f"validator set to : {placement_type}")
                break
        else:
            log.debug(f"file_name does not contain validator string")
            self.validator = {}
        
            
    def open_csv(self, f_path):
        
        
        if f_path is None : return None, None, None
        
        log.debug(f"Path Loaded : {f_path}")
        
        self.setValidator(f_path)
        df = pd.read_csv(f_path)
        df = df.filter(items = self.header_list)
        log.debug(f"CSV Load to dataframe")
        self.df, self.warning, self.error = self.process_raw_csv(df)
        log.debug(f"dataframe value coerce")
    
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
        
        log.debug(f"warning {warning_msgs}")
        log.debug(f"error {error_msgs}")
        return df, ",".join(warning_msgs), ",".join(error_msgs)



if __name__ == "__main__": 
    path = r"C:\Users\User\My Drive\Porotech\Project M\Delorean\MTK\text_MTK_Bump_location_20240906 - Copy.csv"
    i    = CsvImport()
    i.open_csv(path)

    print(i.df)

     

