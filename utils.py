import cv2
import numpy as np

def get_HSV_mask(img, hsv_values):
    hmin, hmax, smin, smax, vmin, vmax =hsv_values

    hsvImg = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    lower = np.array([hmin, smin, vmin])
    upper = np.array([hmax, smax, vmax])

    maskHSV = cv2.inRange(hsvImg, lower, upper)

    return maskHSV

def get_Concat_img_with_hsv_mask(img, hsvMask1Ch):
    mask3ch = cv2.merge((hsvMask1Ch, hsvMask1Ch, hsvMask1Ch))
    maskConcat = np.hstack((img, mask3ch))
    return maskConcat