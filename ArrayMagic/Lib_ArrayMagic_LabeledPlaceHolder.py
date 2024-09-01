import pya
class LabeledPlaceHolder(pya.PCellDeclarationHelper):
    def __init__(self):
        super(LabeledPlaceHolder, self).__init__()
        self.param("name",      self.TypeString,  "Name",             default = "")
        self.param("base",      self.TypeLayer,   "Layer for Base",   default = pya.LayerInfo(1, 0))
        self.param("arrow",     self.TypeLayer,   "Layer for Arrow",  default = pya.LayerInfo(1, 0))
        self.param("fmark",     self.TypeLayer,   "Layer for F-mark", default = pya.LayerInfo(1, 0))
        self.param("text",      self.TypeLayer,   "Layer for text",   default = pya.LayerInfo(1, 0))
        
        self.param("base_w",    self.TypeDouble,  "Width",            default =  20, unit = "um")
        self.param("base_h",    self.TypeDouble,  "Height",           default =  10, unit = "um")
        self.param("text_str",  self.TypeString,  "Label text",       default =  "")
        
    def display_text_impl(self):
        class_name  = self.__class__.__name__
        custom_name = (self.name + "__" if self.name else "") 
        disp_str    = "_%.2fx%.2f" % (self.base_w, self.base_h)

        return "%s%s%s" % (custom_name, class_name, disp_str)
    
    def coerce_parameters_impl(self):          
        unit            = self.layout.dbu
        min_size        =  2 * unit
        self.base_w     = min_size if self.base_w <= min_size else self.base_w
        self.base_h     = min_size if self.base_h <= min_size else self.base_h


    def can_create_from_shape_impl(self):
        return self.shape.is_box() or self.shape.is_polygon() or self.shape.is_path()
        
    def transformation_from_shape_impl(self):
        return pya.Trans(self.shape.bbox().center())
        
    def parameters_from_shape_impl(self):
        pass
    
        
    def insert_placeholder(self):
        lib        = pya.Library.library_by_name("ArrayMagic")
        pcell_decl = lib.layout().pcell_declaration("PlaceHolder")
        param      = ["", self.base, self.arrow, self.fmark, self.base_w, self.base_h]
        pcell_var  = self.layout.add_pcell_variant(lib, pcell_decl.id(), param) 
        base_pcell = pya.CellInstArray(pcell_var, pya.DCplxTrans (1.0, 0, False, 0, 0 ), pya.Vector(0, 0), pya.Vector(0, 0), 0, 0)
        self.cell.insert(base_pcell)
    
    def insert_label(self):
        if self.text_str:
            self.cell.shapes(self.text_layer).insert(pya.DText(self.text_str, 0.0, 0.0))
            
    def produce_impl(self): 
        self.insert_placeholder()
        self.insert_label()
