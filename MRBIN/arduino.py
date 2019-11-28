from serial import Serial
import time
from threading import Thread

class SerialListener:
    def __init__(self, baudrate=9600, timeout=1):
        try:
            self.ser = Serial('/dev/ttyACM0', baudrate, timeout=timeout)
        except:
            self.ser = Serial('/dev/ttyACM1', baudrate, timeout=timeout)
            
        self.stopped = False
        self.paused = False
        self.stream = ''
        time.sleep(1) # Wait for serial buffer to reset
        
    def start(self):
        Thread(target=self.update, args=()).start()
        return self
    
    def update(self):
        if not self.paused:
            while True:
                if self.stopped:
                    self.ser.close()
                    print("Serial Thread Stopped")
                    print("Serial Port Closed")
                    break
                try:
                    self.stream = self.ser.readline().decode('utf-8')
                except:
                    self.stream = self.ser.readline().decode('ascii')
                self.stream = self.stream.rstrip()
                
    def stop(self):
        self.stopped = True
    
    def pause(self):
        self.paused = True
        
    def read(self):
        try:
            return float(self.stream)
        except:
            return -1   # Return -1 if there is an error in reading

if __name__ == "__main__": # FOR DEBUGGING ONLY
    reader = SerialListener().start()
    while True:
        key = input("Enter to read/q to exit: ")
        if key == 'q':
            reader.stop()
            break
        print(reader.read())
