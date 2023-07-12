import cv2
import numpy as np


def get_pixel_to_cm(img):
    imgLab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    values = (0,45,0,158,0,245)
    lower = np.array([0,0,0])
    upper = np.array([45,158,245])    
    mask = cv2.inRange(imgLab, lower, upper)

    # cv2.imshow('mask',mask)

    # cv2.waitKey(-1)
    contours, herirachy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    hImg, wImg = imgLab.shape[:2]
    wTotal = 0
    hTotal = 0
    count_box = 0
    
    for cnt in contours:
        area =  cv2.contourArea(cnt)
        if area >1000 and area<2500:
            print("box area",area)
            x,y,w,h = cv2.boundingRect(cnt)
            wTotal+=w
            hTotal+=h
            count_box+=1
    
    avgW = wTotal /count_box
    avgH = hTotal /count_box
    print("pixel per cm", avgW, avgH)
    pixel_per_cm = int((avgW+ avgH)/2)

    print("PIXEL_per_CM = ", pixel_per_cm)
    return pixel_per_cm

# imgPath = r"requirements_v2\WIN_20230420_10_24_19_Pro.jpg"

# img = cv2.imread(imgPath)
# pixel_per_cm = get_pixel_to_cm(img)