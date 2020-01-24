import os
import cv2
import numpy as np
import tensorflow.compat.v1 as tf
import sys
from scipy.spatial import distance as dist
from utils import label_map_util
from utils import visualization_utils as vis_util

try:
    from picam import camera
except ImportError or ImportError:
    print("Failed importing picam.py **THIS IS NORMAL IF RUNNING ON NON-RASPBIAN**")

sys.path.append("..")


class ObjectClassifier:
    # device="__IP__"(IF USING IPWEBCAM) device="__PI__"(IF USING PI CAMERA)
    def __init__(self, device="__PI__", cam=None):
        print("Initializing Tensorflow...")
        self.userpath = os.getenv("HOME")
        self.device = device
        self.cam = cam

        self.boxes, self.scores, self.classes, self.num = None, None, None, None
        self.confidence = None
        self.image = None
        self.counter = 0
        self.detectedID = []

        dir = self.userpath+'/mrbin/tensorflow/inference_graph_29782'
        ckpt_path = os.path.join(dir, 'frozen_inference_graph.pb')
        labels_path = os.path.join(dir, 'labelmap.pbtxt')
        NUM_CLASSES = 4
        label_map = label_map_util.load_labelmap(labels_path)
        categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
        self.category_index = label_map_util.create_category_index(categories)
        self.detection_graph = tf.Graph()
        with self.detection_graph.as_default():
            od_graph_def = tf.GraphDef()
            with tf.gfile.GFile(ckpt_path, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')

            self.sess = tf.Session(graph=self.detection_graph)
        print("Tensor Initialized")

    def initialize(self, cam):
        self.boxes, self.scores, self.classes, self.num = None, None, None, None
        self.confidence = None
        self.image = None
        self.counter = 0
        self.detectedID = []
        self.cam = cam


    def sessionRun(self):
        image_tensor = self.detection_graph.get_tensor_by_name('image_tensor:0')
        detection_boxes = self.detection_graph.get_tensor_by_name('detection_boxes:0')
        detection_scores = self.detection_graph.get_tensor_by_name('detection_scores:0')
        detection_classes = self.detection_graph.get_tensor_by_name('detection_classes:0')
        num_detections = self.detection_graph.get_tensor_by_name('num_detections:0')
        if self.device == "__PI__":
            self.cam.resume()
            self.image = self.cam.read()
        else:
            _, self.image = self.cam.read()
        image_expanded = np.expand_dims(self.image, axis=0)
        (self.boxes, self.scores, self.classes, self.num) = self.sess.run([detection_boxes, detection_scores, detection_classes, num_detections], feed_dict={image_tensor: image_expanded})

    def getRawImage(self):
        return self.image

    def getProcessedImage(self):
        self.sessionRun()
        img = self.image.copy()
        detected = False
        vis_util.visualize_boxes_and_labels_on_image_array(
            img,
            np.squeeze(self.boxes),
            np.squeeze(self.classes).astype(np.int32),
            np.squeeze(self.scores),
            self.category_index,
            use_normalized_coordinates=True,
            line_thickness=3,
            min_score_thresh=0.95)
        if img is not self.image:
            detected = True
            self.counter += 1
            try:
                self.detectedID.append(self.classes[self.scores > 0.95][0])
            except:
                pass
        return detected, img
    
    def getCoordinates(self):
        ymin = int((self.boxes[0][0][0]*240))
        xmin = int((self.boxes[0][0][1]*320))
        ymax = int((self.boxes[0][0][2]*240))
        xmax = int((self.boxes[0][0][3]*320))
        self.boxes = None
        return (ymin, ymax, xmin, xmax)

    def getAveObjectClass(self):
        if len(self.detectedID) < 5:
            return None
        label = max(set(self.detectedID), key=self.detectedID.count)  # Get average detection id
        self.detectedID = []
        if label == 1.0:
            return "Bottle"
        elif label == 2.0:
            return "Damaged-Bottle"
        elif label == 3.0:
            return "Paper"
        elif label == 4.0:
            return "Plastic-Bag"

    def getObjectClass(self):
        label = self.classes[self.scores > 0.95][0]
        if label == 1.0:
            return "Bottle"
        elif label == 2.0:
            return "Damaged-Bottle"
        elif label == 3.0:
            return "Paper"
        elif label == 4.0:
            return "Plastic-Bag"

    def getObjectScore(self):
        return self.scores

    def release(self):
        self.cam.release()

    def rest(self):
        self.counter = 0
        self.detectedID = []
        if self.device == "__PI__":
            self.cam.pause()

class VolumeMeasurement:
    def __init__(self, recog):
        self.recog = recog
        self.coords = None
        self.diameter = None
        self.height = None
        self.volume = 0
        self.aveVol = None
        self.counter = 0
        self.ppmX, self.ppmY = 7.160714286, 7.5

    def getProcessedImage(self):
        detected, img = self.recog.getProcessedImage()
        self.coords = self.recog.getCoordinates()
        if detected:
            obj = self.recog.getObjectClass()
            print("object: ", obj)
            if obj is "Bottle":
                img = self.drawDimensions(img)
        cv2.putText(img, "Volume Detector", (65, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.8,(255, 255, 255), 2)
        return img

    def getVolume(self):
        return self.volume

    def getAveVol(self):
        return self.aveVol

    def getHeight(self):
        return self.height

    def getDiameter(self):
        return self.diameter

    def drawDimensions(self, img):
        (y1, y2, x1, x2) = self.coords
        (tltrX, tltrY) = self.getMidpoint((x1, y1), (x2, y1))
        (blbrX, blbrY) = self.getMidpoint((x1, y2), (x2, y2))
        (tlblX, tlblY) = self.getMidpoint((x1, y1), (x1, y2))
        (trbrX, trbrY) = self.getMidpoint((x2, y1), (x2, y2))

        dA = dist.euclidean((tltrX, tltrY), (blbrX, blbrY))
        dB = dist.euclidean((tlblX, tlblY), (trbrX, trbrY))
        cv2.circle(img, (int(tltrX), int(tltrY)), 2, (255, 0, 0), -1)
        cv2.circle(img, (int(blbrX), int(blbrY)), 2, (255, 0, 0), -1)
        cv2.circle(img, (int(tlblX), int(tlblY)), 2, (255, 0, 0), -1)
        cv2.circle(img, (int(trbrX), int(trbrY)), 2, (255, 0, 0), -1)
    
        cv2.line(img, (int(tltrX), int(tltrY)), (int(blbrX), int(blbrY)), (100, 0, 100), 1)
        cv2.line(img, (int(tlblX), int(tlblY)), (int(trbrX), int(trbrY)), (100, 0, 100), 1)
        self.diameter = dA / self.ppmY
        self.height = dB / self.ppmX
        self.volume += (np.pi)*((self.diameter/2)**2)*(self.height)
        self.counter += 1
        self.aveVol = self.volume / self.counter
        cv2.putText(img, "{:.2f}cm".format(self.height), (int(tltrX - 15), int(tltrY - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
        cv2.putText(img, "{:.2f}cm".format(self.diameter), (int(trbrX + 10), int(trbrY)), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
        cv2.putText(img, "{:.2f}mL".format(self.aveVol), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
    
        return img

    def rest(self):
        self.aveVol, self.vol, self.counter = 0
        self.cam.pause()

    def getMidpoint(self, ptA, ptB):
        return (ptA[0] + ptB[0]) / 2, (ptA[1] + ptB[1]) / 2
                
    

if __name__ == "__main__":
    def getMidpoint(ptA, ptB):
        return (ptA[0] + ptB[0]) / 2, (ptA[1] + ptB[1]) / 2

    recog = ObjectClassifier("__IP__", "http://192.168.1.3:8080/video")
    proc = VolumeMeasurement(recog)
    while True:
        _, img = recog.getProcessedImage()
        if recog.counter > 20:
            break
        cv2.imshow('img', img)
        q = cv2.waitKey(1)
        if q == ord('q'):
            break
    detected = recog.getObjectClass()
    if detected is None:
        print("No object Detected")
    print(detected)
    recog.rest()
    recog.release()
    cv2.destroyAllWindows()
