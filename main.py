import cv2
import os
import numpy as np
from contour_processor import ContourProcessor, Seed
from utils import *



def main(img_path):
    imageName = os.path.basename(img_path)
    img = cv2.imread(img_path)
    result = img.copy()

    ############### 1. get seed head masks
    hsv_values_seed_heads = 0,127,0,255,0,34 
    hsvMask_seed_heads = get_HSV_mask(img, hsv_values=hsv_values_seed_heads)    
    maskConcat = get_Concat_img_with_hsv_mask(img, hsvMask_seed_heads)
    # display_img('Result_heads', maskConcat)
    contourProcessor_heads = ContourProcessor(imgBinary=hsvMask_seed_heads)

    shortListed_headsContours = contourProcessor_heads.shortlisted_contours
    list_Head_centers = list(map(get_contour_center, shortListed_headsContours))
    print(list_Head_centers)


    # result_cnt_drawn_heads = contourProcessor_heads.display_shortlisted_contours(imgColor=img)
    # display_img('result_cnt_drawn_heads',result_cnt_drawn_heads)



    ############### 1. get seed head masks
    hsv_values_seed = 0,127,0,255,0,172
    hsvMask_seed = get_HSV_mask(img, hsv_values=hsv_values_seed)    
    maskConcatSeed = get_Concat_img_with_hsv_mask(img, hsvMask_seed)
    # display_img('Result_seed', maskConcatSeed)

    contourProcessor = ContourProcessor(imgBinary=hsvMask_seed)
   


    ####################### Check if contours contain heads ###############
    xywh_list = [cv2.boundingRect(cnt) for cnt in contourProcessor.shortlisted_contours]
    cropped_cnts_seeds = [cropImg(contourProcessor.binaryImgShortlistedCnt, tuple_xywh=xywh_tuple) for xywh_tuple in xywh_list]
    cropped_cnt_heads = [cropImg(contourProcessor_heads.binaryImgShortlistedCnt, tuple_xywh=xywh_tuple) for xywh_tuple in xywh_list]

    final_shortListedCnts = []


    xywh_list_final = []
    for i in range(len(xywh_list)):
        croppedCntSeed = cropped_cnts_seeds[i]
        # display_img("croppedCntSeed",croppedCntSeed)
        
        croppedCntHead = cropped_cnt_heads[i]
        resultIntersection = cv2.bitwise_and(croppedCntSeed, croppedCntHead)

        whiteCntsIntersection = np.sum(resultIntersection==255)
        if whiteCntsIntersection >10:
            final_shortListedCnts.append(contourProcessor.shortlisted_contours[i])
            xywh_list_final.append(xywh_list[i])


        comparison = np.hstack((croppedCntSeed, croppedCntHead, resultIntersection))
        # display_img("Comparison", comparison)
        # cv2.waitKey(-1)

    contourProcessor.shortlisted_contours = final_shortListedCnts    
    result_cnt_drawn =contourProcessor.display_shortlisted_contours(imgColor=img)
    display_img('drawnContours', result_cnt_drawn)
    contourProcessor.get_skeleton_img()

    ################## Creating SEED object list ##################
    SeedObjList = []
    for i in range(len(xywh_list_final)):
        SeedObject = Seed(xywh=xywh_list_final[i], imgBinarySeed=hsvMask_seed, 
            imgBinaryHeadOnly=contourProcessor_heads.binaryImgShortlistedCnt)

        SeedObjList.append(SeedObject)
        SeedObject.morph_head_img()
        SeedObject.skeletonize_root()
        SeedObject.make_offset()


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
    