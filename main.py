import cv2
import os
import numpy as np
from contour_processor import ContourProcessor, Seed
from utils import *
import csv
from dataAnalysis import BatchAnalysis

def main(img_path):
    imageName = os.path.basename(img_path)
    img = cv2.imread(img_path)
    result = img.copy()

    ############### INPUT parameters for tuning ##################
    n_segments_each_skeleton = 15           # divisions to make in each length (Increase this for finer results)
    thres_avg_max_radicle_thickness = 13    # avg thickness to distinguish radicle (tune this if camera position changes)
    dead_seed_max_length_r_h = 80
    abnormal_seed_max_length_r_h =  130
    normal_seed_max_length_r_h = 150

    weights_factor_growth_Pc = 0.7
    weights_factor_uniformity_Pu = 0.3

    ####################################################################


    ############### 1. get seed head masks
    hsv_values_seed_heads = 0,127,0,255,0,34 
    hsvMask_seed_heads = get_HSV_mask(img, hsv_values=hsv_values_seed_heads)    
    maskConcat = get_Concat_img_with_hsv_mask(img, hsvMask_seed_heads)
    # display_img('Result_heads', maskConcat)
    contourProcessor_heads = ContourProcessor(imgBinary=hsvMask_seed_heads, colorImg = result)

    shortListed_headsContours = contourProcessor_heads.shortlisted_contours
    list_Head_centers = list(map(get_contour_center, shortListed_headsContours))
    # print(list_Head_centers)





    ############### 1. get complete seed masks
    # hsv_values_seed = 0,127,0,255,0,172
    hsv_values_seed = 0,179,0,255,0,162
    hsvMask_seed = get_HSV_mask(img, hsv_values=hsv_values_seed)    
    maskConcatSeed = get_Concat_img_with_hsv_mask(img, hsvMask_seed)
    display_img('Result_seed', maskConcatSeed)

    contourProcessor = ContourProcessor(imgBinary=hsvMask_seed, colorImg = result)
   


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
    list_hypercotyl_radicle_lengths = []
    for i in range(len(xywh_list_final)):
        SeedObject = Seed(xywh=xywh_list_final[i], imgBinarySeed=hsvMask_seed, 
            imgBinaryHeadOnly=contourProcessor_heads.binaryImgShortlistedCnt,
            imgColor = contourProcessor.colorImg,
            n_segments_each_skeleton = n_segments_each_skeleton,
            thres_avg_max_radicle_thickness = thres_avg_max_radicle_thickness
            )

        SeedObjList.append(SeedObject)
        SeedObject.morph_head_img()
        SeedObject.skeletonize_root()
        # SeedObject.make_offset()
        SeedObject.analyzeSkeleton()
        list_hypercotyl_radicle_lengths.append([SeedObject.hyperCotyl_length_pixels,SeedObject.radicle_length_pixels])



    ######################### Batch analysis

    batchAnalyser = BatchAnalysis(img_path=img_path, batchNumber=batchNumber, 
                        list_hypercotyl_radicle_lengths=list_hypercotyl_radicle_lengths,
                        dead_seed_max_length_r_h=dead_seed_max_length_r_h, abnormal_seed_max_length_r_h=abnormal_seed_max_length_r_h,
                        normal_seed_max_length_r_h=normal_seed_max_length_r_h, weights_factor_growth_Pc=weights_factor_growth_Pc, 
                        weights_factor_uniformity_Pu=weights_factor_uniformity_Pu)

    batch_seed_vigor_index = batchAnalyser.seed_vigor_index


    print()   
    print("#"*50)
    print("FINAL RESULT FOR IMAGE", imageName)
    print("HYPERCOTYL AND RADICLE LENGTHS  ")
    print("RESULT",list_hypercotyl_radicle_lengths)
    print("#"*50)
    print("*"*50)
    print("Seed_vigor_index", batchAnalyser.seed_vigor_index)
    print("Growth", batchAnalyser.growth)
    print("Uniformity", batchAnalyser.uniformity)
    print("Germinated_seed_count", batchAnalyser.germinated_seed_count)
    print("Dead_seed_count", batchAnalyser.dead_seed_count)
    print("Abnormal_seed_count", batchAnalyser.abnormal_seed_count)
    print("*"*50)
    print()

    display_img("Result",contourProcessor.colorImg)
    cv2.waitKey(-1)
    return list_hypercotyl_radicle_lengths, contourProcessor.colorImg, batch_seed_vigor_index
    

def getInputs():
    cultivator_name = input("Please enter cultivator name : ")
    batchNumber = input("Please input batch number :")
    analysts_name = input("Please input analysts name :")
    n_plants = input("Please input number of plants :")
    folder_path = input("Please input folder path of images (default trial_images folder):")


    return cultivator_name, batchNumber, analysts_name, n_plants, folder_path



if __name__ == '__main__':

    cultivator_name, batchNumber, analysts_name, n_plants, folder_path = getInputs()
    outputDir = "output"
    try:

        os.mkdir(outputDir)
    except:
        pass

    if len(folder_path)>0:
        pass

    else:
        folder_path = r'trial_images'
    
    if os.path.exists(folder_path):
        pass
    else:
        print("Please provide correct folder path.")
        exit()


    images = os.listdir(folder_path)
    with open('Results.csv', 'w+',newline='') as f:
        writer = csv.writer(f, delimiter=",")
        header = ["cultivator_name", "batchNumber", "analysts_name", "n_plants", "imageName", "hyp", "rad", "seed_vigor_index"]
        writer.writerow(header)
        for image in images:
            img_path = os.path.join(folder_path,image)
            outputImgPath = os.path.join(outputDir, image)
            print(f"Processing image {image} ............")
            list_hypercotyl_radicle_lengths, output_resultImg, batch_seed_vigor_index = main(img_path)
        
            for hyp, rad in list_hypercotyl_radicle_lengths:
                listResult = [cultivator_name, batchNumber, analysts_name, n_plants, image, hyp, rad, batch_seed_vigor_index]
                writer.writerow(listResult)
            
            cv2.imwrite(outputImgPath, output_resultImg)

            key = cv2.waitKey(-1)
            if key == ord('q'):
                break
            

            print("-"*40)

        cv2.destroyAllWindows()
    f.close()