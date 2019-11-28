from camproc import processing
from arduino import SerialListener

object_detected = False
window_started = False

if __name__ == "__main__":
    reader = SerialListener().start()
    while (reader.read()) == -1:
        pass

    print("Done!")
    processor = processing()
    while True:
        if not object_detected:
            print("Object is not detected!")

		if reader.read() <= 10 and reader.read() > 2: # Checks if object is in range
			if not object_detected: # Only runs if object_detected is not yet triggered
				print("Object Detected!")
				print("Distance from sensor: ", reader.read())
				object_detected = True

		elif reader.read() > 10:
			object_detected = False

        if object_detected:
            if not window_started:
                k = processor.display_proc(window=1, window_started=window_started)
                window_started = True
            
            if k == 27:
                break
        
        
        if not object_detected:
            processor.rest()
    
    
    reader.stop()
    processor.release()





    