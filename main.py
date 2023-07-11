from PyQt5 import QtWidgets, QtMultimedia, QtCore,QtGui
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt
import sys
import utils_pyqt5 as ut
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QWidget, QFileDialog
from main_processor import Main_Processor
import os
import csv
from req_classes.settings_cls import GlobalSettings
from req_classes.setHSVclass import SetHSV
from datetime import datetime
import numpy as np
import pandas as pd
from class_photo_viewer import PhotoViewer
from req_classes.pixel_to_cm import get_pixel_to_cm
from req_classes.seedEditor import SeedEditor
import cv2
import json
import traceback

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

        ## load

        self.viewer = PhotoViewer(self)
        self.h_layout_img.addWidget(self.viewer)

        self.new_screen_w = sizeObject.width()
        self.new_screen_h = sizeObject.height()
        
          
        # menubar = QtWidgets.QMenuBar()
        
        filemenu = self.menubar.addMenu('File')
        
        filemenu.addAction('Open Folder', self.browse_input_folder)
        filemenu.addAction('Inputs', self.give_inputs)
      

        menuConfig = self.menubar.addMenu('Configuration')
        menuConfig.addAction("Import Configurations", self.import_settings)
        menuConfig.addAction("Export Settings", self.export_settings)
        menuConfig.addAction('Change settings', self.change_settings)
        menuConfig.addAction("Set HSV values",self.set_hsv_values)
        menuConfig.addAction("Set caliberation",self.set_pixel_cm_values)
        menuConfig.addAction("Restore Defaults",self.restore_default_settings)



        filemenu.setStyleSheet("""background-color: None;
                            font: 63 10pt "Segoe UI";
                            border-top: none;
                            border-left:none;
                            border-bottom:none;
                            border-left:3px solid  
                            rgb(44,205,112);""")
        
        self.input_folder_path = None
        self.imagePaths = []
        self.batchAnalyzerObjList = []

        self.currentImgIndex = 0

        ################ Inputs
        self.n_segments_each_skeleton = 15           # divisions to make in each length (Increase this for finer results)
        self.thres_avg_max_radicle_thickness = 13    # avg thickness to distinguish radicle (tune this if camera position changes)
        self.dead_seed_max_length_r_h = 80
        self.abnormal_seed_max_length_r_h =  130
        self.normal_seed_max_length_r_h = 150
        self.average_seed_total_length = 500
        self.list_hypercotyl_radicle_lengths = []

        self.weights_factor_growth_Pc = 0.7
        self.weights_factor_uniformity_Pu = 0.3

        self.pixel_per_cm = 40

        self.hsv_values_seed_heads = [0,127,0,255,0,34]     ###### Default values do not change here
        self.hsv_values_seed = [0,179,0,255,0,162]          ###### Default values do not change here

        self.cultivatorName = ""
        self.analystsName = ""
        self.batchNo = 0
        self.n_seeds = 20

        self.data_each_seed = []
        self.germination_percent = 0
        self.scale = 1

        ############ Button actions ############
        self.btnNext.clicked.connect(self.loadNextImg)
        self.btnPrev.clicked.connect(self.loadPrevImg)
        # self.btn_get_result.clicked.connect(self.process_img_and_display_results)
        self.tableView_res.clicked.connect(self.get_selected_row)

        ####### Results ###############
        self.growth =None
        self.penalization = None
        self.uniformity = None
        self.seed_vigor_index = None

        self.count_abnormal_seeds = 0
        self.count_dead_seeds = 0
        self.count_germinated_seeds = 0

        self.PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
        self.settings_dir = os.path.join(self.PROJECT_DIR, "settings")
        self.output_dir = os.path.join(self.PROJECT_DIR, 'output')
        self.output_results_dir = os.path.join(self.output_dir, 'results')
        self.output_images_dir = os.path.join(self.output_dir, 'processed_images')
        # self.output_batch_dir = os.path.join(self.output_dir, self.batchNo)
        # self.settings_file_path = os.path.join(self.settings_dir, "settings.csv")
        self.settings_json_file_path =  os.path.join(self.settings_dir, "settings.json")
        # self.settings_hsv_path = os.path.join(self.settings_dir, "settings_hsv.csv")

        self.mainProcessor = Main_Processor()
        self.mainProcessor.hsv_values_seed = self.hsv_values_seed
        self.mainProcessor.hsv_values_seed_heads = self.hsv_values_seed_heads

        self.list_inputs = [self.dead_seed_max_length_r_h, self.abnormal_seed_max_length_r_h, 
                    self.normal_seed_max_length_r_h, self.n_segments_each_skeleton,
                    self.weights_factor_growth_Pc, self.weights_factor_uniformity_Pu]
        

        self.dict_settings = {                            
                            "dead_seed_max_length": self.dead_seed_max_length_r_h, 
                            "abnormal_seed_max_length":self.abnormal_seed_max_length_r_h, 
                            "normal_seed_max_length":self.normal_seed_max_length_r_h, 
                            "no_of_segments_each_skeleton":self.n_segments_each_skeleton,
                            "weights_factor_growth_Pc":self.weights_factor_growth_Pc, 
                            "weights_factor_uniformity_Pu":self.weights_factor_uniformity_Pu,
                            "thresh_avg_max_radicle_thickness":self.thres_avg_max_radicle_thickness,
                            "average_seed_total_length":self.average_seed_total_length,
                            'hmin_head':self.hsv_values_seed_heads[0],
                            'hmax_head':self.hsv_values_seed_heads[1],
                            'smin_head':self.hsv_values_seed_heads[2],
                            'smax_head':self.hsv_values_seed_heads[3],
                            'vmin_head':self.hsv_values_seed_heads[4],
                            'vmax_head':self.hsv_values_seed_heads[5],
                            'hmin_body':self.hsv_values_seed[0],
                            'hmax_body':self.hsv_values_seed[1],
                            'smin_body':self.hsv_values_seed[2],
                            'smax_body':self.hsv_values_seed[3],
                            'vmin_body':self.hsv_values_seed[4],
                            'vmax_body':self.hsv_values_seed[5],
                            'factor_pixel_to_cm':self.pixel_per_cm
                            
                            }

        self.list_inputs_names = ["dead_seed_max_length", "abnormal_seed_max_length", 
                    "normal_seed_max_length", "no_of_segments_each_skeleton", 
                    "weights_factor_growth_Pc", "weights_factor_uniformity_Pu"]


        self.list_hsv_keys = ['hmin','hmax','smin','smax','vmin','vmax',]
        list_dir = [self.settings_dir, self.output_dir]
        self.create_dirs(list_dir)
        self.create_settings_if_not_present()
        self.read_settings()
        

        imgLogo = cv2.imread('resources/ProSeedling_logo_cropped.png')
        ut.apply_img_to_label_object('resources/ProSeedling_logo_cropped_transparent.png', self.label_logo)
        
        self.seedEditorObj = SeedEditor(self)

    def restore_default_settings(self):
        ################ Inputs
        self.n_segments_each_skeleton = 15           # divisions to make in each length (Increase this for finer results)
        self.thres_avg_max_radicle_thickness = 13    # avg thickness to distinguish radicle (tune this if camera position changes)
        self.dead_seed_max_length_r_h = 80
        self.abnormal_seed_max_length_r_h =  130
        self.normal_seed_max_length_r_h = 150
        self.average_seed_total_length = 500
        self.list_hypercotyl_radicle_lengths = []

        self.weights_factor_growth_Pc = 0.7
        self.weights_factor_uniformity_Pu = 0.3

        self.pixel_per_cm = 40

        self.hsv_values_seed_heads = [0,127,0,255,0,34]     ###### Default values do not change here
        self.hsv_values_seed = [0,179,0,255,0,162] 
        self.dict_settings = {                            
                            "dead_seed_max_length": self.dead_seed_max_length_r_h, 
                            "abnormal_seed_max_length":self.abnormal_seed_max_length_r_h, 
                            "normal_seed_max_length":self.normal_seed_max_length_r_h, 
                            "no_of_segments_each_skeleton":self.n_segments_each_skeleton,
                            "weights_factor_growth_Pc":self.weights_factor_growth_Pc, 
                            "weights_factor_uniformity_Pu":self.weights_factor_uniformity_Pu,
                            "thresh_avg_max_radicle_thickness":self.thres_avg_max_radicle_thickness,
                            "average_seed_total_length":self.average_seed_total_length,
                            'hmin_head':self.hsv_values_seed_heads[0],
                            'hmax_head':self.hsv_values_seed_heads[1],
                            'smin_head':self.hsv_values_seed_heads[2],
                            'smax_head':self.hsv_values_seed_heads[3],
                            'vmin_head':self.hsv_values_seed_heads[4],
                            'vmax_head':self.hsv_values_seed_heads[5],
                            'hmin_body':self.hsv_values_seed[0],
                            'hmax_body':self.hsv_values_seed[1],
                            'smin_body':self.hsv_values_seed[2],
                            'smax_body':self.hsv_values_seed[3],
                            'vmin_body':self.hsv_values_seed[4],
                            'vmax_body':self.hsv_values_seed[5],
                            'factor_pixel_to_cm':self.pixel_per_cm
                            
                            }

        self.save_settings_to_file()
        ut.showdialog("Default settings restored successfully!!!")

    def set_pixel_cm_values(self):
        """Function to upload caliberation image"""

        # 1. upload image with square box printed over it
        # 2. extract square and 
        qWid = QWidget()
        print("Select measurements caliberation image")
        filepath, _ = QFileDialog.getOpenFileName(qWid, 'Select measurements caliberation image','',"Image files (*.jpg)")
        if not os.path.exists(filepath):
            ut.showdialog("Please select a file")
        else:
            img = cv2.imread(filepath)
            
            self.pixel_per_cm = get_pixel_to_cm(img)

            print("Pixels per centimeter is :", self.pixel_per_cm)
            cv2.imshow('img', img)
            self.dict_settings['factor_pixel_to_cm'] = self.pixel_per_cm
            # cv2.waitKey(-1)
            print("self.dict_settings['factor_pixel_to_cm']", self.dict_settings['factor_pixel_to_cm'])
            self.save_settings_to_file()

    def import_settings(self):
        
        qWid = QWidget()
        print("file browse")
        filepath,_ = QFileDialog.getOpenFileName(qWid, 'Select File', "","Json File (*.json)")        
        print(filepath)
        if not os.path.exists(filepath):
            ut.showdialog("Please select a file")
        else:
            with open(filepath, 'r') as f:
                data = f.read()
                self.dict_settings = json.loads(data)

    def export_settings(self):
        self.saveFileDialog()

    def set_configuration(self):
        pass

    def saveFileDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filePath, _ = QFileDialog.getSaveFileName(self,"Save Settings file","","Json File (*.json)", options=options)
        if filePath:
            print(filePath)
            if filePath[-5:] != ".json":
                filePath+=".json"

            with open(filePath, 'w+') as f:
                json.dump(self.dict_settings, f)
        
            ut.showdialog("Settings file exported successfully!!")
        else:
            ut.showdialog("Please select file to export settings.")
    
    def get_selected_row(self):
        index = self.tableView_res.selectedIndexes()[0]
        # id_us = int(self.tableView_res.model().data(index).toString())
        # print ("index : " + str(id_us)) 
        print('selected_index',index.row())
        # seedEditorObj = SeedEditor(self)
        
        seedObjSelected = self.mainProcessor.SeedObjList[index.row()]
        self.seedEditorObj.setSeedObj(seedObjSelected)
        seedIndex=index.row()
        self.seedEditorObj.setSeedIndex(seedIndex)
        
        # ut.show_cv2_img_on_label_obj(uiObj= self.seedEditorObj.label_img_seed ,img = seedObjSelected.cropped_seed_color)
        try:
            self.seedEditorObj.update_values()
        except Exception as e:
            print(traceback.format_exc())
        try:
            self.window = self.seedEditorObj
            self.window.show()
            print("window shown")
        except Exception as e:
            print(traceback.format_exc())
        
        

        # cv2.imshow(f"Seed {index.row()}",self.mainProcessor.SeedObjList[index.row()].cropped_seed_color)
        # cv2.waitKey(-1)
        # indexes = self.tableView_res.selectionModel().selectedRows()
        # for index in sorted(indexes):
        #     print('Row %d is selected' % index.row())

    def summarize_results(self):
        """"""
        print("Recalculating batchObj after edits...")
        batchAnalyserObj = self.batchAnalyzerObjList[self.currentImgIndex]
        batchAnalyserObj.recalculate_all_metrics()

            
        self.show_analyzed_results()

    def set_file_name(self):
            
        if len(self.imagePaths)>0:
            imgfilePath = self.imagePaths[self.currentImgIndex]
            imgName = os.path.basename(imgfilePath)
            self.label_fileName.setText(imgName)

    def change_settings(self):
        self.window = GlobalSettings(self)
        self.window.show()
    
    def read_settings(self):

        # self.dict_settings = {}
        with open(self.settings_json_file_path, 'r') as f:
            data = f.read()
            self.dict_settings = json.loads(data)
                

        # print('dict_values',dict_values)
        self.dead_seed_max_length_r_h = self.dict_settings['dead_seed_max_length']
        self.abnormal_seed_max_length_r_h = self.dict_settings['abnormal_seed_max_length']
        self.normal_seed_max_length_r_h = self.dict_settings["normal_seed_max_length"]
        self.n_segments_each_skeleton = self.dict_settings["no_of_segments_each_skeleton"]
        self.weights_factor_growth_Pc = self.dict_settings["weights_factor_growth_Pc"]
        self.weights_factor_uniformity_Pu = self.dict_settings["weights_factor_uniformity_Pu"]

        
        # with open(self.settings_hsv_path, 'r') as f:
        #     reader = csv.reader(f)
            
        #     for key, head_body,value in reader:
                
        #         if head_body=='head':
        #             object_to_save = self.hsv_values_seed_heads
        #         elif head_body=='body':
        #             object_to_save = self.hsv_values_seed
                
        #         index_value = self.list_hsv_keys.index(key)
        #         object_to_save[index_value] = int(value)
        
        self.apply_new_hsv_values()
                       
    def apply_new_hsv_values(self):
        print("Applying new hsv values head :", self.hsv_values_seed_heads)
        self.mainProcessor.hsv_values_seed = self.hsv_values_seed
        self.mainProcessor.hsv_values_seed_heads = self.hsv_values_seed_heads

    def set_hsv_values(self):
        # if len(self.imagePaths)>0:
        self.window = SetHSV(self)
        self.window.show()
        # else:
        #     ut.showdialog("Please select a image folder before.. and then you can change HSV values")

    def give_inputs(self):
        # QtWidgets.QInputDialog.setStyleSheet()
        inputDialog = QtWidgets.QInputDialog()
        inputDialog.setStyleSheet("""font: 63 10pt "Segoe UI Semibold";""")
        self.cultivatorName, done1 = inputDialog.getText(
             self, 'Inputs', 'Enter cultivar name:') 
        self.analystsName, done2 = inputDialog.getText(
           self, 'Inputs', 'Enter Analysts name:')
        self.batchNo, done3 = inputDialog.getInt(
           self, 'Inputs', 'Enter Lot no:') 
        self.n_seeds, done4 = inputDialog.getInt(
           self, 'Inputs',  'Enter no of seeds :', value=1, min=1)
        
        if self.n_seeds < 1:
            ut.showdialog("No of seeds cannot be less than 1. Please select proper value.")
            self.n_seeds, done4 = inputDialog.getInt(
                    self, 'Inputs', 'Enter no of seeds :')
        if done1 and done2 and done3:
            self.label_cult_name.setText(str(self.cultivatorName))
            self.label_analys_name.setText(str(self.analystsName))
            self.label_batchNo.setText(str(self.batchNo))
            self.label_n_plants.setText(str(self.n_seeds))
            
    def save_settings_to_file(self):
        print("Saving in settings file...")
        try:
            os.remove(self.settings_json_file_path)
    
        except Exception as e:
            print(e)
        # with open(self.settings_file_path, 'a+', newline="") as f:
        #     csvWriter = csv.writer(f)                    
        #     print("self.dead_seed_max_length_r_h", self.dead_seed_max_length_r_h)
        #     self.list_inputs = [self.dead_seed_max_length_r_h, self.abnormal_seed_max_length_r_h, 
        #             self.normal_seed_max_length_r_h, self.n_segments_each_skeleton, 
        #             self.weights_factor_growth_Pc, self.weights_factor_uniformity_Pu]
        #     for i in range(len(self.list_inputs)):
        #         list_each = [self.list_inputs_names[i], self.list_inputs[i]]
        #         csvWriter.writerow(list_each)

        with open(self.settings_json_file_path,'w+') as f:
            json.dump(self.dict_settings, f)
    
    def save_hsv_settings_to_file(self):
        print("Saving HSV settings in file...")
        try:
            os.remove(self.settings_hsv_path)
    
        except Exception as e:
            print(e)
        with open(self.settings_hsv_path, 'a+', newline="") as f:
            csvWriter = csv.writer(f)                    
            for i in range(len(self.hsv_values_seed_heads)):
                list_each = [self.list_hsv_keys[i], "head", self.hsv_values_seed_heads[i]]
                csvWriter.writerow(list_each)
            for i in range(len(self.hsv_values_seed)):
                list_each = [self.list_hsv_keys[i], "body", self.hsv_values_seed[i]]
                csvWriter.writerow(list_each)
      
    def create_settings_if_not_present(self):
        # if not os.path.exists(self.settings_file_path):
        #     self.save_settings_to_file()
        # if not os.path.exists(self.settings_hsv_path):
        #     self.save_hsv_settings_to_file()
        if not os.path.exists(self.settings_json_file_path):
            with open(self.settings_json_file_path,'w+') as f:
                json.dump(self.dict_settings, f)
    

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
        if len(self.imagePaths)>0:
            ## NOTE: uncomment this 
            # self.give_inputs()

            self.output_dir = os.path.join(self.input_folder_path, str(self.batchNo))
            self.output_results_dir = os.path.join(self.output_dir, 'results')
            self.output_images_dir = os.path.join(self.output_dir, 'processed_images')

            os.makedirs(self.output_dir, exist_ok=True)
            os.makedirs(self.output_results_dir, exist_ok=True)
            os.makedirs(self.output_images_dir, exist_ok=True)


            self.process_img_and_display_results()
            # self.showImg()
            # self.output_dir = self.input_folder_path
            # self.process_img_and_display_results()
        else:
            ut.showdialog("This folder does not contain any image file. Please choose another one..")

        return self.input_folder_path

    def check_if_all_valid_inputs(self):       

        validated = True
        for inputs in self.list_inputs:
            if inputs >=0:
                pass
            else:
                validated=False
        
        return validated

    def save_results_to_csv(self):
        current_file_name = os.path.basename(self.imagePaths[self.currentImgIndex])
        print("saving results to ",current_file_name)
        ext = current_file_name.split(".")[-1]
        ext_len = len(ext) + 1
        fileNameWoExt = current_file_name[:-1 * ext_len]

        outCsvFileName = fileNameWoExt + ".csv"
        output_result_csv_path = os.path.join(self.output_results_dir, outCsvFileName)
        datetime_now = datetime.today()
        date = datetime_now.date
        date_str = datetime_now.strftime("%d-%m-%y")
        try:
            os.remove(output_result_csv_path)
        except Exception as e:
            pass
        
        batchAnalyserObj = self.batchAnalyzerObjList[self.currentImgIndex]
        
        with open(output_result_csv_path, 'a+', newline="") as f:
            writer = csv.writer(f)
            line0 = ['SEP=,']
            line1 = ["ProSeedling Software"]
            line2 = ["Cultivar", "Lot number", "Number of seeds", "Analyst", "Date"]
            line3 = [self.cultivatorName, self.batchNo, self.n_seeds, self.analystsName, date_str]
            line4 = []
            line5 = ["Seedling", 'hypocotyl', 'root', 'Total length', 'hypocotyl/root ratio']
            line_list1 = [line0, line1, line2, line3, line4, line5]
            writer.writerows(line_list1)
            
            for line in self.data_each_seed:
                writer.writerow(line)
         
            lineBlank = []
            line6 = ['Vigor Index', 'Growth', 'Uniformity', 'Germination', 'Average length', 'Standard deviation',
                        'Normal Seedlings', 'Abnormal Seedlings', 'Non germinated seeds']
            line7 = [self.seed_vigor_index, self.growth, self.uniformity, f"{self.germination_percent} %",self.avg_length, self.std_deviation,
                     self.count_germinated_seeds, self.count_abnormal_seeds, self.count_dead_seeds]

            writer.writerows([lineBlank, line6, line7])
            
            
            # data_pandas = pd.DataFrame([data], columns = ['Seedling No', 'Hypercotyl length', 'Radicle length', 'Total length'])

            self.model = TableModel(self.data_each_seed)
            self.model.columns=['Seedling', 'Hypocotyl (cm)', 'Root (cm)', 'Total (cm)', 'Hypocotyl/root ratio']
            self.tableView_res.setModel(self.model)

    def show_analyzed_results(self):
        batchAnalyserObj = self.batchAnalyzerObjList[self.currentImgIndex]
        if batchAnalyserObj is not None:
            self.data_each_seed = []
            for i, seedObj in enumerate(batchAnalyserObj.seedObjList):
                line = [i+1, seedObj.hyperCotyl_length_cm, seedObj.radicle_length_cm, seedObj.total_length_cm, seedObj.ratio_h_root]
                self.data_each_seed.append(line)

                # writer.writerow(line)
                # total_lengths+= seedObj.total_length_pixels
                # list_total_lengths.append(seedObj.total_length_pixels)
            
            self.std_deviation = batchAnalyserObj.std_deviation
            self.growth = round(batchAnalyserObj.growth,2)

           
            self.penalization = round(batchAnalyserObj.penalization,2)
            self.uniformity = round(batchAnalyserObj.uniformity,2)
            self.seed_vigor_index = round(batchAnalyserObj.seed_vigor_index,2)

            self.count_abnormal_seeds = batchAnalyserObj.abnormal_seed_count
            self.count_dead_seeds = batchAnalyserObj.dead_seed_count
            self.count_germinated_seeds = batchAnalyserObj.germinated_seed_count
            self.germination_percent = round(batchAnalyserObj.germination_percent,2)
            
            self.label_growth.setText(str(self.growth))
            self.label_sd.setText(str(self.std_deviation))
            self.label_uniformity.setText(str(self.uniformity))
            self.label_seedvigor.setText(str(self.seed_vigor_index))
            self.label_germination.setText(f"{round(batchAnalyserObj.germination_percent,2)} %")
            self.label_avg_hypocotyl.setText(str(batchAnalyserObj.avg_hypocotyl_length))
            self.label_avg_root.setText(str(batchAnalyserObj.avg_root_length))
            self.label_avg_total_length.setText(str(batchAnalyserObj.avg_total_length))

            self.model = TableModel(self.data_each_seed)
            self.model.columns=['Seedling', 'Hypocotyl', 'Root', 'Total', 'Hypocotyl/root ratio']
            self.tableView_res.setModel(self.model)


    def process_img_and_display_results(self):
        
        if self.check_if_all_valid_inputs():

            ## Process for main
            imgPath = self.imagePaths[self.currentImgIndex]
            self.list_hypercotyl_radicle_lengths, colorImg, batchAnalyzerObj = self.mainProcessor.process_main(imgPath)
            self.batchAnalyzerObjList[self.currentImgIndex] = batchAnalyzerObj


            self.std_deviation = batchAnalyzerObj.std_deviation
            self.growth = round(batchAnalyzerObj.growth,2)


            ## save output image
            try:
                os.makedirs(self.output_images_dir, exist_ok=True)
            except Exception as e:
                pass
            output_img_path = os.path.join(self.output_images_dir, os.path.basename(self.imagePaths[self.currentImgIndex]))
            cv2.imwrite(output_img_path, colorImg)

            self.showResultImg(colorImg)
            
        total_lengths = 0
        list_total_lengths = []
        self.data_each_seed = []

        # for i in range(len(self.list_hypercotyl_radicle_lengths)):
        #     hyp, rad = self.list_hypercotyl_radicle_lengths[i]
        #     seed_length = hyp + rad
        #     ratio_h_root = round(hyp/rad, 2) if rad>0 else 'NA'
        #     line = [i+1, hyp, rad, seed_length,  ratio_h_root]

        for i, seedObj in enumerate(batchAnalyzerObj.seedObjList):
            line = [i+1, seedObj.hyperCotyl_length_cm, seedObj.radicle_length_cm, seedObj.total_length_cm, seedObj.ratio_h_root]
            self.data_each_seed.append(line)

            # writer.writerow(line)
            total_lengths+= seedObj.total_length_pixels
            list_total_lengths.append(seedObj.total_length_pixels)
        
        
        self.avg_length = total_lengths / self.n_seeds
        total_length_array = np.array(list_total_lengths)
        
        

        self.show_analyzed_results()


        self.save_results_to_csv()

    def loadNextImg(self):
        if self.currentImgIndex<len(self.imagePaths)-1:
            self.currentImgIndex+=1
            self.showImg()
            self.process_img_and_display_results()
    
    def loadPrevImg(self):
        if self.currentImgIndex>=1:
            self.currentImgIndex-=1
            self.showImg()
            self.process_img_and_display_results()

    def load_images(self):
        imgExtensions = ['jpg', 'jpeg','png','bmp','tiff']
        if self.input_folder_path is not None and len(self.input_folder_path)>1:
            files = os.listdir(self.input_folder_path)
            
            self.imagePaths = [os.path.join(self.input_folder_path, fileName) for fileName in files if fileName.split(".")[-1].lower() in imgExtensions]

        self.batchAnalyzerObjList = [None] *len(self.imagePaths)

    def showImg(self):

        if len(self.imagePaths)>0:
            imgPath = self.imagePaths[self.currentImgIndex]
            # ut.apply_img_to_label_object(imgPath, self.imgLabel)
            self.viewer.setPhoto(QtGui.QPixmap(imgPath))
            imgNo = self.currentImgIndex + 1
            total_images = len(self.imagePaths)
            self.label_img_no.setText(f"{imgNo} / {total_images}")

        self.set_file_name()
    
    def showResultImg(self, imgNumpy):
        h, w, ch = imgNumpy.shape
        bytesPerLine = 3 * w
        qImg = QImage(imgNumpy.data, w, h, bytesPerLine, QImage.Format_RGB888)
        self.pixmap = QtGui.QPixmap.fromImage(qImg)
        # self.imgLabel.setPixmap(self.pixmap)
        self.viewer.setPhoto(self.pixmap)
  
    
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


class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data
        self.columns = []

    
    def data(self, index, role):
        if role == Qt.DisplayRole:
            # See below for the nested-list data structure.
            # .row() indexes into the outer list,
            # .column() indexes into the sub-list
            return self._data[index.row()][index.column()]

    def rowCount(self, index):
        # The length of the outer list.
        return len(self._data)

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return len(self._data[0])

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...):
        if orientation==QtCore.Qt.Horizontal and role==QtCore.Qt.DisplayRole:
            return self.columns[section]
        return super().headerData(section, orientation, role)
    

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    w.setWindowTitle("ProSeedling Software")
    w.setWindowIcon(QtGui.QIcon(r'resources/ProSeedling_logo_cropped.png'))
    sys.exit(app.exec())
    