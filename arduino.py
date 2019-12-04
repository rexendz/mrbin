# Reads data from the serial monitor without interrupting the main thread

from serial import Serial
import time
from threading import Thread


class SerialListener:
    def __init__(self, baudrate=9600, timeout=0.5):
        try:
            self.ser = Serial('/dev/ttyACM0', baudrate, timeout=timeout)
        except:
            self.ser = Serial('/dev/ttyACM1', baudrate, timeout=timeout)

        self.stopped = False
        self.paused = False
        self.stream = ''
        time.sleep(1)  # Wait for serial buffer to reset

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

    def flush(self):
        self.ser.flush()

    def SerialAvailable(self):
        return self.ser.inWaiting()

    def readDistance(self):
        try:
            return float(self.stream)
        except:
            return -1  # Returns -1 if there is an error in reading

    def readRFID(self):
        return self.stream

    def write(self, msg):
        self.ser.write(msg.encode())


if __name__ == "__main__":  # FOR DEBUGGING ONLY
    uno = SerialListener().start()
    uno.flush()
    print("Serial Started")

    while True:
        uid = ''
        while uid is '':
            uid = uno.readRFID()
        time.sleep(0.1)

        if uid == "5BEE9F0D":
            uno.write('O')
        else:
            uno.write('X')
        print(uid)
        time.sleep(1)

    uno.stop()
