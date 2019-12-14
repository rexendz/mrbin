import numpy as np 
import cv2
import imutils
from imutils import contours, perspective
from picamera import PiCamera
from picamera.array import PiRGBArray


class imageprocessing:
    def smoothImage(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) # Converts the img to grayscale because our method explicitly requires grayscale images
        gray = cv2.GaussianBlur(gray, (7, 7), 0) # Blurs the image to reduce noise
        return gray # return the image to the caller

    def getCanny(self, img, lth, uth):
        edged = cv2.Canny(img, lth, uth) # Get canny edge detection with custom user-based threshold lth uth
        edged = cv2.dilate(edged, None, iterations=1) # Dilate the edges to widen the lines
        edged = cv2.erode(edged, None, iterations=1) # Erode the edges to narrow the lines
        return edged # return the edged image to the caller
    
    def getContours(self, img):
        cnts = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) # calculates full hierarchy of contours
        cnts = imutils.grab_contours(cnts) # Just for backward compatibility (python 2)
        if len(cnts) > 1: # If there is at least one contour detected
            (cnts, _) = contours.sort_contours(cnts) # Sort the detected contours by their size
            return cnts # Return the contour to the caller
        else:
            return None  # Which means there are no contours

    def getPoints(self, cnts, lth, uth):
        for c in cnts: # Iterate through each contours
            if cv2.contourArea(c) > lth or cv2.contourArea(c) < uth: # We only get the contour with the desired area
                rect = cv2.minAreaRect(c) # Finds a rotated rectangle of the minimum area enclosing the input 2D point set
                box = cv2.boxPoints(rect) # Get the four points of the rectangle
                box = perspective.order_points(box) # Order 4 points to top left, top right, bottom right, bottom left
                return box # Return the ordered 4 points clockwise from top left

    def drawConts(self, img, cnts):
        cv2.drawContours(img, [cnts.astype("int")], -1, (0, 255, 0), 2) # Just draws the contour (THE GREEN BOX)
        
    def showImage(self, img):
        cv2.imshow('Board', img) # Show the image
        return cv2.waitKey(1) & 0xFF # Return the keypresses

class scrabble(imageprocessing):  # class scrabble inherits from imageprocessing class, so all functions of imageprocessing is accessible to scrabble
    def __init__(self):  # This automatically gets called when an object is instantiated
        self.cam = PiCamera() # Instantiate a PiCamera object
        self.cam.resolution = (320, 240) # Set the resolution
        self.cam.framerate = 32 # Set the framerate
        self.rawCapture = PiRGBArray(self.cam, size=(320, 240)) # Produces a 3-dimensional RGB array from RGB Capture
        self.stream = self.cam.capture_continuous(self.rawCapture, format="bgr", use_video_port=True) # Captures images continuously
        self.img = None # Create variable accessible to the whole class of scrabble
        self.stopped = False

    def getBoard(self):
        for f in self.stream: # Iterate through self.stream(array of image arrays) which contains images from the pi camera
            self.img = f.array # Converts the image to readable numpy array for opencv
            self.rawCapture.truncate(0) # Empty the array between each capture to make room for new image
            image = self.smoothImage(self.img) # smoothimage is a function from imageprocessing that minimizes noise
            image = self.getCanny(image, 50, 100) # Gets the edges of an object e.g. scrabble board
            image_contour = self.getContours(image) # Gets region of interests for a given threshold
            if image_contour is None: # If there is no contours, skip the other code to avoid errors (unpacking None types)
                return None
            board_points = self.getPoints(image_contour, 30000, 40000) # get the four points of the detected rectangle from the edges
            return board_points # Give the points to the caller

    def drawBoard(self): # Draws the captured image
        while not self.stopped: # To stop the infinite loop
            box = self.getBoard()
            if box is not None: # If there is no contours then...
                self.drawConts(self.img, box) # Do not draw contours (obviously)
            keyEscape = self.showImage(self.img) # A literal 'escape' key to escape the loop
            if keyEscape == 27: # 27 is the keycode for escape
                self.stopped = True # If escape key is pressed, then the loop will stop


if __name__ == "__main__":
    game = scrabble()  # Create new object from class scrabble
    boardPoints = game.getBoard()
    game.drawBoard()

    (tl, tr, br, bl) = boardPoints

    # Do something with the board points, e.g. crop perspectiveTransform(rect, destination) blabla (idk that pa)
    # Integrate this to your own code




    
