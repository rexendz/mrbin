from camproc import processing
try:
    from arduino import SerialListener
except ImportError or ImportError:
    print ("Warning: No Arduino connected")


object_detected = False
window_started = False

if __name__ == "__main__":
    try:
        reader = SerialListener().start()
        while (reader.read()) == -1:
            pass
    except NameError:
        print ("Warning: No Arduino")

    print("Done!")
    processor = processing(device="__IP__")
    while True:
        try:
            distance = reader.read()
            if distance <= 10 and distance > 2:
                if not object_detected:
                    print("Object Detected!")
                    print("Distance from sensor: ", reader.read())
                    object_detected = True
            
            elif distance > 10:
                object_detected = False
        except NameError:
            object_detected = True  # IF there is no Arduino, always show image

        if not object_detected:
            print("Object is not detected!")
            processor.rest()
            
        elif object_detected:
            # window=0 --- Raw Image from Camera
            # window=1 --- Image w/ Detection 
            # window=2 --- Edge Mask
            # window=3 --- Image w/ Detection & Edge Mask
            # window=4 --- Image w/ Detection & Edge Mask & Trackbars
            k = processor.display_proc(window=4)
            
            if k == 27:
                break
    try:
        reader.stop()
    except NameError:
        print("Warning: No Arduino")
    processor.release()
