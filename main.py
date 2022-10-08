import cv2
import os
import numpy as np
from contour_processor import ContourProcessor
from utils import *

def display_img(title,img):
    cv2.namedWindow(title,cv2.WINDOW_NORMAL)
    cv2.imshow(title,img)

def main(img_path):
    imageName = os.path.basename(img_path)
    img = cv2.imread(img_path)
    result = img.copy()

    ############### 1. get seed head masks
    hsv_values_seed_heads = 0,127,0,255,0,34 
    hsvMask_seed_heads = get_HSV_mask(img, hsv_values=hsv_values_seed_heads)    
    maskConcat = get_Concat_img_with_hsv_mask(img, hsvMask_seed_heads)
    display_img('Result_heads', maskConcat)

    ############### 1. get seed head masks
    hsv_values_seed = 0,127,0,255,0,172
    hsvMask_seed = get_HSV_mask(img, hsv_values=hsv_values_seed)    
    maskConcatSeed = get_Concat_img_with_hsv_mask(img, hsvMask_seed)
    display_img('Result_seed', maskConcatSeed)

    contourProcessor = ContourProcessor(imgBinary=hsvMask_seed)
    result_cnt_drawn =contourProcessor.display_shortlisted_contours(imgColor=img)
    display_img('drawnContours', result_cnt_drawn)


    # display_img(f"Input_{imageName}",img)   
    # display_img(f"Result_{imageName}",maskConcat)
    cv2.waitKey(-1)
    


if __name__ == '__main__':
    folder_path = r'trial_images'
    images = os.listdir(folder_path)
    for image in images:
        img_path = os.path.join(folder_path,image)
        print(f"Processing image {image} ............")
        main(img_path)
    
        key = cv2.waitKey(-1)
        if key == ord('q'):
            break

        print("-"*40)
        cv2.destroyAllWindows()
    