import pya

class PlaceHolder(pya.PCellDeclarationHelper):
    def __init__(self):
        super(PlaceHolder, self).__init__()
        self.param("name",   self.TypeString,  "Name",             default = "")
        self.param("base",   self.TypeLayer,   "Layer for Base",   default = pya.LayerInfo(1, 0))
        self.param("arrow",  self.TypeLayer,   "Layer for Arrow",  default = pya.LayerInfo(1, 0))
        self.param("fmark",  self.TypeLayer,   "Layer for F-mark", default = pya.LayerInfo(1, 0))

        self.param("base_w", self.TypeDouble,  "Width",            default =  20, unit = "um")
        self.param("base_h", self.TypeDouble,  "Height",           default =  10, unit = "um")
        
    def display_text_impl(self):
        class_name  = self.__class__.__name__
        custom_name = (self.name + "__" if self.name else "") 
        disp_str    = "_%.2fx%.2f" % (self.base_w, self.base_h)

        return "%s%s%s" % (custom_name, class_name, disp_str)
        
    def can_create_from_shape_impl(self):
        return self.shape.is_box() or self.shape.is_polygon() or self.shape.is_path() 

    def transformation_from_shape_impl(self):
        return pya.Trans(self.shape.bbox().center())
        
    def coerce_parameters_impl(self):          
        unit            = self.layout.dbu
        min_size        =  2 * unit
        min_arrow_size  = 64 * unit
        min_fmark_size  = 64 * unit
        self.show_arrow = min_arrow_size > min(self.base_w, self.base_h)
        self.show_fmark = min_fmark_size > min(self.base_w, self.base_h)

    def parameters_from_shape_impl(self):
        pass

    def arrow_pts(self, x, y, size):
        lw = size / 10 * 0.8

        x0, x1, x2, x3, x4 = [ x - lw * 2, x - lw * 1, x, x + lw * 1, x + lw * 2]
        y0, y1, y2,        = [ y + lw * 4, y, y - lw * 3]

        return [
            pya.DPoint(x0, y1), pya.DPoint(x2, y0), pya.DPoint(x4, y1), pya.DPoint(x3, y1), 
            pya.DPoint(x3, y1), pya.DPoint(x3, y2), pya.DPoint(x1, y2), pya.DPoint(x1, y1), 
            pya.DPoint(x0, y1),  
        ]
        
    def fmark_pts(self, x, y, size):
        lw = size / 10 * 0.8
        
        x0, x1, x2, x3     = [ x - lw * 2, x - lw * 1, x + lw * 1, x + lw * 2]
        y0, y1, y2, y3, y4 = [ y - lw * 3, y, y + lw, y + lw * 3,  y + lw * 4]

        return [
            pya.DPoint(x0, y0), pya.DPoint(x0, y4), pya.DPoint(x3, y4), pya.DPoint(x3, y3), 
            pya.DPoint(x1, y3), pya.DPoint(x1, y2), pya.DPoint(x2, y2), pya.DPoint(x2, y1), 
            pya.DPoint(x1, y1), pya.DPoint(x1, y0), 
        ]
        
    def produce_impl(self): 
        pattern_size = min(self.base_w, self.base_h) * 0.8

        base_rect = pya.DBox(
            pya.DPoint( self.base_w/2,  self.base_h/2), 
            pya.DPoint(-self.base_w/2, -self.base_h/2)
        )
        
        self.cell.shapes(self.base_layer).insert(base_rect)

        if not(self.show_arrow):
            arrow_poly = pya.DPolygon(self.arrow_pts( 0, 0, pattern_size))
            self.cell.shapes(self.arrow_layer).insert(arrow_poly)
        
        if not(self.show_fmark):
            fmark_poly = pya.DPolygon(self.fmark_pts( 0, 0, pattern_size))
            self.cell.shapes(self.fmark_layer).insert(fmark_poly)