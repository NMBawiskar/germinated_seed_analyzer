from PyQt5 import QtWidgets, QtMultimedia, QtCore,QtGui
from PyQt5.QtGui import QImage, QPixmap
import sys
import utils_pyqt5 as ut
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QWidget, QFileDialog
from main_processor import Main_Processor
import os

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QDialog.__init__(self)
             
        loadUi(r'UI_files\mainWindow_ui.ui',self)
        sizeObject = QtWidgets.QDesktopWidget().screenGeometry(-1)
        print(" Screen size : "  + str(sizeObject.height()) + "x"  + str(sizeObject.width()))   
        resized_w = sizeObject.width()
        resized_h = sizeObject.height() - 100
        self.setMaximumSize(resized_w,resized_h)
        self.org_design_w = 1920
        self.org_design_h = 1080

        self.new_screen_w = sizeObject.width()
        self.new_screen_h = sizeObject.height()
        # print(dir(self.pushButton_5))
        # print(self.pushButton_5.y())
        # print(self.pushButton_5.size().height())
        # self.resize_and_relocate(self.pushButton_5)
        # # print(dir(self.pushButton_5))
        # print(self.pushButton_5.y())
        # print(self.pushButton_5.size().height())
          
        # menubar = QtWidgets.QMenuBar()
        filemenu = self.menubar.addMenu('File')
        filemenu.addAction('Open Folder', self.browse_input_folder)
        self.input_folder_path = None
        self.imagePaths = []
        self.currentImgIndex = 0

        ################ Inputs
        self.n_segments_each_skeleton = 15           # divisions to make in each length (Increase this for finer results)
        self.thres_avg_max_radicle_thickness = 13    # avg thickness to distinguish radicle (tune this if camera position changes)
        self.dead_seed_max_length_r_h = 80
        self.abnormal_seed_max_length_r_h =  130
        self.normal_seed_max_length_r_h = 150

        self.weights_factor_growth_Pc = 0.7
        self.weights_factor_uniformity_Pu = 0.3


        ############ Button actions ############
        self.btnNext.clicked.connect(self.loadNextImg)
        self.btnPrev.clicked.connect(self.loadPrevImg)
        self.btn_apply.clicked.connect(self.apply_inputs)


        self.mainProcessor = Main_Processor()

    @QtCore.pyqtSlot()
    def browse_input_folder(self):
        action = self.sender()
        print('Action: ', action.text())
        qWid = QWidget()
        print("file browse")
        self.input_folder_path = QFileDialog.getExistingDirectory(qWid, 'Select folder', '')
        self.load_images()
        self.showImg()
        return self.input_folder_path
    

    def check_if_all_valid_inputs(self):
        if self.dead_seed_max_length_r_h >0 and self.abnormal_seed_max_length_r_h>0 and 

    def apply_inputs(self):


        if len(self.lineEdit_deadSeedL.text())>0 and self.lineEdit_deadSeedL.text().isnumeric():
            self.dead_seed_max_length_r_h = int(self.lineEdit_deadSeedL.text())
            self.mainProcessor.dead_seed_max_length_r_h = self.dead_seed_max_length_r_h
        if len(self.lineEdit_abnormal_seedL.text())>0 and self.lineEdit_abnormal_seedL.text().isnumeric():
            self.abnormal_seed_max_length_r_h =  int(self.lineEdit_abnormal_seedL.text())
            self.mainProcessor.abnormal_seed_max_length_r_h = self.abnormal_seed_max_length_r_h
            
        if len(self.lineEdit_normal_seedL.text())>0 and self.lineEdit_normal_seedL.text().isnumeric():
            self.normal_seed_max_length_r_h =  int(self.lineEdit_normal_seedL.text())
            self.mainProcessor.normal_seed_max_length_r_h = self.normal_seed_max_length_r_h
        if len(self.lineEdit_avg_rad_length.text())>0 and self.lineEdit_avg_rad_length.text().isnumeric():
            self.thres_avg_max_radicle_thickness =  int(self.lineEdit_avg_rad_length.text())
            self.mainProcessor.thres_avg_max_radicle_thickness = self.thres_avg_max_radicle_thickness
        self.n_segments_each_skeleton = self.spinBox_n_seg.value()           # divisions to make in each length (Increase this for finer results)
        self.mainProcessor.n_segments_each_skeleton = self.n_segments_each_skeleton                                                                    # avg thickness to distinguish radicle (tune this if camera position changes)
    
        self.weights_factor_growth_Pc =self.doubleSpinBox_pc.value()
        self.mainProcessor.weights_factor_growth_Pc = self.weights_factor_growth_Pc
        self.weights_factor_uniformity_Pu = self.doubleSpinBox_pu.value()
        self.mainProcessor.weights_factor_uniformity_Pu = self.weights_factor_uniformity_Pu

         



    def loadNextImg(self):
        if self.currentImgIndex<len(self.imagePaths)-1:
            self.currentImgIndex+=1
            self.showImg()
        
    
    def loadPrevImg(self):
        if self.currentImgIndex>=1:
            self.currentImgIndex-=1
            self.showImg()

    def load_images(self):

        if self.input_folder_path is not None:
            files = os.listdir(self.input_folder_path)
            self.imagePaths = [os.path.join(self.input_folder_path, fileName) for fileName in files]

    def showImg(self):
        imgPath = self.imagePaths[self.currentImgIndex]
        ut.apply_img_to_label_object(imgPath, self.imgLabel)
   


    def resize_and_relocate(self, obj):
        old_x = obj.x()
        old_y = obj.y()
        old_h = obj.size().height()
        old_w = obj.size().width()
        ratio_x = self.new_screen_w / self.org_design_w 
        ratio_y = self.new_screen_h / self.org_design_h

        new_x = int(ratio_x * old_x)
        new_y = int(ratio_y * old_y)
        new_w = int(ratio_x * old_w)
        new_h = int(ratio_y * old_h)
        obj.setGeometry(new_x, new_y, new_w, new_h)

    def displayImage(self, uiObj, img):
        qformat = QImage.Format_BGR888
        img = QImage(img, img.shape[1], img.shape[0], qformat)
        uiObj.setPixmap(QPixmap.fromImage(img))

    def close_win(self):
        self.close()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    w.setWindowTitle("Vigor-N")
    w.setWindowIcon(QtGui.QIcon(r'resources/QuicSolv-Fevicon.png'))
    sys.exit(app.exec())
    