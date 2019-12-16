import numpy as np 
import cv2
import imutils
import time
from scipy.spatial import distance as dist
from imutils import contours, perspective
try:
    from picam import camera
except ImportError or ImportError:
    print("Failed importing picam.py **THIS IS NORMAL IF RUNNING ON NON-RASPBIAN**")


class ImageProcessor:
    def getMidpoint(self, ptA, ptB):
        return (ptA[0] + ptB[0]) / 2, (ptA[1] + ptB[1]) / 2

    def smoothImage(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        result = cv2.GaussianBlur(gray, (7, 7), 0)
        return result

    def getEdges(self, img, lth, uth):
        edged = cv2.Canny(img, lth, uth)
        edged = cv2.morphologyEx(edged, cv2.MORPH_GRADIENT, None)
        return edged

    def getContours(self, img):
        cnts, hier = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        return cnts

    def getRectContour(self, cnts_pts):
        box = cv2.minAreaRect(cnts_pts)
        box = cv2.boxPoints(box)
        box = np.array(box, dtype="int")
        box = perspective.order_points(box)  # Order pts tl, tr, br, bl
        return box

class Processing(ImageProcessor):
    # device="__IP__"(IF USING IPWEBCAM) device="__PI__"(IF USING PI CAMERA)
    def __init__(self, device="__PI__", url="0.0.0.0", ppm=10):
        self.device = device
        if self.device == "__IP__":
            self.cam = cv2.VideoCapture(url)
        else:
            self.cam = np.zeros([240, 320, 3], np.uint8)
        self.ppm = ppm
        self.diameter = 0
        self.height = 0
        self.cam_started = False

    # 0 - RAW IMAGE, 1 - IMAGE, 2 - EDGED
    def getProcessedImage(self, window=1, cannyLTH=0, cannyUTH=60, minarea=1500):
        img = np.zeros([240, 320, 3], np.uint8)
        
        if self.device == "__PI__":
            if not self.cam_started:
                self.cam = camera().start()
                print("Starting Pi Camera...")
                time.sleep(1)
                print("Pi Camera Started!")
                self.cam_started = True
        
            img = self.cam.read()
            
        elif self.device == "__IP__":
            ret, img = self.cam.read()

        orig = img.copy()
        gray = self.smoothImage(img)
        edged = self.getEdges(gray, cannyLTH, cannyUTH)

        cnts = self.getContours(edged)

        if len(cnts) > 0:
            for c in cnts:
                if cv2.contourArea(c) < minarea:
                    continue

                box = self.getRectContour(c)

                if self.device == "__PI__":
                    img = orig.copy()  # Only render box to single object to save memory
                
                cv2.drawContours(img, [box.astype("int")], -1, (0, 255, 0), 2)
                for (x, y) in box:
                    cv2.circle(img, (int(x), int(y)), 2, (0, 0, 255), -1)

                (tl, tr, br, bl) = box
                (tltrX, tltrY) = self.getMidpoint(tl, tr)
                (blbrX, blbrY) = self.getMidpoint(bl, br)
                (tlblX, tlblY) = self.getMidpoint(tl, bl)
                (trbrX, trbrY) = self.getMidpoint(tr, br)
            
                cv2.circle(img, (int(tltrX), int(tltrY)), 2, (255, 0, 0), -1)
                cv2.circle(img, (int(blbrX), int(blbrY)), 2, (255, 0, 0), -1)
                cv2.circle(img, (int(tlblX), int(tlblY)), 2, (255, 0, 0), -1)
                cv2.circle(img, (int(trbrX), int(trbrY)), 2, (255, 0, 0), -1)
            
                cv2.line(img, (int(tltrX), int(tltrY)), (int(blbrX), int(blbrY)), (100, 0, 100), 1)
                cv2.line(img, (int(tlblX), int(tlblY)), (int(trbrX), int(trbrY)), (100, 0, 100), 1)
            
                dA = dist.euclidean((tltrX, tltrY), (blbrX, blbrY))
                dB = dist.euclidean((tlblX, tlblY), (trbrX, trbrY))
                dimA = dA / self.ppm  # DIAMETER
                dimB = dB / self.ppm  # HEIGHT
                if len(cnts) == 1:
                    self.diameter = dimA
                    self.height = dimB

                cv2.putText(img, "{:.1f}cm".format(dimB), (int(tltrX - 15), int(tltrY - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
                cv2.putText(img, "{:.1f}cm".format(dimA), (int(trbrX + 10), int(trbrY)), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)

            if window == 0:
                return orig
            elif window == 1:
                return img
            elif window == 2:
                return edged
        return np.zeros([240, 320, 3], np.uint8)

    def release(self):
        if self.device == "__PI__":
            self.cam.close()
        elif self.device == "__IP__":
            self.cam.release()

        cv2.destroyAllWindows()

    def getVolume(self):
        volume = np.pi * (self.diameter / 2) * (self.diameter / 2) * self.height
        return volume

    def rest(self):
        if self.device == "__PI__":
            if self.cam_started:
                self.cam.pause()

        self.window_started = False
        cv2.destroyAllWindows()


