import numpy as np 
import cv2
import imutils
import time
from scipy.spatial import distance as dist
from imutils import contours, perspective
from picamera import PiCamera
from picamera.array import PiRGBArray

class imageprocessing:
    def smoothImage(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (7, 7), 0)
        return gray

    def getCanny(self, img, lth, uth):
        edged = cv2.Canny(img, lth, uth)
        edged = cv2.dilate(edged, None, iterations=1)
        edged = cv2.erode(edged, None, iterations=1)
        return edged
    
    def getContours(self, img):
        cnts = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        if len(cnts) > 1:
            (cnts, _) = contours.sort_contours(cnts)
            return cnts
        else:
            return -1  # Which means there are no contours

    def getValidContour(self, cnts, lth, uth):
        for c in cnts:
            if cv2.contourArea(c) > lth or cv2.contourArea(c) < uth:
                return c

    def getPoints(self, contour):
        rect = cv2.minAreaRect(contour)
        box = cv2.boxPoints(rect)
        box = perspective.order_points(box) # Order 4 points to top left, top right, bottom right, bottom left
        return box

    def drawConts(self, img, cnts):
        cv2.drawContours(img, [cnts.astype("int")], -1, (0, 255, 0), 2)
        
    def showImage(self, img):
        cv2.imshow('Board', img)
        cv2.waitKey()

class scrabble(imageprocessing):
    def __init__(self):
        self.cam = PiCamera()
        self.cam.resolution = (320, 240)
        self.cam.framerate = 32
        self.rawCapture = PiRGBArray(self.cam, size=(320, 240))
        self.stream = self.cam.capture_continuous(self.rawCapture, format="bgr", use_video_port=True)
        self.img = None

    def getBoard(self):
        for f in self.stream:
            self.img = f.array
            self.rawCapture.truncate(0)
            image = self.smoothImage(self.img)
            image = self.getCanny(image, 50, 100)
            image_contour = self.getContours(image)
            if len(image_contour) < 0:
                continue
            valid = self.getValidContour(image_contour, 30000, 40000)
            board_points = self.getPoints(valid)
            if board_points is not None:
                return board_points

    def drawBoard(self, box):
        self.drawConts(self.img, box)
        self.showImage(self.img)


if __name__ == "__main__":
    game = scrabble()
    board_pts = game.getBoard()
    game.drawBoard(board_pts)

    (tl, tr, br, bl) = board_pts




    
