import os
from PyQt5 import QtCore, QtGui, QtWidgets
from PIL.ImageQt import ImageQt
from PIL import Image
from PyQt5.QtWidgets import QWidget, QFileDialog
from PyQt5.QtGui import QImage, QPixmap


def create_directory(path):
    try:
        os.mkdir(path)
    except Exception as e:
        print(e)
    
def showdialog(message_txt):
    msg = QtWidgets.QMessageBox()
    msg.setIcon(QtWidgets.QMessageBox.Information)
    msg.setText(message_txt)        
    msg.setWindowTitle("Info")             
    retval = msg.exec_()

def apply_img_to_label_object(imgPath, labelObject):
    imgPil = Image.open(imgPath)
    # imgPil_resized = imgPil.resize((266,150))
    im = ImageQt(imgPil).copy()
    pixmap = QtGui.QPixmap.fromImage(im)
    labelObject.setPixmap(pixmap)

def show_cv2_img_on_label_obj(uiObj, img):
    qformat = QImage.Format_BGR888
    img = QImage(img, img.shape[1], img.shape[0], qformat)
    uiObj.setPixmap(QPixmap.fromImage(img))

def browse_folder(self):
    qWid = QWidget()
    print("file browse")
    path_folder = QFileDialog.getExistingDirectory(qWid, 'Select folder', '')        
    return path_folder
