import cv2

class ContourProcessor:
    def __init__(self, imgBinary):
        self.binaryImgRaw = imgBinary

        ############
        self.shortlisted_contours = []
        ############

        self.__get_img_prop()
        self.preprocess_thresholded_img()
        self.__findContours()

    def __get_img_prop(self):
        self.imgH, self.imgW = self.binaryImgRaw.shape[:2]



    def __findContours(self):
        contours, heirarchy = cv2.findContours(self.binaryImgRaw, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        contoursSorted = sorted(contours, key=cv2.contourArea)
        for cnt in contoursSorted:
            x,y,w,h = cv2.boundingRect(cnt)
            area = cv2.contourArea(cnt)
            if w > 0.75 * self.imgW or h >0.75 * self.imgH:
                continue
            elif area <1000:
                continue
            else:
                print("area",area)
                self.shortlisted_contours.append(cnt)

        print("Shortlisted contours :",len(self.shortlisted_contours))

    def preprocess_thresholded_img(self):
        kernel_ =cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
        self.binaryImgRaw = cv2.dilate(self.binaryImgRaw, kernel_, 3)

    def display_shortlisted_contours(self, imgColor):
        for cnt in self.shortlisted_contours:
            cv2.drawContours(imgColor, cnt, -1, (255,0,0), 2)

        return imgColor


class Seed:
    def __init__(self) -> None:
        pass
