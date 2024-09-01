import pya 

class RectHolder(pya.PCellDeclarationHelper):
    def __init__(self):
        super(RectHolder, self).__init__()
        self.param("base",   self.TypeLayer,   "Layer for Base",   default = pya.LayerInfo(1, 0))
        self.param("base_w", self.TypeDouble,  "Width",            default =  20, unit = "um")
        self.param("base_h", self.TypeDouble,  "Height",           default =  10, unit = "um")
        
    def display_text_impl(self):
        class_name  = self.__class__.__name__
        disp_str    = "_%.2fx%.2f" % (self.base_w, self.base_h)
        return "%s%s" % (class_name, disp_str)
        
    def can_create_from_shape_impl(self):
        return self.shape.is_box() or self.shape.is_polygon() or self.shape.is_path() 

    def transformation_from_shape_impl(self):
        return pya.Trans(self.shape.bbox().center())
        
    def coerce_parameters_impl(self):          
        self.base_w = 0 if self.base_w < 0 else self.base_w
        self.base_h = 0 if self.base_h < 0 else self.base_h

    def parameters_from_shape_impl(self):
        pass

    def produce_impl(self): 
        self.cell.shapes(self.base_layer).insert(pya.DBox(
            pya.DPoint( self.base_w/2,  self.base_h/2), 
            pya.DPoint(-self.base_w/2, -self.base_h/2)
        ))