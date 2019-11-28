import numpy as np
import cv2
import imutils
import time
from scipy.spatial import distance as dist
from picamera import PiCamera
from picamera.array import PiRGBArray
from imutils import contours, perspective
from threading import Thread
from arduino import SerialListener

class mrbin:
	def __init__(self, resolution=(320,240), framerate=32, PPM=10):
		self.camera = PiCamera()
		self.camera.resolution = resolution
		self.camera.framerate = framerate
		self.PPM = PPM
		self.rawCapture = PiRGBArray(self.camera, size=resolution)
		self.stream = self.camera.capture_continuous(self.rawCapture, format="bgr", use_video_port=True)
		self.frame = None
		self.stopped = False
		self.paused = False
		
	def start(self):
		Thread(target=self.update, args=()).start()
		return self
	
	def update(self):
		if not self.paused:
			for f in self.stream:
				self.frame = f.array
				self.rawCapture.truncate(0)
				if self.stopped:
					self.stream.close()
					self.rawCapture.close()
					self.camera.close()
					return	
				
	def read(self):
		return self.frame
		
	def stop(self):
		self.stopped = True
	
	def pause(self):
		self.paused = True
		
	def getRes(self):
		return self.resolution
		
	def getFPS(self):
		return self.fps
		
	def getPPM(self):
		return self.PPM

def midpoint(ptA, ptB):
	return (ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5	

def nothing(x=0):
	pass

object_detected = False
cam_started = False
cam_destroy = False
camera_initialized = False
window_started = False

if __name__ == "__main__":
	reader = SerialListener().start()
	while (reader.read()) == -1:
		nothing()
	print("Done!")
		
	while True:
		if not object_detected:
			print("Object is not detected!")		
		
		if reader.read() <= 10 and reader.read() > 2:
			if not object_detected:
				print("Object Detected!")
				print("Distance from sensor: ", reader.read())
				object_detected = True
		elif reader.read() > 10:
			object_detected = False
						
		if object_detected:
			if cam_started == False:	
				cam = mrbin().start()
				cam_started = True
			if window_started == False:
				cv2.namedWindow('Image')
				cv2.namedWindow('Edged')
				cv2.namedWindow('tracks')
				cv2.resizeWindow('tracks', 200, 200)
				cv2.createTrackbar('lth', 'tracks', 0, 200, nothing)
				cv2.createTrackbar('uth', 'tracks', 60, 200, nothing)
				cv2.createTrackbar('area', 'tracks', 1500, 10000, nothing)
				window_started = True
				
			img = cam.read()
			img = imutils.resize(img, width=400)
			gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
			gray = cv2.GaussianBlur(gray.copy(), (7,7), 10)
			edged = cv2.Canny(gray, cv2.getTrackbarPos('lth', 'tracks'), cv2.getTrackbarPos('uth', 'tracks'))
			edged = cv2.dilate(edged, None, iterations=1)
			edged = cv2.erode(edged, None, iterations=1)
		
			cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
			cnts = imutils.grab_contours(cnts)
			if len(cnts) > 0: # to avoid errors when there are less than 2 contours to sort
				(cnts, _) = contours.sort_contours(cnts)
		
			for c in cnts:
				if cv2.contourArea(c) < cv2.getTrackbarPos('area', 'tracks'):
					continue
				orig = img
				box = cv2.minAreaRect(c)
				box = cv2.boxPoints(box)
				box = np.array(box, dtype="int")
			
				box = perspective.order_points(box)
				cv2.drawContours(orig, [box.astype("int")], -1, (0, 255, 0), 2)
				for (x, y) in box:
					cv2.circle(orig, (int(x), int(y)), 2, (0, 0, 255), -1)
				
				(tl, tr, br, bl) = box
				(tltrX, tltrY) = midpoint(tl, tr)
				(blbrX, blbrY) = midpoint(bl, br)
				(tlblX, tlblY) = midpoint(tl, bl)
				(trbrX, trbrY) = midpoint(tr, br)
			
				cv2.circle(orig, (int(tltrX), int(tltrY)), 2, (255, 0, 0), -1)
				cv2.circle(orig, (int(blbrX), int(blbrY)), 2, (255, 0, 0), -1)
				cv2.circle(orig, (int(tlblX), int(tlblY)), 2, (255, 0, 0), -1)
				cv2.circle(orig, (int(trbrX), int(trbrY)), 2, (255, 0, 0), -1)
			
				cv2.line(orig, (int(tltrX), int(tltrY)), (int(blbrX), int(blbrY)), (100, 0, 100), 1)
				cv2.line(orig, (int(tlblX), int(tlblY)), (int(trbrX), int(trbrY)), (100, 0, 100), 1)
			
				dA = dist.euclidean((tltrX, tltrY), (blbrX, blbrY))
				dB = dist.euclidean((tlblX, tlblY), (trbrX, trbrY))
				ppm = cam.getPPM()
				dimA = dA / ppm # DIAMETER
				dimB = dB / ppm # HEIGHT
				pi = 3.14159265358
				vol = (pi)*(dimA/2)*(dimA/2)*(dimB) 
				cv2.putText(orig, "{:.1f}cm".format(dimB), (int(tltrX - 15), int(tltrY - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
				cv2.putText(orig, "{:.1f}cm".format(dimA), (int(trbrX + 10), int(trbrY)), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
				cv2.putText(orig, "{:.1f}mL".format(vol), (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255))
			
			cv2.imshow('Image', img)
			cv2.imshow('Edged', edged)
			k = cv2.waitKey(1) & 0xFF
			if k == 27:
				cam_destroy = True
				break
				
		if cam_started:
			if not object_detected:
				cam.pause()
				cv2.destroyAllWindows()
				window_started = False
	
	reader.stop()
	cam.stop()
	cv2.destroyAllWindows()
	cam_destroy == False

	
	
