from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget, QFileDialog
from PyQt5.uic import loadUi
from utils_pyqt5 import showdialog
import os
import utils_pyqt5 as ut
import cv2
from req_classes.pixel_to_cm import get_pixel_to_cm

class CalibrationSettings(QWidget):
    def __init__(self, mainUi):
        super().__init__()
        loadUi(r'UI_files\pixel_cm_setting_ui.ui', self)
        self.mainUi = mainUi

        self.mainUi.read_settings()

        self.lineEdit_pixel_cm.setText(str(self.mainUi.dict_settings['factor_pixel_to_cm']))
        self.btn_load_calib_img.clicked.connect(self.load_calib_image)
        self.btnSave.clicked.connect(self.saveSetting)


    def load_calib_image(self):

        qWid = QWidget()
        print("Select measurements caliberation image")
        filepath, _ = QFileDialog.getOpenFileName(qWid, 'Select measurements caliberation image','',"Image files (*.jpg)")
        if not os.path.exists(filepath):
            ut.showdialog("Please select a file")
        else:
            img = cv2.imread(filepath)
            
            self.mainUi.pixel_per_cm = get_pixel_to_cm(img)

            print("Pixels per centimeter is :", self.mainUi.pixel_per_cm)
            # cv2.imshow('img', img)
            self.mainUi.dict_settings['factor_pixel_to_cm'] = self.mainUi.pixel_per_cm
            # cv2.waitKey(-1)
            print("self.dict_settings['factor_pixel_to_cm']", self.mainUi.dict_settings['factor_pixel_to_cm'])
            self.lineEdit_pixel_cm.setText(str(self.mainUi.dict_settings['factor_pixel_to_cm']))

            ut.showdialog(f"Calibration done! \n {self.mainUi.pixel_per_cm} pixel = 1 cm. ")
            self.mainUi.save_settings_to_file()
            self.mainUi.process_img_and_display_results()
            self.close()

    def saveSetting(self):
        if len(self.lineEdit_pixel_cm.text())>0 and self.lineEdit_pixel_cm.text().isnumeric():
            self.mainUi.pixel_per_cm =  int(self.lineEdit_pixel_cm.text())
            self.mainUi.dict_settings['factor_pixel_to_cm'] = int(self.lineEdit_pixel_cm.text())

            self.mainUi.save_settings_to_file()
            ut.showdialog(f"Saved! \n {self.mainUi.pixel_per_cm} pixel = 1 cm. \n Saved in settings. ")
            self.mainUi.process_img_and_display_results()
        else:
            ut.showdialog(f"Please enter integer value. ")
        
        self.close()