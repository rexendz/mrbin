from serial import Serial
import time
from threading import Thread

class SerialListener:
	def __init__(self, port='/dev/ttyACM1', baudrate=9600, timeout=1):
		try:
			self.ser = Serial(port, baudrate, timeout=timeout)
		except:
			self.ser = Serial('/dev/ttyACM0', baudrate, timeout=timeout)
		self.stopped = False
		self.paused = False
		self.stream = ''
		print("Serial port initialized, waiting 3 seconds...")
		time.sleep(3) # Wait for serial buffer to reset
		
	def start(self):
		Thread(target=self.update, args=()).start()
		return self
	
	def update(self):
		if not self.paused:
			while True:
				if self.stopped:
					self.ser.close()
					print("Serial closed!")
					break
				try:
					self.stream = self.ser.readline().decode('utf-8')
				except:
					self.stream = self.ser.readline().decode('ascii')
				self.stream = self.stream.rstrip()
				
	def stop(self):
		self.stopped = True
		print("Thread stopped!")
	
	def pause(self):
		self.paused = True
		
	def read(self):
		try:
			return float(self.stream)
		except:
			return -1	

if __name__ == "__main__": # FOR DEBUGGING ONLY
	reader = SerialListener().start()
	while True:
		key = input("Enter to read/q to exit: ")
		if key == 'q':
			reader.stop()
			break
		print(reader.read())
