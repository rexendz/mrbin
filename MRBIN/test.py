import cv2
import imutils
import numpy as np
from picam import camera
import time

cam = camera().start()
time.sleep(2)
while True:
    img = cam.read()
    cv2.imshow('img', img)
    k = cv2.waitKey(1) & 0xFF
    if k == 27:
        break

cv2.destroyAllWindows()
cam.close()
