from picam import camera
import time
import cv2
import os

files = os.listdir('pimages')
imnum = len(files)+1
path = '/home/pi/mrbin/pimages/'
cam = camera().start()
time.sleep(5)
print("READY")
print("Starting image: " + path+str(imnum)+'.jpg')
while True:
    img = cam.read()
    cv2.imshow('img', img)
    key = cv2.waitKey(1)
    if key == ord('s'):
        cv2.imwrite((path+str(imnum)+'.jpg'), img)
        print("Image Saved")
        print((path+str(imnum)+'.jpg'))
        imnum += 1
    if key == ord('q'):
        break
cv2.destroyAllWindows()
cam.close()
        
    
