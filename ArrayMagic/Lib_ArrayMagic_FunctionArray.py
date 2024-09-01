import re
import pya
import math
import numbers
from asteval import Interpreter


class FunctionArray(pya.PCellDeclarationHelper):
    def __init__(self):
        super(FunctionArray, self).__init__()
        self.param("name",   self.TypeString, "Name",                   default = "")
        self.param("base",   self.TypeLayer,  "Layer for Base",         default = pya.LayerInfo(1, 0))
        self.param("arrow",  self.TypeLayer,  "Layer for Arrow",        default = pya.LayerInfo(1, 0))
        self.param("fmark",  self.TypeLayer,  "Layer for F-mark",       default = pya.LayerInfo(1, 0))
        self.param("text",   self.TypeLayer,  "Layer for info text",    default = pya.LayerInfo(1, 0))
        self.param("base_w", self.TypeDouble, "Width",                  default =  20, unit = "um",              tooltip = "parameter: WIDTH")
        self.param("base_h", self.TypeDouble, "Height",                 default =  10, unit = "um",              tooltip = "parameter: HEIGHT")
        self.param("row",    self.TypeInt,    "Row counts",             default =   5,                           tooltip = "parameter: ROWS")
        self.param("col",    self.TypeInt,    "Column counts",          default =   5,                           tooltip = "parameter: COLS")
        self.param("x_fun",  self.TypeString, "X position Function",    default =  "COL * 20 + (COL ** 2 ) * 5", tooltip = "parameter: Xpos")
        self.param("y_fun",  self.TypeString, "Y position Function",    default =  "ROW * 20 + (ROW ** 2 ) * 5", tooltip = "parameter: Ypos")
        self.param("r_fun",  self.TypeString, "Rotation   Function",    default =  "(COL + Row) * 10",           tooltip = "parameter: ROT")
        self.param("m_fun",  self.TypeString, "Mirror     Function",    default =  "ROW % 2 == 0",               tooltip = "parameter: MIR")
        self.param("v_fun",  self.TypeString, "Visibility Function",    default =  "")
        self.param("l_fun",  self.TypeString, "Element Label Function", default =  "")
        
    def display_text_impl(self):
        class_name  = self.__class__.__name__
        custom_name = (self.name + "__" if self.name else "") 
        disp_str    = "_%.2fx%.2f; R:%d, C:%d" % (self.base_w, self.base_h, self.row, self.col)

        return "%s%s%s" % (custom_name, class_name, disp_str)
    
    def coerce_parameters_impl(self):          
        unit            = self.layout.dbu
        min_size        =  2 * unit
        min_arrow_size  = 64 * unit
        min_fmark_size  = 64 * unit
        self.base_w     = min_size if self.base_w <= min_size else self.base_w
        self.base_h     = min_size if self.base_h <= min_size else self.base_h
        self.show_arrow = min_arrow_size > min(self.base_w, self.base_h)
        self.show_fmark = min_fmark_size > min(self.base_w, self.base_h)
        
        self.row        = self.row if (self.row > 0) else 1
        self.col        = self.col if (self.col > 0) else 1
        
        self.x_fun      = self.pre_process_str(self.x_fun, ignore = "xyrm")
        self.y_fun      = self.pre_process_str(self.y_fun, ignore = "yrm")
        self.r_fun      = self.pre_process_str(self.r_fun, ignore = "rm")
        self.m_fun      = self.pre_process_str(self.m_fun, ignore = "m")
        self.v_fun      = self.pre_process_str(self.v_fun, ignore = "")
        self.l_fun      = self.pre_process_str(self.l_fun, ignore = "")
        
    def pre_process_str(self, fun_str, ignore = ""):
        fun_str = re.sub(r'\s+', ' ', fun_str)
        
        kwards = {
            "width"  : "WIDTH", 
            "height" : "HEIGHT", 
            "rows"   : "ROWS", 
            "row"    : "ROW", 
            "cols"   : "COLS", 
            "col"    : "COL", 
            "xpos"   : "" if ("x" in ignore) else "Xpos", 
            "ypos"   : "" if ("y" in ignore) else "Ypos", 
            "rot"    : "" if ("r" in ignore) else "ROT", 
            "mir"    : "" if ("m" in ignore) else "MIR", 
            "pya."   : "",
            "math."  : "",

        }
        for k in kwards:
            fun_str = re.sub(rf'({k})', kwards[k], fun_str, flags=re.IGNORECASE)
            
        return fun_str.strip()
  
        
    def can_create_from_shape_impl(self):
        return self.shape.is_box() or self.shape.is_polygon() or self.shape.is_path()
    
    def parameters_from_shape_impl(self):
        pass
    
    def transformation_from_shape_impl(self):
        return pya.Trans(self.shape.bbox().center())
        
    def pcell_lbph(self, x, y, angle, mirror, label_txt):
        unit       = self.layout.dbu
        um         = 1 / unit
        lib        = pya.Library.library_by_name("ArrayMagic")
        pcell_decl = lib.layout().pcell_declaration("LabeledPlaceHolder")
        param      = ["", self.base, self.arrow, self.fmark, self.text, self.base_w, self.base_h, label_txt]
        pcell_var  = self.layout.add_pcell_variant(lib, pcell_decl.id(), param) 
        return pya.CellInstArray(pcell_var, pya.DCplxTrans (1.0, angle, mirror, x * um, y * um), pya.Vector(0, 0), pya.Vector(0, 0), 0, 0)
        
        
    def post_process_str(self, aeval, width, height, rows, cols, row, col, x = 0, y=0, r=0, m=False):
        aeval.symtable["WIDTH" ] = width
        aeval.symtable["HEIGHT"] = height
        aeval.symtable["ROWS"  ] = rows
        aeval.symtable["ROW"   ] = row
        aeval.symtable["COLS"  ] = cols
        aeval.symtable["COL"   ] = col
        aeval.symtable["Xpos"  ] = x
        aeval.symtable["Ypos"  ] = y
        aeval.symtable["ROT"   ] = r
        aeval.symtable["MIR"   ] = m
         
    def eval_string(self, variable, default_value, aeval, variable_code, error_stat):
        check_type = numbers.Number if type(default_value) in [int, float] else type(default_value)

        if (variable is None):
            eval_value = aeval(variable_code)
            variable   = eval_value if isinstance(eval_value, check_type ) else default_value

            if len(aeval.error) > 0:
                variable = default_value
                error_stat = variable_code if not(error_stat) else error_stat

        return variable, error_stat
        
    def produce_impl(self): 
        counts   = 0
        rows     = self.row
        cols     = self.col
        aeval    = Interpreter()
        init_x   =     0 if (self.x_fun == "") else None
        init_y   =     0 if (self.y_fun == "") else None
        init_r   =     0 if (self.r_fun == "") else None
        init_m   = False if (self.m_fun == "") else None
        init_v   = True  if (self.v_fun == "") else None
        init_l   =    "" if (self.l_fun == "") else None
        errors   = {"x_error" : "", "y_error" : "", "r_error" : "", "m_error" : "", "v_error" : "", "l_error" : ""}

        for row in range(self.row):
            for col in range(self.col):
                x, y, r, m, v, l = init_x, init_y, init_r, init_m, init_v, init_l
                
                self.post_process_str(aeval, self.base_w, self.base_h, self.row, self.col, row, col, x, y, r, m)
                x, errors["x_error"] = self.eval_string(x,   0.0, aeval, self.x_fun, errors["x_error"])
                
                self.post_process_str(aeval, self.base_w, self.base_h, self.row, self.col, row, col, x, y, r, m)
                y, errors["y_error"] = self.eval_string(y,   0.0, aeval, self.y_fun, errors["y_error"])
                
                self.post_process_str(aeval, self.base_w, self.base_h, self.row, self.col, row, col, x, y, r, m)
                r, errors["r_error"] = self.eval_string(r,   0.0, aeval, self.r_fun, errors["r_error"])
                
                self.post_process_str(aeval, self.base_w, self.base_h, self.row, self.col, row, col, x, y, r, m)
                m, errors["m_error"] = self.eval_string(m, False, aeval, self.m_fun, errors["m_error"])
                
                self.post_process_str(aeval, self.base_w, self.base_h, self.row, self.col, row, col, x, y, r, m)
                v, errors["v_error"] = self.eval_string(v,  True, aeval, self.v_fun, errors["v_error"])
                
                self.post_process_str(aeval, self.base_w, self.base_h, self.row, self.col, row, col, x, y, r, m)
                l, errors["l_error"] = self.eval_string(l,    "", aeval, self.l_fun, errors["l_error"])
                
                
                if v : 
                    self.cell.insert(self.pcell_lbph( x, y , r, m, l))
                    counts = counts + 1
        
        
        info = "\n".join([
            f"ArrayMagic", 
            f"item  counts: {counts}",
            f"Xpos  error : {errors['x_error']}" if errors["x_error"] else "",
            f"Ypos  error : {errors['y_error']}" if errors["y_error"] else "",
            f"ROT   error : {errors['r_error']}" if errors["r_error"] else "",
            f"MIR   error : {errors['m_error']}" if errors["m_error"] else "",
            f"VIS   error : {errors['v_error']}" if errors["v_error"] else "",
            f"Label error : {errors['l_error']}" if errors["l_error"] else "",
        ])
        
        self.cell.shapes(self.text_layer).insert(pya.DText(info, 0.0, 0.0))
        if counts == 0:
            self.cell.shapes(self.text_layer).insert(pya.DBox(10, 10))


