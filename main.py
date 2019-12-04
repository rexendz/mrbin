from camproc import processing
from sql import SQLServer
import time
import argparse
try:
    from arduino import SerialListener
except ImportError or ImportError:
    print("Warning: No Arduino connected")

if __name__ == "__main__":
    object_detected = False
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--ip", help="Select IP Camera with URL Instead Of PI Camera")
    parser.add_argument("-w", "--window", help="Select Window To Display[0-4]", type=int)
    
    args = parser.parse_args()
    
    device = "__PI__"
    url = "0.0.0.0"
    window = 4;
    
    if args.ip is not None:
        device = "__IP__"
        url = args.ip
    if args.window is not None:
        window = args.window

    userAuthenticated = False

    try:
        reader = SerialListener().start()
        reader.flush()
        sql = SQLServer()
        time.sleep(1)

        print("Please scan your ID")

        name = None
        pts = None
        while not userAuthenticated:
            uid = ''
            while uid is '':
                uid = reader.readRFID()
            time.sleep(0.1)
            user = sql.findUid(int(uid, 16))
            if len(user) > 0:
                (_, name, _, pts), = user
                print("Welcome, " + name)
                print("Current Incentives: " + str(pts))
                reader.write('O')
                userAuthenticated = True
            else:
                reader.write('X')
                print("There is no record of UID: " + uid + " in our database")
                cr = input("Would you like to create a new one? (Y/N): ")
                if cr == 'Y' or cr == 'y':
                    name = input("Enter your name: ")
                    sql.insert(name, int(uid, 16), 0)
                print("Please scan your ID again")
            time.sleep(1)

        sql.close()
    except NameError:
        print("Warning: No Arduino")

    processor = processing(device=device, url=url)

    while True:
        try:
            distance = reader.readDistance()
            if 18 >= distance > 2:
                if not object_detected:
                    # print("Object Detected!")
                    # print("Distance from sensor: ", reader.readDistance())
                    object_detected = True
            
            elif distance > 10:
                object_detected = False
        except NameError:
            object_detected = True  # IF there is no Arduino, always show image

        if not object_detected:
            # print("Object is not detected!")
            processor.rest()
            
        elif object_detected:
            # window=0 --- Raw Image from Camera
            # window=1 --- Image w/ Detection
            # window=2 --- Edge Mask
            # window=3 --- Image w/ Detection & Edge Mask
            # window=4 --- Image w/ Detection & Edge Mask & Trackbars
            k = processor.display_proc(window=window)
            
            if k == 27:
                break
    try:
        reader.stop()
    except NameError:
        print("Warning: No Arduino")
    processor.release()
