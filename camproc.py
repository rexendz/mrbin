import numpy as np 
import cv2
import imutils
import time
from scipy.spatial import distance as dist
from imutils import contours, perspective
from picam import camera


class processing:
    def __init__(self, ppm=10):
        self.ppm = ppm
        self.diameter = 0
        self.height = 0
        self.cam_started = False
        self.window_started = False
    
    def midpoint(self, ptA, ptB):
        return (ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5
    
    def display_proc(self, window=1, cannyLTH=0, cannyUTH=60, minarea=500): # 0 - RAW IMAGE, 1 - IMAGE, 2 - EDGED, 3 - IMAGE&EDGED, 4 - IMAGE&EDGED w/ TRACKS
        if not self.window_started:
            if window == 1:
                cv2.namedWindow('Image')
            elif window == 2:
                cv2.namedWindow('Edged')
            elif window == 3:
                cv2.namedWindow('Image')
                cv2.namedWindow('Edged')
            elif window == 4:
                cv2.namedWindow('Image')
                cv2.namedWindow('Edged')
                cv2.namedWindow('Tracks')
                cv2.createTrackbar('lth', 'Tracks', 0, 200, self.ignore)
                cv2.createTrackbar('uth', 'Tracks', 60, 200, self.ignore)
                cv2.createTrackbar('area', 'Tracks', 1500, 10000, self.ignore)
            self.window_started = True
            
        if not self.cam_started:
            self.cam = camera().start()
            print("Starting Camera...")
            time.sleep(1)
            print("Camera Started!")
            self.cam_started = True
            
        img = self.cam.read()
        img = imutils.resize(img, width=400)
        orig = img.copy()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (7, 7), 3)
        if window == 4:
            edged = cv2.Canny(gray, cv2.getTrackbarPos('lth', 'Tracks'), cv2.getTrackbarPos('uth', 'Tracks'))
        else:
            edged = cv2.Canny(gray, cannyLTH, cannyUTH)
        edged = cv2.dilate(edged, None, iterations=1)
        edged = cv2.erode(edged, None, iterations=1)

        cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        if len(cnts) > 0:
            (cnts, _) = contours.sort_contours(cnts)

        for c in cnts:
            if window == 4:
                if cv2.contourArea(c) < cv2.getTrackbarPos('area', 'Tracks'):
                    continue
            else:
                if cv2.contourArea(c) < minarea:
                    continue

            box = cv2.minAreaRect(c)
            box = cv2.boxPoints(box)
            box = np.array(box, dtype="int")

            box = perspective.order_points(box)

            cv2.drawContours(img, [box.astype("int")], -1, (0, 255, 0), 2)
            for (x, y) in box:
                cv2.circle(img, (int(x), int(y)), 2, (0, 0, 255), -1)

            (tl, tr, br, bl) = box
            (tltrX, tltrY) = self.midpoint(tl, tr)
            (blbrX, blbrY) = self.midpoint(bl, br)
            (tlblX, tlblY) = self.midpoint(tl, bl)
            (trbrX, trbrY) = self.midpoint(tr, br)
            
            cv2.circle(orig, (int(tltrX), int(tltrY)), 2, (255, 0, 0), -1)
            cv2.circle(orig, (int(blbrX), int(blbrY)), 2, (255, 0, 0), -1)
            cv2.circle(orig, (int(tlblX), int(tlblY)), 2, (255, 0, 0), -1)
            cv2.circle(orig, (int(trbrX), int(trbrY)), 2, (255, 0, 0), -1)
            
            cv2.line(orig, (int(tltrX), int(tltrY)), (int(blbrX), int(blbrY)), (100, 0, 100), 1)
            cv2.line(orig, (int(tlblX), int(tlblY)), (int(trbrX), int(trbrY)), (100, 0, 100), 1)
            
            dA = dist.euclidean((tltrX, tltrY), (blbrX, blbrY))
            dB = dist.euclidean((tlblX, tlblY), (trbrX, trbrY))
            dimA = dA / self.ppm # DIAMETER
            dimB = dB / self.ppm # HEIGHT
            if len(cnts) == 1:
                self.diameter = dimA
                self.height = dimB

            cv2.putText(img, "{:.1f}cm".format(dimB), (int(tltrX - 15), int(tltrY - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
            cv2.putText(img, "{:.1f}cm".format(dimA), (int(trbrX + 10), int(trbrY)), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)

        if window == 0:
            cv2.imshow('Image', orig)
        elif window == 1:
            cv2.imshow('Image', img)
        elif window == 2:
            cv2.imshow('Edged', edged)
        elif window == 3 or window == 4:
            cv2.imshow('Image', img)
            cv2.imshow('Edged', edged)
        
        return cv2.waitKey(1) & 0xFF

    def release(self):
        self.cam.close()
        cv2.destroyAllWindows()


    def getVolume(self):
        volume = (np.pi)*(self.diameter/2)*(self.diameter/2)*(self.height)
        return volume

    def rest(self):
        if self.cam_started == True:
            self.cam.pause()
        self.window_started = False
        cv2.destroyAllWindows()

    def ignore(self, x):
        pass
