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
        distance = reader.read()
        if distance <= 10 and distance > 2:
            if not object_detected:
                print("Object Detected!")
                print("Distance from sensor: ", reader.read())
                object_detected = True
            
        elif distance > 10:
            object_detected = False

        if not object_detected:
            print("Object is not detected!")
            processor.rest()
            
        elif object_detected:
            # window=0 --- Raw Image from Camera
            # window=1 --- Image w/ Detection 
            # window=2 --- Edge Mask
            # window=3 --- Image w/ Detection & Edge Mask
            # window=4 --- Image w/ Detection & Edge Mask & Trackbars
            k = processor.display_proc(window=1) 
            
            if k == 27:
                break
    
    reader.stop()
    processor.release()





    
