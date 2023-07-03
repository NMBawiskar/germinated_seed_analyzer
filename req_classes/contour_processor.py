import cv2
import numpy as np
from skimage.morphology import skeletonize
from skimage.util import img_as_float, img_as_ubyte
from utils import *
from shapely import ops, geometry
# import matplotlib.pyplot as plt
from .skeletonGeneratorAnalyzer import SkeltonizerContour
from proj_settings import MainSettings, SeedHealth
import json


def plot_line(ax, ob, color):
    x, y = ob.xy
    ax.plot(x, y, color=color, alpha=0.7, linewidth=3, 
            solid_capstyle='round', zorder=2)

class ContourProcessor:
    def __init__(self, imgBinary, colorImg):
        self.binaryImgRaw = imgBinary
        self.colorImg = colorImg
        

        ############
        self.shortlisted_contours = []
        ############

        self.binaryImgShortlistedCnt =None

        self.__get_img_prop()
        self.preprocess_thresholded_img()
        self.__findContours()
        self.__draw_shortlisted_contours_binary()

    def __get_img_prop(self):
        self.imgH, self.imgW = self.binaryImgRaw.shape[:2]

    def __draw_shortlisted_contours_binary(self):
        self.binaryImgShortlistedCnt = np.zeros_like(self.binaryImgRaw)
        for cnt in self.shortlisted_contours:
            cv2.drawContours(self.binaryImgShortlistedCnt, [cnt], -1, 255, -1)
        

    def __findContours(self):
        contours, heirarchy = cv2.findContours(self.binaryImgRaw, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        contoursSorted = sorted(contours, key=cv2.contourArea)
        for cnt in contoursSorted:
            x,y,w,h = cv2.boundingRect(cnt)
            area = cv2.contourArea(cnt)
            if w > 0.75 * self.imgW or h >0.75 * self.imgH:
                continue
            # elif area <500:
            elif area<100:
                continue
            else:
                # print("area",area)
                self.shortlisted_contours.append(cnt)

        # print("Shortlisted contours :",len(self.shortlisted_contours))

    def preprocess_thresholded_img(self):
        kernel_ =cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
        self.binaryImgRaw = cv2.dilate(self.binaryImgRaw, kernel_, 3)

    def display_shortlisted_contours(self, imgColor):
        for cnt in self.shortlisted_contours:
            cv2.drawContours(imgColor, cnt, -1, (255,0,0), 2)

        return imgColor

    def get_skeleton_img(self):
        self.__draw_shortlisted_contours_binary()
        skImg = img_as_float(self.binaryImgShortlistedCnt)
        skeltonized = skeletonize(skImg)
        skeltonized = img_as_ubyte(skeltonized)
        # display_img('binaryImg',self.binaryImgShortlistedCnt)
        # display_img('skeleton',skeltonized)




class Seed():
    
    def __init__(self, xywh, imgBinarySeed, imgBinaryHeadOnly, imgColor, n_segments_each_skeleton=15,
                        thres_avg_max_radicle_thickness=12, mainUI=None):
        self.imgBinarySeed = imgBinarySeed
        self.imgBinaryHead = imgBinaryHeadOnly
        self.colorImg = imgColor
        self.xywh = xywh  ## Location of seed in image
        self.n_segments_each_skeleton = n_segments_each_skeleton    # divisions to make in each length
        self.thres_avg_max_radicle_thickness = thres_avg_max_radicle_thickness # avg thickness to distinguish radicle and hypercotyl

        ####################################
        self.cropped_head_binary = None
        self.cropped_seed_binary = None
        self.imgBinarySeedWoHead = None
        self.skeltonized = None

        self.hyperCotyl_length_pixels = 0
        self.radicle_length_pixels = 0
        self.total_length_pixels = 0

        self.seed_health = SeedHealth.NORMAL_SEED
        self.settings_file_path = MainSettings.settings_json_file_path
        self.dict_settings = {}
        self.load_settings()
        self.remove_head()

    def remove_head(self):
        self.cropped_head_binary = cropImg(self.imgBinaryHead, self.xywh)
        self.cropped_seed_binary = cropImg(self.imgBinarySeed, self.xywh)
        self.cropped_seed_color = cropImg(self.colorImg, self.xywh)
        self.imgBinarySeedWoHead = cv2.subtract(self.cropped_seed_binary, self.cropped_head_binary)

        # display_img('cropped_seed_color',self.cropped_seed_color)
        # display_img('cropped_seed_binary',self.cropped_seed_binary)
        # display_img('cropped_head_binary',self.cropped_head_binary)
        # cv2.waitKey(-1)
    
    def load_settings(self):
        with open(self.settings_file_path, 'r') as f:
            data = f.read()
            self.dict_settings = json.loads(data)


    def show_comparison(self):
        result_img = np.hstack((self.cropped_seed_binary, self.cropped_head_binary, self.imgBinarySeedWoHead))
        # display_img("Removed Head", result_img)
        # cv2.waitKey(-1)

    def morph_head_img(self):
        for i in range(1,5):
            kernel_ = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, ksize=(7,7))
            morphed_ = cv2.dilate(self.cropped_head_binary, kernel=kernel_, iterations=i)
            self.cropped_head_binary = morphed_
            self.imgBinarySeedWoHead = cv2.subtract(self.cropped_seed_binary, self.cropped_head_binary)
            
            contours, heirarchy = cv2.findContours(self.cropped_head_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            maxAreaCnt = max(contours, key=cv2.contourArea)
            maxArea = cv2.contourArea(maxAreaCnt)
            # print(f"kernel 7x7 maxArea {maxArea} iteration {i}")
            # self.show_comparison()
            if maxArea >4000:
                break
        self.getMaxLengthContour()

    def getMaxLengthContour(self):
        contours, heirarchy = cv2.findContours(self.imgBinarySeedWoHead, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        if len(contours)>0:
            maxArcLengthCnt = None
            maxArcLength = 0
            for cnt in contours:
                arcLengthCnt = cv2.arcLength(cnt, closed=True)
                if arcLengthCnt > maxArcLength:
                    maxArcLengthCnt = cnt
                    maxArcLength = arcLengthCnt


            imgBinaryNew = np.zeros_like(self.imgBinarySeedWoHead)
            cv2.drawContours(imgBinaryNew, [maxArcLengthCnt],-1, 255, -1)
            self.imgBinarySeedWoHead = imgBinaryNew

        # display_img("Final root img", self.imgBinarySeedWoHead)
        # cv2.waitKey(-1)

    def skeletonize_root(self):

        skImg = img_as_float(self.imgBinarySeedWoHead)
        skeltonized = skeletonize(skImg)
        self.skeltonized = img_as_ubyte(skeltonized)
        skelton_result = np.hstack((self.imgBinarySeedWoHead, self.skeltonized))
        # display_img('Skeletonized root',skelton_result)


    def analyzeSkeleton(self):
        skeletonAnayzer = SkeltonizerContour(self.imgBinarySeedWoHead, colorImg = self.cropped_seed_color, 
                n_segments_each_skeleton=self.n_segments_each_skeleton, 
                thres_avg_max_radicle_thickness=self.thres_avg_max_radicle_thickness)
        skeletonAnayzer.get_line_endpoints_intersections()
        skeletonAnayzer.seperate_each_branch_of_skeleton()
        
        self.hyperCotyl_length_pixels = skeletonAnayzer.hyperCotyl_length_pixels
        self.radicle_length_pixels = skeletonAnayzer.radicle_length_pixels
        self.total_length_pixels = self.hyperCotyl_length_pixels + self.radicle_length_pixels

        if 'dead_seed_max_length' in self.dict_settings.keys():
            if self.total_length_pixels <= self.dict_settings['dead_seed_max_length']:
                self.seed_health = SeedHealth.DEAD_SEED
            elif self.total_length_pixels <= self.dict_settings['abnormal_seed_max_length']:
                self.seed_health = SeedHealth.ABNORMAL_SEED
            else:
                self.seed_health = SeedHealth.NORMAL_SEED



    def make_offset(self):
        skeleton_copy = self.skeltonized.copy()
        skeleton_copy2 = self.skeltonized.copy()

        intersection_points, line_end_points = get_line_endpoints_intersections(skeletonized_img_np_array=self.skeltonized)
        
        pixels = np.argwhere(self.skeltonized==255)
        pixels = pixels[...,[1,0]]
        
        h_sk, w_sk = self.skeltonized.shape[:2]
        pixels[:,1] = h_sk - pixels[:,1]

        pixels = pixels.tolist()
        # print(pixels)
        if len(pixels)>0:
            line  = geometry.LineString(pixels)
            offset_left = line.parallel_offset(1, 'left', join_style=1)
            offset_right = line.parallel_offset(1, 'right', join_style=1)

            # fig = plt.figure()
            # ax = fig.add_subplot(111)
            # # plot_line(ax, line, "blue")
            # plot_line(ax, offset_left, "green")
            # plot_line(ax, offset_right, "purple")
            # plt.show()

        for endpoint in line_end_points:
            y,x = endpoint
            cv2.circle(skeleton_copy, (x,y),3,255,1)
        
        get_seperate_lines_from_intersections(skeleton_copy2, intersection_points)

        for intersection_point in intersection_points:
            y,x = intersection_point
            cv2.circle(skeleton_copy, (x,y),3,255,1)
            cv2.circle(skeleton_copy, (x,y),5,255,1)
        
        # cv2.imshow("ENdpoints Intersections", skeleton_copy)
        # cv2.waitKey(-1)