import os
import pya
import datetime
import numpy as np
import pandas as pd
from util_CsvImport          import *

class CsvPCell(object):
    def __init__(self, ui = None):
        super(CsvPCell, self).__init__()
        self.ui    = ui
        self.abort = False
        pd.set_option("display.max_columns", None)
        
    def place_pcell_shape(self, layout, cell, shape, layer, datatype, x, y, width, height, rotate, mirror):
        width, height = float(width), float(height)
        lib           = pya.Library.library_by_name("ArrayMagic")
        pcell_decl    = lib.layout().pcell_declaration(f"{shape}Holder")
        ly_info       = self.layer_info(layout, layer, datatype)
        param         = [ly_info, width, height]
        item          = layout.add_pcell_variant(lib, pcell_decl.id(), param) 
        self.cell_placer(layout, cell, item, x, y, rotate, mirror)

    def place_pcell_text(self, layout, cell, text, layer, datatype, mag, inverse, bias, cspacing, lspacing, x, y, rotate, mirror):
        lib        = pya.Library.library_by_name("Basic")
        pcell_decl = lib.layout().pcell_declaration("TEXT")
        ly_info    = self.layer_info(layout, layer, datatype)
        param      = {"layer": ly_info, "text": text, "mag" : mag, "inverse" : inverse, "bias" : bias, "cspacing" : cspacing, "lspacing" : lspacing, }
        item       =  layout.add_pcell_variant(lib, pcell_decl.id(), param) 
        self.cell_placer(layout, cell, item, x, y, rotate, mirror)

    def place_text(self, layout, cell, text, layer, datatype, x, y):
        ly_id   = layout.layer(layer, datatype)
        ly_info = layout.get_info(ly_id)
        cell.shapes(ly_info).insert(pya.DText(text, x, y))
    
    def cell_placer(self, layout, cell, item, x, y, r, m):
        x, y, r, m = float(x), float(y), float(r), float(m)
        unit = layout.dbu
        um   = 1 / unit
        inst = pya.CellInstArray(item, pya.DCplxTrans (1.0, r, m, x * um, y * um), pya.Vector(0, 0), pya.Vector(0, 0), 0, 0)
        cell.insert(inst)
        
    def layer_info(self, layout, layer, datatype):
        ly_id = layout.layer(int(layer), int(datatype))
        return layout.get_info(ly_id)
        
    def startProcess(self, cell, df, placement_type):
        self.updateProgress(0)    
        
        if any( [ (i is None) for i in [ df, cell] ] ) : 
            self.cancelProcess()
            self.finishProcess()
            return None
            
        row    = df.shape[0]
        seg    = int(row / 100)
        seg    = row if (seg == 0) else seg
        layout = cell.layout()

        self.proceedProcess()
        item_placer = {
            "pcell_shape" : lambda params : self.place_pcell_shape(** params),
            "pcell_text"  : lambda params : self.place_pcell_text (** params),
            "text"        : lambda params : self.place_text       (** params),
            "cell"        : lambda params : self.place_cell       (** params),
        }[placement_type]

        for i in range(row):
            if self.abort : break
            if (i % seg) == 0 : self.updateProgress(i / row * 100)
            params = dict(df.iloc[i]) | {"layout" : layout, "cell" : cell}
            item_placer(params)
        self.finishProcess()  

    def proceedProcess(self):
        if self.ui:
            self.ui.proceedProcess()

    def finishProcess(self):
        if not(self.abort) :self.updateProgress(100)
        
        self.abort = False
        if self.ui:
            self.ui.finishProcess()

    def cancelProcess(self):
        self.abort = True 
            
    def updateProgress(self, progress):
        if self.ui:
            self.ui.updateProgress(progress)
        

        
    
if __name__ == "__main__": 
    lv       = pya.Application.instance().main_window().current_view()
    cv       = lv.active_cellview()
    layout   = cv.layout()
    i        = CsvImport()
    p        = CsvPCell()
    path     = r"C:\Users\scott\KLayout\pymacros\Library\ArrayMagic\Examples\pcell_shape_1.csv"
    cell     = layout.create_cell("CSVArray")
    i.open_csv(path)
    p.startProcess(cell, i.df)