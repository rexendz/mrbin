# Reads data from the serial monitor without interrupting the main thread

from serial import Serial, serialutil
import time
from threading import Thread
from sql import SQLServer


class SerialListener:
    def __init__(self, baudrate=9600, timeout=0.5):
        try:
            self.ser = Serial('/dev/ttyACM0', baudrate, timeout=timeout)
        except serialutil.SerialException:
            try:
                self.ser = Serial('/dev/ttyACM1', baudrate, timeout=timeout)
            except serialutil.SerialException:
                self.ser = Serial('/dev/ttyACM2', baudrate, timeout=timeout)

        self.stopped = False
        self.paused = False
        self.stream = ''
        time.sleep(1)  # Wait for serial buffer to reset
        print("Serial Started")

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
    sql = SQLServer()
    uno.flush()
    name = None
    pts = None
    try:
        while True:
            uid = ''
            while uid is '':
                uid = uno.readRFID()
            time.sleep(0.1)
            user = sql.findUid(int(uid, 16))
            if len(user) > 0:
                (_, name, _, pts), = user
                print("Welcome, " + name)
                print("Current Incentives: " + str(pts))
                uno.write('O')
            else:
                uno.write('X')
                print("There is no record of UID: " + uid + " in our database")
                cr = input("Would you like to create a new one? (Y/N): ")
                if cr == 'Y' or cr == 'y':
                    name = input("Enter your name: ")
                    sql.insert(name, int(uid, 16), 0)
                print("Please scan your ID again")
            time.sleep(1)
    except KeyboardInterrupt:
        uno.stop()
        sql.close()
