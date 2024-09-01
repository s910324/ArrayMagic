import pya

from util_CsvImport          import *
from util_CsvPCell           import *

class CSVArrayWidget(pya.QWidget):
    def __init__(self, parent = None):
        super(CSVArrayWidget, self).__init__()
        self.processStart = False
        self.importer = CsvImport()
        self.injector = CsvPCell(self)
        self.initUI()
        self.initSignal()
        self.setWindowTitle("import CSV data")
        
    def initUI(self):
        self.file_name_edit = pya.QLineEdit()
        self.status_edit    = pya.QTextEdit()
        self.get_file_pb    = pya.QPushButton("...")
        self.import_pb      = pya.QPushButton("Start Import")
        self.layout         = pya.QGridLayout()
        self.progress       = pya.QProgressBar()
                
        self.layout.addWidget(pya.QLabel("csv File path:"), 0, 0, 1, 1)
        
        self.layout.addWidget(self.file_name_edit, 0, 1, 1, 1)
        self.layout.addWidget(self.get_file_pb,    0, 2, 1, 1)
        self.layout.addWidget(self.status_edit,    1, 0, 1, 3)
        self.layout.addWidget(self.progress,       2, 0, 1, 3)
        self.layout.addWidget(self.import_pb,      3, 0, 1, 3)

        self.progress.setValue(0)
        self.layout.setColumnMinimumWidth(0, 70)
        self.layout.setColumnStretch(1, 1)
        self.layout.setRowStretch(1, 1)
        self.setLayout(self.layout)

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
            lv      = pya.Application.instance().main_window().current_view()
            cv      = lv.active_cellview()
            layout  = cv.layout()
            return lv, cv, layout
        except :
            return None, None, None
    
    def trigger(self):
        if self.processStart == True:
            self.cancelProcess()
        else:
            self.startProcess()
            
    def insertCell(self):
        lv, cv, layout = self.layoutValidate()
        if any([(self.importer.df is None), (layout is None)]) : return

        cell       = layout.create_cell("CSVArray")
        cv.cell    = cell
        xmin, xmax = self.importer.df['x'].agg(['min', 'max'])
        ymin, ymax = self.importer.df['y'].agg(['min', 'max'])
        lv.zoom_box(pya.DBox(pya.DPoint(xmin, ymin), pya.DPoint(xmax, ymax)))
        self.injector.startProcess(cell, self.importer.df)
    
    def startProcess(self):
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
        pya.Application.instance().processEvents()
        
    def enableUI(self, enable):
        self.get_file_pb.setEnabled   (enable)
        self.file_name_edit.setEnabled(enable)
        self.status_edit.setEnabled   (enable)
              
if __name__ == "__main__": 
    liw  = CSVArrayWidget()
    liw.show()
 