import pya

from util_CsvImport          import *
from util_CsvPCell           import *

class CSVArrayWidget(pya.QWidget):
    def __init__(self, parent = None):
        super(CSVArrayWidget, self).__init__()
        self.lv           = None
        self.cv           = None
        self.ly           = None
        self.processStart = False
        self.importer     = CsvImport()
        self.injector     = CsvPCell(self)
        self.initUI()
        self.initSignal()
        self.setWindowTitle("import CSV data")
        
    def initUI(self):
        self.file_name_edit = pya.QLineEdit()
        self.status_edit    = pya.QTextEdit()
        self.get_file_pb    = pya.QPushButton("...")
        self.import_pb      = pya.QPushButton("Start Import")
        self.grid           = pya.QGridLayout()
        self.progress       = pya.QProgressBar()
                
        self.grid.addWidget(pya.QLabel("csv File path:"), 0, 0, 1, 1)
        
        self.grid.addWidget(self.file_name_edit, 0, 1, 1, 1)
        self.grid.addWidget(self.get_file_pb,    0, 2, 1, 1)
        self.grid.addWidget(self.status_edit,    1, 0, 1, 3)
        self.grid.addWidget(self.progress,       2, 0, 1, 3)
        self.grid.addWidget(self.import_pb,      3, 0, 1, 3)

        self.progress.setValue(0)
        self.grid.setColumnMinimumWidth(0, 70)
        self.grid.setColumnStretch(1, 1)
        self.grid.setRowStretch(1, 1)
        self.setLayout(self.grid)

        self.get_file_pb.setFixedWidth(35)
        self.file_name_edit.setReadOnly (True)
        self.status_edit.setReadOnly (True)
    
    def initSignal(self):
        self.get_file_pb.clicked.connect(self.load)
        self.import_pb.clicked.connect(self.trigger)
        pass
        
                      
    def load(self):
        path = pya.QFileDialog.getOpenFileName(filter = "*csv")

        if path:
            with open(path, 'rb') as f:
                self.importer.open_csv(path)
                self.file_name_edit.setText(path)
                self.status_edit.setText(str(self.importer.df))
                pya.QToolTip.showText(pya.QCursor.pos, f"File loaded : {path}")
                
                
    def layoutValidate(self):
        try:
            self.lv = pya.Application.instance().main_window().current_view()
            self.cv = self.lv.active_cellview()
            self.ly = self.cv.layout()
            
        except :
            self.lv = None
            self.cv = None
            self.ly = None
            
    def trigger(self):
        if self.processStart == True:
            self.cancelProcess()
        else:
            self.startProcess()
            
    def insertCell(self):
        if any([(self.importer.df is None), (self.importer.placement_type is None), (self.ly is None)]) : return
        cell         = self.ly.create_cell("CSVArray")
        self.cv.cell = cell
        xmin, xmax   = self.importer.df['x'].agg(['min', 'max'])
        ymin, ymax   = self.importer.df['y'].agg(['min', 'max'])
        self.lv.zoom_box(pya.DBox(pya.DPoint(xmin, ymin), pya.DPoint(xmax, ymax)))
        self.injector.startProcess(cell, self.importer.df, self.importer.placement_type)
    
    def startProcess(self):
        self.layoutValidate()
        self.insertCell()
    
    def cancelProcess(self):
        self.injector.cancelProcess()
        
    def finishProcess(self):
        self.processStart = False
        self.import_pb.setText("Start Import")
        self.enableUI(True)
        
    def proceedProcess(self):
        self.processStart = True
        self.import_pb.setText("Abort")
        self.enableUI(False)
        
    def updateProgress(self, progress):
        self.progress.setValue(progress)
        self.lv.add_missing_layers()
        pya.Application.instance().processEvents()
        
    def enableUI(self, enable):
        self.get_file_pb.setEnabled   (enable)
        self.file_name_edit.setEnabled(enable)
        self.status_edit.setEnabled   (enable)
              
if __name__ == "__main__": 
    liw  = CSVArrayWidget()
    liw.show()
 