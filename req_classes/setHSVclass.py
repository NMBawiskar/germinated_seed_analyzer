from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import  QWidget
from PyQt5.uic import loadUi
from utils_pyqt5 import showdialog

class SetHSV(QWidget):
    def __init__(self, mainUi):
        super().__init__()
        loadUi(r'UI_files\set_hsv_ui.ui', self)
        self.mainUi = mainUi


        self.slider_hmin.setMinimum(0)
        self.slider_hmax.setMaximum(179)
        self.slider_smin.setMinimum(0)
        self.slider_smax.setMaximum(255)
        self.slider_vmin.setMinimum(0)
        self.slider_vmax.setMaximum(255)
        self.hsvValuesToread = self.mainUi.hsv_values_seed_heads

        self.slider_hmin.valueChanged.connect(self.updateValues)
        self.slider_hmax.valueChanged.connect(self.updateValues)
        self.slider_smin.valueChanged.connect(self.updateValues)
        self.slider_smax.valueChanged.connect(self.updateValues)
        self.slider_vmin.valueChanged.connect(self.updateValues)
        self.slider_vmax.valueChanged.connect(self.updateValues)



        self.radioHSV_seed_head.seed_part = 'Head'
        self.radioHSV_seed_head.clicked.connect(self.onClicked)
        self.radio_hsv_seed_body.seed_part = 'Body'
        self.radio_hsv_seed_body.clicked.connect(self.onClicked)
        self.radioHSV_seed_head.setChecked(True)

        self.seedPart = 'Head'
        self.updateValuesForPartType()
        


    def updateValuesForPartType(self):


        self.set_hsv_values()
        self.show_current_values()

    def updateValues(self):

        self.show_current_values()
        self.set_hsv_values()
    


    def onClicked(self):
        radioButton = self.sender()
        if radioButton.isChecked():
            print("Seed part is %s" % (radioButton.seed_part))
            self.seedPart = radioButton.seed_part

            if self.seedPart=="Head":
                self.hsvValuesToread= self.mainUi.hsv_values_seed_heads
                print("setting hsvValuesToread of head", self.mainUi.hsv_values_seed_heads)
            elif self.seedPart=="Body":
                self.hsvValuesToread= self.mainUi.hsv_values_seed
                print("setting hsvValuesToread of body", self.mainUi.hsv_values_seed)
            
            self.updateValuesForPartType()

    def set_hsv_values(self):
        

        self.slider_hmin.setValue(self.hsvValuesToread[0])
        self.slider_hmax.setValue(self.hsvValuesToread[1])
        self.slider_smin.setValue(self.hsvValuesToread[2])
        self.slider_smax.setValue(self.hsvValuesToread[3])
        self.slider_vmin.setValue(self.hsvValuesToread[4])
        self.slider_vmax.setValue(self.hsvValuesToread[5])

        

    def show_current_values(self):
        self.hsvValuesToread[0] = int(self.slider_hmin.value())
        self.hsvValuesToread[1] = int(self.slider_hmax.value())
        self.hsvValuesToread[2] = int(self.slider_smin.value())
        self.hsvValuesToread[3] = int(self.slider_smax.value())
        self.hsvValuesToread[4] = int(self.slider_vmin.value())
        self.hsvValuesToread[5] = int(self.slider_vmax.value())      


        self.label_hmin.setText(str(self.slider_hmin.value()))
        self.label_hmax.setText(str(self.slider_hmax.value()))
        self.label_smin.setText(str(self.slider_smin.value()))
        self.label_smax.setText(str(self.slider_smax.value()))
        self.label_vmin.setText(str(self.slider_vmin.value()))
        self.label_vmax.setText(str(self.slider_vmax.value()))