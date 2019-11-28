from picamera import PiCamera
from picamera.array import PiRGBArray
from threading import Thread

class camera:
    def __init__(self, resolution=(320,240), framerate=32):
        self.cam = PiCamera()
        self.cam.resolution = resolution
        self.cam.framerate = framerate
        self.rawCapture = PiRGBArray(self.cam, size=resolution)
        self.stream = self.cam.capture_continuous(self.rawCapture, format="bgr", use_video_port=True)
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
                    self.cam.close()
                    print("Camera Thread Stopped")
                    return  

    def read(self):
        return self.frame
    
    def close(self):
        self.stopped = True

    def pause(self):
        self.paused = True
        
    def resume(self):
        self.paused = False
        