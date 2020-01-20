import imutils
import numpy as np
import cv2
import time
from scipy.spatial import distance as dist
from imutils import perspective


class ImageProcessor:
    def getMidpoint(self, ptA, ptB):
        return (ptA[0] + ptB[0]) / 2, (ptA[1] + ptB[1]) / 2

    def smoothImage(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        result = cv2.GaussianBlur(gray, (5, 5), 0)
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
    def __init__(self, device="__PI__", cam=None, ppmX=1, ppmY=1):
        self.device = device
        self.cam = cam
        self.ppmX = ppmX
        self.ppmY = ppmY
        self.diameter = 0
        self.height = 0
        self.volume = 0
        self.averageVolume = 0
        self.counter = 0
        print("INITIALIZED")

    # 0 - RAW IMAGE, 1 - IMAGE, 2 - EDGED
    def getProcessedImage(self, window=1, cannyLTH=0, cannyUTH=30, minarea=300):
        img = np.zeros([240, 320, 3], np.uint8)
        if self.device == "__PI__":
            self.cam.resume()
            img = self.cam.read()
            
        elif self.device == "__IP__":
            ret, img = self.cam.read()

        img = imutils.resize(img, width=320)

        orig = img.copy()
        gray = self.smoothImage(img)
        edged = self.getEdges(gray, cannyLTH, cannyUTH)

        cnts = self.getContours(edged)
        if len(cnts) > 0:
            for c in cnts:
                if cv2.contourArea(c) < minarea or cv2.contourArea(c) > 30000:
                    continue

                box = self.getRectContour(c)
                (tl, tr, br, bl) = box
                if tl[0] < 10 or tr[0] > 300 or br[0] > 300 or bl[0] < 10 or tl[1] < 10 or tr[1] < 10 or br[1] > 200 or bl[1] > 200:
                    continue
                #print("tl:", tl)
                #print("tr:", tr)
                #print("br:", br)
                #print("bl:", bl)

                if self.device == "__PI__":
                    img = orig.copy()  # Only render box to single object to save memory
                
                cv2.drawContours(img, [box.astype("int")], -1, (0, 255, 0), 2)
                for (x, y) in box:
                    cv2.circle(img, (int(x), int(y)), 2, (0, 0, 255), -1)
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
                dimA = dA / self.ppmY  # DIAMETER
                dimB = dB / self.ppmX  # HEIGHT
                self.diameter = dimA
                self.height = dimB
                self.volume += self.getVolume()
                self.counter += 1
                self.averageVolume = self.volume/self.counter
                cv2.putText(img, "{:.2f}cm".format(dimB), (int(tltrX - 15), int(tltrY - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
                cv2.putText(img, "{:.2f}cm".format(dimA), (int(trbrX + 10), int(trbrY)), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
                cv2.putText(img, "{:.2f}mL".format(self.averageVolume), (5, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)

            cv2.putText(img, "Volume Detector", (65, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            if window == 0:
                return orig
            elif window == 1:
                return img
            elif window == 2:
                return edged
        return np.zeros([240, 320, 3], np.uint8)

    def release(self):
        if self.device == "__IP__":
            self.cam.release()

    def getVolume(self):
        volume = np.pi * (self.diameter / 2) * (self.diameter / 2) * self.height
        return volume

    def getAveVol(self):
        return self.averageVolume

    def getAveHei(self):
        return self.height
        
    def getAveDia(self):
        return self.diameter
        
    def rest(self):
        self.volume, self.averageVolume, self.counter = 0, 0, 0
        if self.device == "__PI__":
            self.cam.pause()

if __name__ == "__main__":
    def nothing(x):
        pass

    from picam import camera
    cam = camera().start()
    proc = Processing(cam=cam)
    cv2.namedWindow('track')
    cv2.createTrackbar('lth', 'track', 20, 255, nothing)
    cv2.createTrackbar('uth', 'track', 60, 255, nothing)
    import time
    time.sleep(1)
    while True:
        img = proc.getProcessedImage(1, cv2.getTrackbarPos('lth', 'track'), cv2.getTrackbarPos('uth', 'track'))
        cv2.imshow('img', img)
        q = cv2.waitKey(1)
        if q == ord('q'):
            break
    cv2.destroyAllWindows()
    cam.close()
