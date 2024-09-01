import os
import pya
import datetime
import numpy as np
import pandas as pd

class CsvPCell(object):
    def __init__(self, ui = None):
        super(CsvPCell, self).__init__()
        self.ui    = ui
        self.abort = False
        
    def pcell_rect(self, layout, layer_no, layer_dt, base_w, base_h):
        base_w, base_h = float(base_w), float(base_h)
        lib            = pya.Library.library_by_name("ArrayMagic")
        pcell_decl     = lib.layout().pcell_declaration("RectHolder")
        ly_id          = layout.layer(layer_no, layer_dt)
        ly_info        = layout.get_info(ly_id)
        param          = [ly_info, base_w, base_h]
        return layout.add_pcell_variant(lib, pcell_decl.id(), param) 
    
    def cell_placer(self, layout, cell, x,  y, angle, mirror):
        x, y, angle, mirror = float(x), float(y), float(angle), float(mirror)
        unit = layout.dbu
        um   = 1 / unit
        return pya.CellInstArray(cell, pya.DCplxTrans (1.0, angle, mirror, x * um, y * um), pya.Vector(0, 0), pya.Vector(0, 0), 0, 0)
    
        
    def startProcess(self, cell, df):
        self.updateProgress(0)    
        
        if any( [ (i is None) for i in [ df, cell] ] ) : 
            self.cancelProcess()
            self.finishProcess()
            return None
            
        row    = df.shape[0]
        seg    = int(row / 100)
        layout = cell.layout()

        self.proceedProcess()

        for i in range(row):
            if self.abort : break
            if (i % seg) == 0 : self.updateProgress(i / row * 100)
            row_data         = df.iloc[i]
            x, y, w, h, r, m = row_data
            item = self.pcell_rect(layout, 0, 0, w, h,)
            cell.insert(self.cell_placer(layout, item, x, y, r, m))
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

    p  = CsvPCell()
    