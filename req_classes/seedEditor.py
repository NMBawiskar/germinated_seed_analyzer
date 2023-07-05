from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import  QWidget, QLabel
from PyQt5.uic import loadUi
from utils_pyqt5 import showdialog, show_cv2_img_on_label_obj
from utils import *
from req_classes.contour_processor import Seed
from proj_settings import SeedHealth
from PIL import Image
from PIL.ImageQt import ImageQt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtGui import QPainter, QColor, QFont
from PyQt5.QtCore import Qt, QPoint

def QImageToCvMat(incomingImage):
    '''  Converts a QImage into an opencv MAT format  '''

    incomingImage = incomingImage.convertToFormat(QtGui.QImage.Format.Format_RGBA8888)

    width = incomingImage.width()
    height = incomingImage.height()

    ptr = incomingImage.bits()
    ptr.setsize(height * width * 4)
    arr = np.frombuffer(ptr, np.uint8).reshape((height, width, 4))
    return arr

class CanvasLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.text = "Custom Canvas"
        self.background_color = QColor(0, 255, 0)
        self.x = 50
        self.y = 30
        self.w = 301
        self.h = 781
        self.seedEditor = None
        self.setGeometry(self.x,self.y,self.w,self.h)
        self.imgW = 0
        self.imgH = 0
        self.margin_x = 0
        self.margin_y = 0
        self.eraserActive = False
        self.breakPointActive = False

        self.canvasMask = None
        self.last_x, self.last_y = None, None
        self.pen_draw_color = [0,255,0]
        self.pen_thickness= 2
        self.pen_color_mask = QtGui.QColor('black')
        
        # self.seedObj = seedObj
        
        # self.setScaledContents(True)
        self.updated_img = None

    def apply_cv2_image(self, imgcv2):
        self.imgH, self.imgW = imgcv2.shape[:2]
        rgb_image = cv2.cvtColor(imgcv2, cv2.COLOR_BGR2RGB)
        PIL_image = Image.fromarray(rgb_image).convert('RGB')
        # imMask = ImageQt(PIL_image).copy()
        # self.canvasMask= QtGui.QPixmap.fromImage(imMask)
        # self.setPixmap(QPixmap.fromImage(ImageQt(imMask)))
        self.canvasMask = QPixmap.fromImage(ImageQt(PIL_image))  
        self.setPixmap(self.canvasMask)

        delta_x = self.w - self.imgW
        delta_y = self.h - self.imgH
        if delta_x >0:
            #img is smaller in width
            self.margin_x = delta_x / 2

        if delta_y > 0:
            self.margin_y = delta_y / 2

    def mouseMoveEvent(self, a0: QtGui.QMouseEvent) -> None:
        # print("ev", a0.x(), a0.y())
        
        if self.last_x is None:
            self.last_x = int((a0.x()) / self.w * self.imgW) 
            self.last_y = int((a0.y()) / self.h * self.imgH) 
                      
            return # ignore the first frame


        self.drawX = int((a0.x()) / self.w * self.imgW) 
        self.drawY = int((a0.y()) / self.h * self.imgH)


        if self.breakPointActive:
            ## find closest point on contour 

            ## Reload pixmap
            # Load skeletonized mask for editing
            rgb_image = cv2.cvtColor(self.seedObj.skeltonized, cv2.COLOR_BGR2RGB)
            imgPilMask = Image.fromarray(rgb_image).convert('RGB')        
            imMask = ImageQt(imgPilMask).copy()
            self.canvasMask= QtGui.QPixmap.fromImage(imMask)
            self.setPixmap(QPixmap.fromImage(ImageQt(imgPilMask)))
            painter = QtGui.QPainter(self.canvasMask)
            
            # SET PEN
            p = painter.pen()

            closest_point_cnt = find_closest_point(contour=self.seedObj.sorted_point_list, point = (self.drawY, self.drawX))
            self.pen_color_mask = QtGui.QColor('blue')
            p.setWidth(20)
            p.setColor(self.pen_color_mask)
            painter.setPen(p)
            qPoint = QPoint(closest_point_cnt[1], closest_point_cnt[0])
            painter.drawPoint(qPoint)
            painter.end()
            self.setPixmap(self.canvasMask)
            self.update()
            
            self.seedObj.reassign_points(new_break_point=closest_point_cnt)
            
            self.last_x = self.drawX
            self.last_y = self.drawY

        if self.eraserActive:

            ################ paint mask ###################
            rgb_image = cv2.cvtColor(self.seedObj.skeltonized, cv2.COLOR_BGR2RGB)
            imgPilMask = Image.fromarray(rgb_image).convert('RGB')        
            imMask = ImageQt(imgPilMask).copy()
            self.canvasMask= QtGui.QPixmap.fromImage(imMask)
            self.setPixmap(QPixmap.fromImage(ImageQt(imgPilMask)))
            
            painter = QtGui.QPainter(self.canvasMask)
           

            # SET PEN
            p = painter.pen()
            p.setWidth(self.pen_thickness)
            p.setColor(self.pen_color_mask)
            painter.setPen(p)
            
           

        
            painter.drawLine(self.last_x, self.last_y, self.drawX, self.drawY)
            painter.end()
            self.setPixmap(self.canvasMask)
            self.update()
            
                        
            self.seedObj.erase_points(point=[self.drawY, self.drawX])

            
            # update origin
            self.last_x = self.drawX
            self.last_y = self.drawY

        
        self.seedEditor.update_values()


        ################ paint mask ###################
        # painter = QtGui.QPainter(self.label_paint_area.pixmap())
        # painter = QtGui.QPainter(self.canvasMask)
       

        # # SET PEN
        # p = painter.pen()
        # p.setWidth(self.pen_thickness)
        # p.setColor(self.pen_color_mask)
        # painter.setPen(p)
        # # print('a0', a0.x(), a0.y())

        
        # self.drawX = int((a0.x()) / self.w * self.imgW) 
        # self.drawY = int((a0.y()) / self.h * self.imgH)
        # # self.drawX = int(a0.x() - self.delta_x)
        # # self.drawY = int(a0.y() - self.delta_y)

    
        # painter.drawLine(self.last_x, self.last_y, self.drawX, self.drawY)
        # painter.end()
        # self.setPixmap(self.canvasMask)
        # updatedQImg = self.pixmap().toImage()
        # self.updated_img = QImageToCvMat(updatedQImg)
        # self.seedObj.erase_points(point = [self.drawY, self.drawX])
        # self.update()
        # self.seedEditor.update_values()


        # self.last_x = self.drawX
        # self.last_y = self.drawY

        return super().mouseMoveEvent(a0)


class SeedEditor(QWidget):
    def __init__(self, mainUi):
        super().__init__()
        loadUi(r'UI_files\seed_editor.ui', self)
        self.mainUi = mainUi
        self.setWindowIconText("Seed ")
        self.btngroup1 = QtWidgets.QButtonGroup()


        self.eraserActive = False
        self.breakPointActive = False
        self.seedObj:Seed = None
        self.seedNo = 0
        

        self.btngroup1.addButton(self.radioBtnNormalSeed)
        self.btngroup1.addButton(self.radioBtnAbnormalSeed)
        self.btngroup1.addButton(self.radioBtnDeadSeed)

        self.radioBtnNormalSeed.toggle()
        self.radioBtnNormalSeed.toggled.connect(self.checkRadio)
        self.radioBtnAbnormalSeed.toggled.connect(self.checkRadio)
        self.radioBtnDeadSeed.toggled.connect(self.checkRadio)

        self.radioBtnNormalSeed.setShortcut('n')
        self.radioBtnAbnormalSeed.setShortcut('a')
        self.radioBtnDeadSeed.setShortcut('d')

        self.btnEraser.setShortcut('e')
        self.btnPoint.setShortcut('b')
        # self.btnPen.setShortcut('p')

        self.btnEraser.clicked.connect(self.use_eraser)
        self.btnPoint.clicked.connect(self.use_breakPoint)
        # self.btnPen.clicked.connect(self.use_pen)
        self.btnSave.clicked.connect(self.save_changes)

        self.canvasMask=None
        self.last_x, self.last_y = None, None
        self.pen_draw_color = [0,255,0]
        self.pen_thickness= 2
        self.pen_color_mask = QtGui.QColor('white')
        self.imgH = 0
        self.imgW = 0

        self.delta_x=390 
        self.delta_y=30
        # self.label_paint_w = 301  ## To set afterwards
        # self.label_paint_h = 781  ## To set afterwards

        self.customLabel = CanvasLabel(self)
        self.customLabel.seedEditor = self
        self.customLabel.show()
        

    def save_changes(self):
        print("saving changes")
        self.customLabel.canvasMask.save('customCanvas.png')
        imgUpdated = cv2.imread('customCanvas.png')
        self.seedObj.skeltonized = imgUpdated
        # cv2.imshow('updatedQIMG',self.seedObj.skeltonized)
        # cv2.imshow('self.customLabel.updated_img',self.customLabel.updated_img)
        # cv2.waitKey(1)
        self.close()

    def use_eraser(self):
        print("Eraser clicked")
        self.pen_color_mask = QtGui.QColor('black')
        self.eraserActive=True
        self.breakPointActive=False
        self.customLabel.breakPointActive=False
        self.customLabel.eraserActive=True
    
    def use_breakPoint(self):
        print("Breakpoint clicked")
        # self.pen_color_mask = QtGui.QColor('black')
        self.eraserActive=False
        self.breakPointActive=True
        print(f"Initial hyperCotyl_length_pixels , radicle_length_pixels : {self.seedObj.hyperCotyl_length_pixels}, {self.seedObj.radicle_length_pixels}")
        self.customLabel.breakPointActive=True
        self.customLabel.eraserActive=False

    def use_pen(self):
        print("Pen clicked")
        self.pen_color_mask = QtGui.QColor('white')

    def display_mask(self):
        cv2.imshow('mask_skeleton', self.seedObj.skeltonized)
        # cv2.imshow('mask_head', self.seedObj.cropped_head_binary)
        cv2.waitKey(1)

    def checkRadio(self):
        if self.radioBtnNormalSeed.isChecked():
            print("radio NormalSeed is checked")
            self.seedObj.seed_health = SeedHealth.NORMAL_SEED
            
        elif self.radioBtnAbnormalSeed.isChecked():
            print("radio Abnormal is checked")
            self.seedObj.seed_health = SeedHealth.ABNORMAL_SEED
            
        
        elif self.radioBtnDeadSeed.isChecked():
            print('radio Dead Seed is checked')
            self.seedObj.seed_health = SeedHealth.DEAD_SEED

        self.mainUi.summarize_results()
        self.update_values()

    def setColorPixmap(self):
        # Load skeletonized mask for editing
        rgb_image = cv2.cvtColor(self.seedObj.cropped_seed_color, cv2.COLOR_BGR2RGB)
        imgPilMask = Image.fromarray(rgb_image).convert('RGB')        
        imMask = ImageQt(imgPilMask).copy()
        # self.canvasMask= QtGui.QPixmap.fromImage(imMask)
        self.label_img_seed_mask.setPixmap(QPixmap.fromImage(ImageQt(imgPilMask)))

    def setSeedObj(self,seedObj):
        self.seedObj = seedObj
   


        self.imgH, self.imgW = self.seedObj.skeltonized.shape[:2]
        print(self.imgH, self.imgW)
        # self.label_paint_h = self.imgH
        # self.label_paint_w = self.imgW 

        self.customLabel.w = self.imgW
        self.customLabel.h = self.imgH
        self.customLabel.seedObj = seedObj
        self.customLabel.setGeometry(self.customLabel.x, self.customLabel.y, self.customLabel.w, self.customLabel.h)
        self.customLabel.apply_cv2_image(self.seedObj.skeltonized)


        self.label_img_seed_mask.setGeometry(self.delta_x, self.customLabel.y, self.customLabel.w, self.customLabel.h)
        print('set geometry for color label')
        # Load cropped_seed_color mask for editing
        rgb_image = cv2.cvtColor(self.seedObj.cropped_seed_color, cv2.COLOR_BGR2RGB)
        imgPilMask = Image.fromarray(rgb_image).convert('RGB')        
        imMask = ImageQt(imgPilMask).copy()
        self.canvasMask= QtGui.QPixmap.fromImage(imMask)
        self.label_img_seed_mask.setPixmap(QPixmap.fromImage(ImageQt(imgPilMask)))
        print('set pixmap color')

        # self.display_mask()

    def setSeedIndex(self, seedIndex):
        self.seedNo = seedIndex + 1
        print('set seed index no', self.seedNo)

    def update_values(self):
        
        self.label_seed_no.setText(str(self.seedNo))
        self.label_hypocotyl_length.setText(str(self.seedObj.hyperCotyl_length_pixels))
        self.label_root_length.setText(str(self.seedObj.radicle_length_pixels))
        self.label_total_length.setText(str(self.seedObj.total_length_pixels))
        self.label_seed_health.setText(self.seedObj.seed_health)

        self.setColorPixmap()

        self.mainUi.show_analyzed_results()
    """
    def mouseMoveEvent(self, a0: QtGui.QMouseEvent) -> None:
        if self.last_x is None:
            
            self.last_x = int((a0.x() - self.delta_x) / self.label_paint_w * self.imgW) 
            self.last_y = int((a0.y() - self.delta_y) / self.label_paint_h * self.imgH) 
            # self.last_x = int(a0.x() - self.delta_x)
            # self.last_y = int(a0.y() - self.delta_y)
            return # ignore the first frame
        
        self.drawX = int((a0.x() - self.delta_x) / self.label_paint_w * self.imgW) 
        self.drawY = int((a0.y() - self.delta_y) / self.label_paint_h * self.imgH) 
        
        
        
        


        if self.breakPointActive:
            ## find closest point on contour 

            ## Reload pixmap
            # Load skeletonized mask for editing
            rgb_image = cv2.cvtColor(self.seedObj.skeltonized, cv2.COLOR_BGR2RGB)
            imgPilMask = Image.fromarray(rgb_image).convert('RGB')        
            imMask = ImageQt(imgPilMask).copy()
            self.canvasMask= QtGui.QPixmap.fromImage(imMask)
            self.customLabel.setPixmap(QPixmap.fromImage(ImageQt(imgPilMask)))
            painter = QtGui.QPainter(self.canvasMask)
            
            # SET PEN
            p = painter.pen()

            closest_point_cnt = find_closest_point(contour=self.seedObj.sorted_point_list, point = (self.drawY, self.drawX))
            self.pen_color_mask = QtGui.QColor('blue')
            p.setWidth(20)
            p.setColor(self.pen_color_mask)
            painter.setPen(p)
            qPoint = QPoint(closest_point_cnt[1], closest_point_cnt[0])
            painter.drawPoint(qPoint)
            painter.end()
            self.customLabel.setPixmap(self.canvasMask)
            self.update()

            self.seedObj.reassign_points(new_break_point=closest_point_cnt)
            self.setColorPixmap()
            self.last_x = self.drawX
            self.last_y = self.drawY
            
        
        if self.eraserActive:

            ################ paint mask ###################
            
            painter = QtGui.QPainter(self.canvasMask)
           

            # SET PEN
            p = painter.pen()
            p.setWidth(self.pen_thickness)
            p.setColor(self.pen_color_mask)
            painter.setPen(p)
            
            # print('a0', a0.x(), a0.y())


            # self.drawX = int((a0.x() - self.delta_x) / self.label_paint_w * self.imgW) 
            # self.drawY = int((a0.y() - self.delta_y) / self.label_paint_h * self.imgH) 
            # self.drawX = int(a0.x() - self.delta_x)
            # self.drawY = int(a0.y() - self.delta_y)

        
            painter.drawLine(self.last_x, self.last_y, self.drawX, self.drawY)
            painter.end()
            self.label_img_seed_mask.setPixmap(self.canvasMask)
            self.update()
            
            
            ################ paint MainImg ###################

            # painter1 = QtGui.QPainter(self.canvas)
        

            # # SET PEN
            # p1 = painter1.pen()
            # p1.setWidth(self.pen_thickness)
            # p1.setColor(self.pen_color_img)
            # # painter1.setBrush(QtGui.QColor(0, 255, 0, 200))
            # painter1.setPen(p1)

            # self.drawX = int(a0.x() / self.label_paint_w * self.imgW)
            # self.drawY = int(a0.y() / self.label_paint_h * self.imgH)

        
            # painter1.drawLine(self.last_x, self.last_y, self.drawX, self.drawY)
            # painter1.end()
            # # self.label_img_org.setPixmap(self.canvas)
            # self.update()
            
            self.seedObj.erase_points(point=[self.drawY, self.drawX])

            self.setColorPixmap()
            # update origin
            self.last_x = self.drawX
            self.last_y = self.drawY


        self.update_values()

        return super().mouseMoveEvent(a0)
    """
    # def mouseReleaseEvent(self, a0: QtGui.QMouseEvent) -> None:
    #     self.last_x = None
    #     self.last_y = None

    #     return super().mouseReleaseEvent(a0)