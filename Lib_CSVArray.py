import os
import pya
import datetime
import numpy as np
import pandas as pd
from io import StringIO

class CSVArray(pya.PCellDeclarationHelper):
    def __init__(self):
        super(CSVArray, self).__init__()
        self.param("name",        self.TypeString,   "Name",                   default = "")
        self.param("base",        self.TypeLayer,    "Layer for Base",         default = pya.LayerInfo(1, 0))
        self.param("arrow",       self.TypeLayer,    "Layer for Arrow",        default = pya.LayerInfo(1, 0))
        self.param("fmark",       self.TypeLayer,    "Layer for F-mark",       default = pya.LayerInfo(1, 0))
        self.param("text",        self.TypeLayer,    "Layer for info text",    default = pya.LayerInfo(1, 0))
        self.param("f_folder",    self.TypeString,   "CSV folder path",        default =  r"C:\Users\User\KLayout\pymacros\Library\ArrayMagic\Examples")
        self.param("f_name",      self.TypeString,   "CSV file name",          default =  r"csvArray.csv")
        self.param("call_load",   self.TypeCallback, "Load CSV")
        self.param("call_clear",  self.TypeCallback, "Clear Data")
        self.param("status",      self.TypeString,   "Status",                 default =  "",  readonly=True )
        self.param("error",       self.TypeString,   "Error",                  default =  "",  readonly=True )
        self.param("source" ,     self.TypeString,   "Source",                 default =  "", )# hidden = True )
        self.param("save1",       self.TypeString,   "Saved data 0001-0500",   default =  "", )# hidden = True )
        self.param("save2",       self.TypeString,   "Saved data 0500-1000",   default =  "", )# hidden = True )
        self.param("save3",       self.TypeString,   "Saved data 1000-1500",   default =  "", )# hidden = True )
        self.param("save4",       self.TypeString,   "Saved data 1500-2000",   default =  "", )# hidden = True )
        self.init_setup()

        
    def init_setup(self):
        self.trigger_load_csv = False
        self.trigger_clear    = False
        self.validator   = {
            "x"      : {"required" :  True, "dtype" : "float32",  "low" : -1E6, "high" :  1E6, "default" :    0}, 
            "y"      : {"required" :  True, "dtype" : "float32",  "low" : -1E6, "high" :  1E6, "default" :    0}, 
            "width"  : {"required" :  True, "dtype" : "float32",  "low" :    0, "high" :  1E6, "default" :    0}, 
            "height" : {"required" :  True, "dtype" : "float32",  "low" :    0, "high" :  1E6, "default" :    0}, 
            "rotate" : {"required" : False, "dtype" : "float32",  "low" : -1E6, "high" :  1E6, "default" :    0}, 
            "mirror" : {"required" : False, "dtype" :    "bool",  "low" : None, "high" : None, "default" :False}, 
            "hide"   : {"required" : False, "dtype" :    "bool",  "low" : None, "high" : None, "default" :False}, 
            #"label"  : {"required" : False, "dtype" :  "string",  "low" : None, "high" : None, "default" :   ""}, 
        }
        self.header_list  = list(self.validator.keys())
        self.dtype_table  = {self.validator[header]["dtype"] for header in self.validator}
        self.bool_table   = {"TRUE" : True, "FALSE" : False, "1" : True, "0" : False}   

    def display_text_impl(self):
        class_name  = self.__class__.__name__
        custom_name = (self.name + "__" if self.name else "") 
        disp_str    = f"{self.source}"

        return "%s%s%s" % (custom_name, class_name, disp_str)

    def can_create_from_shape_impl(self):
        return self.shape.is_box() or self.shape.is_polygon() or self.shape.is_path()
    
    def parameters_from_shape_impl(self):
        pass
    
    def transformation_from_shape_impl(self):
        return pya.Trans(self.shape.bbox().center())

    def check_data_status(self):
        if self.source == "":
            self.status = "No data, Wait File input"
        else :
            self.status = f"Current data : {self.source}"
            
    def check_path(self):
            
        if "" in [self.f_folder, self.f_name]:
            self.error  = "[Load file] Please specify csv file path"
            return None

        if not(os.path.isdir(self.f_folder)):
            self.error = "[Load file] Folder path not exist"
            return None

        f_path = os.path.join(self.f_folder, self.f_name)
        if not(os.path.isfile(f_path)):
            self.error = "[Load file] File path not exist"
            return None

        return f_path
        
    def callback_impl(self, name):
        if name == "call_load":
            self.trigger_load_csv = True
            print("trigger load csv from disk")
            
        elif name == "call_clear":
            self.trigger_clear = True
            print("trigger remove data")
            
    def coerce_parameters_impl(self):  
         
        
        print("Pcell Reset")
        
        if self.trigger_clear:
            self.save1      = ""
            self.save2      = ""
            self.save3      = ""
            self.save4      = ""
            self.trigger_clear = False
         
        if self.trigger_load_csv:
            df, self.source = self.load_from_disk()
            chunk_df_str    = self.chop_data(df, chunk_size = 500, chunk_max = 2000)
            self.save1      = chunk_df_str[0]
            self.save2      = chunk_df_str[1]
            self.save3      = chunk_df_str[2]
            self.save4      = chunk_df_str[3]
            self.trigger_load_csv = False
            self.check_data_status()
            print(f"fetched {len(df)}  data from disk", self.source)
            print("SAVE1", self.save1)
            print("SAVE2", self.save2)
            print("SAVE3", self.save3)
            print("SAVE4", self.save4)
            
        self.check_data_status()
        
        print("start Redraw\n\n")
        
    def load_from_disk(self):
        f_path     = self.check_path()
        df         = self.open_csv(f_path)
        date_str   = datetime.datetime.now().strftime("%Y%m%d - %H:%M:%S")
        return (None, "") if (df is None) else (df, f"{date_str} {f_path}")
   
       
    def open_csv(self, f_path):
        if f_path is None : return None
        
        df = pd.read_csv(f_path)
        df = df.filter(items = self.header_list)
        df, warning, error = self.process_raw_csv(df)
        print("open_csv", warning)
        print("open_csv", error)
        return df
    
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
        
    def chop_data(self, df, chunk_size, chunk_max):
        chunk_count  = int(chunk_max/chunk_size)
        chunk_df_str = { i : "" for i in range(chunk_count)}
        chunk_max    = min(chunk_max, len(df))
        
        for i in range(chunk_count):
            chunk_df_str[i] = df.loc[i * chunk_size : (i+1) * chunk_size - 1:] .to_csv(index=False)
            
        return chunk_df_str
        
    def load_db_from_save_slot(self, save_slot):
        
        if save_slot == "" : 
            print(f"save slot : empty")
            return None
        
        csv_string = save_slot
        
        try:
            df = pd.read_csv(StringIO(csv_string))
            print(f"load from save slot : {len(df)}")
            return df
            
        except Exception as e:
            print("load_db_from_save_slot", e)
            return None
        
    def pcell_lbph(self, x, y, base_w, base_h, angle, mirror):
        x, y, base_w, base_h, angle = float(x), float(y), float(base_w), float(base_h), float(angle)
        
        unit       = self.layout.dbu
        um         = 1 / unit
        lib        = pya.Library.library_by_name("ArrayMagic")
        pcell_decl = lib.layout().pcell_declaration("PlaceHolder")
        param      = ["", self.base, self.arrow, self.fmark, base_w, base_h]
        pcell_var  = self.layout.add_pcell_variant(lib, pcell_decl.id(), param) 
        return pya.CellInstArray(pcell_var, pya.DCplxTrans (1.0, angle, mirror, x * um, y * um), pya.Vector(0, 0), pya.Vector(0, 0), 0, 0)
        
    def df_to_pcell(self, df):
        if df is None : return None

        for i in range(df.shape[0]):
            row_data = df.iloc[i]
            if row_data["hide"] : continue
            self.cell.insert(self.pcell_lbph(row_data["x"], row_data["y"], row_data["width"], row_data["height"], row_data["rotate"], row_data["mirror"]))
            
    def produce_impl(self): 
        is_empty = True
        for save_slot in [self.save1, self.save2, self.save3, self.save4]:
            df = self.load_db_from_save_slot(save_slot)
            if not(df is None):
                is_empty = False
                self.df_to_pcell(df)
            

        if is_empty:
            self.cell.shapes(self.text_layer).insert(pya.DBox(100, 100))
            self.cell.shapes(self.text_layer).insert(pya.DText("CSV_ARRAY : No DATA Loaded, wait File Input", 0, 0))
            return
        

