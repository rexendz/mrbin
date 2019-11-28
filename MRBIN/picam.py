from picamera import PiCamera
from picamera.array import PiRGBArray
from threading import Threading

class picamera:
    def __init__(self, resolution=(320,240), framerate=30, ppm=10):
        self.cam = PiCamera()
        self.cam.resolution = resolution
        self.cam.framerate = framerate
        self.ppm = ppm
        self.rawCapture = PiRGBArray(self.cam, resolution=self.resolution)
        self.stream = self.cam.capture_continuous(self.rawCapture, format="bgr", use_video_port=True)
        self.frame = None
        self.stopped = False
        self.paused = False

        def start(self):
            Threading(target=self.update, args=()).start()
            return self

        def update(self):
            if not self.paused:
                for f in self.stream:
                    self.frame = f.array()
                    self.rawCapture.truncate(0)
                    if self.stopped:
					self.stream.close()
					self.rawCapture.close()
					self.cam.close()
					return	

        def read(self):
            return self.frame

        def pause(self):
            self.paused = True
        
        def resume(self):
            self.paused = False