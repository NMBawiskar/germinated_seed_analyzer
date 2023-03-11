from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import  QWidget
from PyQt5.uic import loadUi
from utils_pyqt5 import showdialog

class GlobalSettings(QWidget):
    def __init__(self, mainUi):
        super().__init__()
        loadUi(r'UI_files\settings_ui.ui', self)
        self.mainUi = mainUi
        self.btn_apply.clicked.connect(self.apply_inputs)
        self.btn_cancel.clicked.connect(self.close_window)

        self.mainUi.read_settings()

    
    def set_stored_values(self):
        pass

    def apply_inputs(self):

        if len(self.lineEdit_deadSeedL.text())>0 and self.lineEdit_deadSeedL.text().isnumeric():
            self.mainUi.dead_seed_max_length_r_h = int(self.lineEdit_deadSeedL.text())
            
        if len(self.lineEdit_abnormal_seedL.text())>0 and self.lineEdit_abnormal_seedL.text().isnumeric():
            self.mainUi.abnormal_seed_max_length_r_h =  int(self.lineEdit_abnormal_seedL.text())
            
            
        if len(self.lineEdit_normal_seedL.text())>0 and self.lineEdit_normal_seedL.text().isnumeric():
            self.mainUi.normal_seed_max_length_r_h =  int(self.lineEdit_normal_seedL.text())
            
        if len(self.lineEdit_avg_rad_length.text())>0 and self.lineEdit_avg_rad_length.text().isnumeric():
            self.mainUi.thres_avg_max_radicle_thickness =  int(self.lineEdit_avg_rad_length.text())
            
        self.mainUi.n_segments_each_skeleton = self.spinBox_n_seg.value()           # divisions to make in each length (Increase this for finer results)
                                                                      # avg thickness to distinguish radicle (tune this if camera position changes)
        self.mainUi.weights_factor_growth_Pc =self.doubleSpinBox_pc.value()
        self.mainUi.weights_factor_uniformity_Pu = self.doubleSpinBox_pu.value()
        
        ### Call method to save values
        print("self.mainUi.dead_seed_max_length_r_h",self.mainUi.dead_seed_max_length_r_h)
        self.mainUi.save_settings_to_file()
        showdialog("Settings saved successfully!!!")
        self.close_window()

    

    def close_window(self):
        print("Closing window")
        self.close()
   