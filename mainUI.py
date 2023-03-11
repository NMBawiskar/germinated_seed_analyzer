from PyQt5 import QtWidgets, QtMultimedia, QtCore,QtGui
from PyQt5.QtGui import QImage, QPixmap
import sys
import utils_pyqt5 as ut
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QWidget, QFileDialog
from main_processor import Main_Processor
import os
import csv
from settings_cls import GlobalSettings

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
        filemenu.addAction('Change settings', self.change_settings)
        filemenu.addAction('Inputs', self.give_inputs)
        filemenu.addAction("Set HSV values",self.set_hsv_values)
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
        


        ####### Results ###############
        self.growth =None
        self.penalization = None
        self.uniformity = None
        self.seed_vigor_index = None

        self.PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
        self.settings_dir = os.path.join(self.PROJECT_DIR, "settings")
        self.output_dir = os.path.join(self.PROJECT_DIR, 'output')
        self.settings_file_path = os.path.join(self.settings_dir, "settings.csv")


        self.mainProcessor = Main_Processor()

        self.list_inputs = [self.dead_seed_max_length_r_h, self.abnormal_seed_max_length_r_h, 
                    self.normal_seed_max_length_r_h, self.n_segments_each_skeleton, 
                    self.weights_factor_growth_Pc, self.weights_factor_uniformity_Pu]
        self.list_inputs_names = ["dead_seed_max_length", "abnormal_seed_max_length", 
                    "normal_seed_max_length", "no_of_segments_each_skeleton", 
                    "weights_factor_growth_Pc", "weights_factor_uniformity_Pu"]

        list_dir = [self.settings_dir, self.output_dir]
        self.create_dirs(list_dir)
        self.create_settings_if_not_present()


    def change_settings(self):
        self.window = GlobalSettings(self)
        self.window.show()
    
    def read_settings(self):

        dict_values = {}
        with open(self.settings_dir, 'r') as f:
            lines = f.read()
            lines = [line.replace("\n", "") for line in lines]
            for line in lines:
                key, value = line.split(",")
                dict_values[key]= value

        self.dead_seed_max_length_r_h = dict_values['dead_seed_max_length']
        self.abnormal_seed_max_length_r_h = dict_values['abnormal_seed_max_length']
        self.normal_seed_max_length_r_h = dict_values["normal_seed_max_length"]
        self.n_segments_each_skeleton = dict_values["no_of_segments_each_skeleton"]
        self.weights_factor_growth_Pc = dict_values["weights_factor_growth_Pc"]
        self.weights_factor_uniformity_Pu = dict_values["weights_factor_uniformity_Pu"]



    def set_hsv_values(self):
        pass

    def give_inputs(self):
        self.cultivatorName, done1 = QtWidgets.QInputDialog.getText(
             self, 'Inputs', 'Enter cultivator name:') 
        self.analystsName, done2 = QtWidgets.QInputDialog.getText(
           self, 'Inputs', 'Enter Analysts name:')
        self.batchNo, done3 = QtWidgets.QInputDialog.getInt(
           self, 'Inputs', 'Enter Batch no:') 
 
        if done1 and done2 and done3:
            self.label_cult_name.setText(str(self.cultivatorName))
            self.label_analys_name.setText(str(self.analystsName))
            self.label_batchNo.setText(str(self.batchNo))
            
    def save_settings_to_file(self):
        print("Saving in settings file...")
        try:
            os.remove(self.settings_file_path)
        except Exception as e:
            print(e)
        with open(self.settings_file_path, 'a+', newline="") as f:
            csvWriter = csv.writer(f)                    
            print("self.dead_seed_max_length_r_h", self.dead_seed_max_length_r_h)
            self.list_inputs = [self.dead_seed_max_length_r_h, self.abnormal_seed_max_length_r_h, 
                    self.normal_seed_max_length_r_h, self.n_segments_each_skeleton, 
                    self.weights_factor_growth_Pc, self.weights_factor_uniformity_Pu]
            for i in range(len(self.list_inputs)):
                list_each = [self.list_inputs_names[i], self.list_inputs[i]]
                csvWriter.writerow(list_each)

    def create_settings_if_not_present(self):
        if not os.path.exists(self.settings_file_path):
            self.save_settings_to_file()


    def create_dirs(self, dir_list):
        for dir_path in dir_list:
            os.makedirs(dir_path, exist_ok=True)

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
        

        validated = True
        for inputs in self.list_inputs:
            if inputs >=0:
                pass
            else:
                validated=False
        
        return validated
        
    def display_results(self):
        
        self.label_growth.setText(str(self.growth))
        self.label_penalization.setText(str(self.penalization))
        self.label_uniformity.setText(str(self.uniformity))
        self.label_seedvigor.setText(str(self.seed_vigor_index))

    

        if self.check_if_all_valid_inputs():

            ## Process for main
            imgPath = self.imagePaths[self.currentImgIndex]
            list_hypercotyl_radicle_lengths, colorImg, batchAnalyserObj = self.mainProcessor.process_main(imgPath)
            self.growth = round(batchAnalyserObj.growth,2)
            self.penalization = round(batchAnalyserObj.penalization,2)
            self.uniformity = round(batchAnalyserObj.uniformity,2)
            self.seed_vigor_index = round(batchAnalyserObj.seed_vigor_index,2)

            self.display_results()

            self.showResultImg(colorImg)

    def loadNextImg(self):
        if self.currentImgIndex<len(self.imagePaths)-1:
            self.currentImgIndex+=1
            self.showImg()
    
    def loadPrevImg(self):
        if self.currentImgIndex>=1:
            self.currentImgIndex-=1
            self.showImg()

    def load_images(self):

        if self.input_folder_path is not None and len(self.input_folder_path)>1:
            files = os.listdir(self.input_folder_path)
            self.imagePaths = [os.path.join(self.input_folder_path, fileName) for fileName in files]

    def showImg(self):

        if len(self.imagePaths)>0:
            imgPath = self.imagePaths[self.currentImgIndex]
            ut.apply_img_to_label_object(imgPath, self.imgLabel)
    
    def showResultImg(self, imgNumpy):
        h, w, ch = imgNumpy.shape
        bytesPerLine = 3 * w
        qImg = QImage(imgNumpy.data, w, h, bytesPerLine, QImage.Format_RGB888)
        pixmap = QtGui.QPixmap.fromImage(qImg)
        self.imgLabel.setPixmap(pixmap)
    
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
    