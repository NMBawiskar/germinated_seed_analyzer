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

def display_img(title,img):
    cv2.namedWindow(title,cv2.WINDOW_NORMAL)
    cv2.imshow(title,img)


def get_contour_center(contour):
    x,y,w,h = cv2.boundingRect(contour)
    c_x = int(x+ w/2)
    c_y = int(y+h/2)
    return (c_x, c_y)

def check_if_point_lies_in_contour(point, point_format:"yx" ,contour):
    """point(y,x)
    point_format = "yx"or "xy"
     """
    
    if point_format=='xy':
        x,y = point
        pointNew = (y,x)
        point_to_parse = pointNew
    else:
        point_to_parse = point

    result = cv2.pointPolygonTest(contour, point_to_parse, False)
    print(result)

    if result>=0:
        ## Point inside contour
        return True
    else:
        ## Point outside contour
        return False


def cropImg(img, tuple_xywh):
    x,y,w,h = tuple_xywh
    cropped = img[y:y+h+1, x:x+w+1]
    return cropped 
    

def get_line_endpoints_intersections(skeletonized_img_np_array):
    whitepixels = np.argwhere(skeletonized_img_np_array==255)
    
    isolated_points = []  ## having only one white count(itselt)
    line_end_points = [] ## having two white count(itselt)
    continuous_line_points = [] ## having three white count(itselt)
    intersetion_points = [] ## having > three white count(itselt)

    for i_row,j_col in whitepixels:
        cropped_window = skeletonized_img_np_array[i_row-1:i_row+2,j_col-1:j_col+2]        
        count_whites = np.sum(cropped_window==255)
        if count_whites ==1:
            isolated_points.append([i_row,j_col])
        elif count_whites==2:
            line_end_points.append([i_row,j_col])
        elif count_whites==3:
            continuous_line_points.append([i_row,j_col])
        elif count_whites>3:
            intersetion_points.append([i_row,j_col])

    # print(f"Total points {whitepixels.shape}")
    # print(f"Intersection_points ={len(intersetion_points)}, endpoints = {len(line_end_points)}, continuous line points = {len(continuous_line_points)}, isolated point = {len(isolated_points)}")

    return [intersetion_points, line_end_points]

def get_seperate_lines_from_intersections(skeletonized_img_np_array, intersection_points):
    
    for intersection_pnt in intersection_points:
        y,x = intersection_pnt
        skeletonized_img_np_array[y,x] = 0
    
    # cv2.imshow('skeletonized_img_np_array',skeletonized_img_np_array)


def find_dist(pt1, pt2):
    y1,x1 = pt1
    y2,x2 = pt2

    dist = ((y2-y1)**2 + (x2-x1)**2)**(1/2)
    return dist

def find_closest_point(contour, point):
    closest_point = None
    min_distance = float('inf')

    for contour_point in contour:
        distance = find_dist(contour_point, point)  # Euclidean distance
        if distance < min_distance:
            min_distance = distance
            closest_point = contour_point

    return closest_point

def find_closest_n_points(contour, point, no_points=2):
    sortedPoints = sorted(contour, key=lambda x:find_dist(x, point))
    
    return sortedPoints[:no_points]

def check_if_point_lies_xywh_box(point, xywh_bbox):
    x1,y1,w,h = xywh_bbox
    x,y = point
    if x >= x1 and x <= (x1+w):
        if y >=y1 and y<= y1+h:
            return True

    return False
