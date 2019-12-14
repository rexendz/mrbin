import cv2
import numpy as np
import copy
from picamera import PiCamera
from picamera.array import PiRGBArray

class imageprocessing():
    def __init__(self):
        pass

    def smoothenImage(self, img):
        result = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        result = cv2.bilateralFilter(result, 7, 30, 30)
        # result = cv2.GaussianBlur(result, (5, 5), 0)
        return result

    def cannyOf(self, img):
        high_thresh, thresh_im = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        print("High Threshhold: ",high_thresh)
        lowThresh = 0.5 * high_thresh
        result = cv2.Canny(img, lowThresh, high_thresh)
        return result

    def dilationOf(self, img):
        kernal = np.ones((1, 1), np.uint8)
        result = cv2.dilate(img, kernel=kernal)
        return result

    def blackImageOf(self, img):
        result = np.zeros((img.shape[0], img.shape[1]), np.uint8)
        return result

    def contoursOf(self, img):
        contours, hierarchy = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        return contours

    def smallestContour(self, img, contours, indexes):
        smallest = 999999
        chosen = 0

        for x in indexes:
            arcLength = cv2.arcLength(contours[x], True)
            if arcLength < smallest:
                smallest = arcLength
                chosen = x
        return chosen

    def validContours(self, img, contours):
        valid = []
        for x in range(len(contours)):
            arcLength = cv2.arcLength(contours[x], True)
            threshold = img.shape[0] * 4
            if arcLength > threshold:
                valid.append(x)

        return valid

    def getConvexHull(self, contours, index):
        hull = cv2.convexHull(contours[index])
        contours[index] = hull
        approx = cv2.approxPolyDP(contours[index], 0.05 * cv2.arcLength(contours[index], True), True)
        return approx

    def addText(self, text, x, y):
        font = cv2.FONT_HERSHEY_SIMPLEX
        fontScale = 1
        fontColor = (255, 255, 255)
        lineType = 2
        position = (x, y)
        cv2.putText(self.img, text, position, font, fontScale, fontColor, lineType)
        return

    def sortLargeContours(self, indexes):
        valid = []
        for x in indexes:
            approx = self.getConvexHull(self.contours, x)
            if len(approx) == 4:
                x, y, w, h = cv2.boundingRect(approx)
                aspectRatio = float(w) / h
                if aspectRatio >= 0.70 and aspectRatio <= 1.30:
                    valid.append(x)

            self.contours[x] = approx
        return valid

    def getCornerOf(self, contours, board):
        coordinates = {}
        if board is not None:
            for point in range(len(contours[board])):
                x = contours[board][point][0][0]
                y = contours[board][point][0][1]
                coordinates[x] = y

            s = sorted(coordinates.keys())

            points = ["", "", "", ""]
            if coordinates[s[0]] > coordinates[s[1]]:
                points[0] = [s[1], coordinates[s[1]]]
                points[2] = [s[0], coordinates[s[0]]]
            else:
                points[0] = [s[0], coordinates[s[0]]]
                points[2] = [s[1], coordinates[s[1]]]

            if coordinates[s[2]] > coordinates[s[3]]:
                points[1] = [s[3], coordinates[s[3]]]
                points[3] = [s[2], coordinates[s[2]]]
            else:
                points[1] = [s[2], coordinates[s[2]]]
                points[3] = [s[3], coordinates[s[3]]]

            return points
        else:
            return



    def getTrimmedImage(self, cornerPoints):
        pts1 = np.float32(cornerPoints)
        pts2 = np.float32([[0, 0], [602, 0], [0, 602], [602, 602]])
        M = cv2.getPerspectiveTransform(pts1, pts2)
        return cv2.warpPerspective(self.img, M, (602, 602))

class scrabble(imageprocessing):

    def __init__(self):
        self.camera = PiCamera()
        self.camera.resolution = (460, 320)
        self.img = np.zeros((460, 320, 3), np.uint8)
        self.createMainWindow()

    def imageTrackbar(self, x):
        self.img = cv2.imread(self.images[x])
        self.img = self.processedImage(self.img)
        cv2.imshow("image", self.img)
        return

    def dilatedTrackbar(self, x):
        image = self.processedImage(self.img)
        cv2.imshow("dilated", image)
        return

    def processedImage(self, img):
        img_copy = copy.deepcopy(img)       #I copied the original unedited image to img_copy
        img = self.smoothenImage(img)       #Smoothened the original image, (converted to grayschool then blurred it a little)
        img = self.cannyOf(img)             #Edge detection, To get the edges of the image
        img = self.dilationOf(img)          #Dilated the edge'd detected image, to reduce noise

        cv2.imshow("Edge Detection", img)   #Displayed the clean, edge detected image, for further analization

        self.contours = self.contoursOf(img)    #Gathered the contours of the edge detected image, Ginagawa nito is, sineseparate nya yung mga lines sa edge detected image at stinostore to sa isang array

        largeContours = self.validContours(img, self.contours)  # gets contours that are large enough to be considered the board, ang ginawa dito is, nag iterate ako sa array ng mga lines na na detect ko sa contours, tapos tiningnan ko if mahaba ba yung line para ma consider sya as board,
        validContour = self.sortLargeContours(largeContours)   # from the large contours, tinitingnan ko saan dun yung merong, four sides i.e. (box, or rectangle or trapezoid)

        image_possibleContours = copy.deepcopy(img_copy)    #gumawa lang ako ulit ng copy nung original image
        image_chosenContour = copy.deepcopy(img_copy)       #same lang dito

        #------Drinaw ko lang yung mga valid contours dun sa copy ng original image tapos dinisplay para makita nyo------
        for x in validContour:
            cv2.drawContours(image_possibleContours, self.contours, x, (1, 1, 255), 3)
        cv2.imshow("Possible Board Contours", image_possibleContours)
        #--------------------------------------------------------------------------------------------------------------


        theBoard = self.smallestContour(img, self.contours, validContour)   #Kinuha ko yung pinaka maliit na contour dun sa mga valid contours, iaassume ko na yung pinakamaliit dun is yung contour ng board
        cv2.drawContours(image_chosenContour, self.contours, theBoard, (255, 1, 1), 3)  #drinaw ko lang ulit yung pinakamaliit na valid contour sa copy ng original image
        cv2.imshow("Chosen Contour", image_chosenContour)


        cornerPoints = self.getCornerOf(self.contours, theBoard);   #Kinuha ko yung corner points nung valid contour
        img = self.getTrimmedImage(cornerPoints)    #Trimmed the image

        return img #return dun para i display

    def getImage(self):
        self.camera.capture('/home/pi/Desktop/calib.jpg')
        return cv2.imread('/home/pi/Desktop/calib.jpg')

    def createMainWindow(self):
        cv2.namedWindow("image")
        k = 0
        while k != 27:
            self.img = self.getImage()
            cv2.imshow("image", self.processedImage(self.img))
            k = cv2.waitKey()
        cv2.destroyAllWindows()



def main():
    game = scrabble()


if __name__ == "__main__":
    main()
