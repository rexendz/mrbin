import os
import cv2
import numpy as np
import tensorflow.compat.v1 as tf
import sys
from utils import label_map_util
from utils import visualization_utils as vis_util

try:
    from picam import camera
except ImportError or ImportError:
    print("Failed importing picam.py **THIS IS NORMAL IF RUNNING ON NON-RASPBIAN**")

sys.path.append("..")


class ObjectClassifier:
    # device="__IP__"(IF USING IPWEBCAM) device="__PI__"(IF USING PI CAMERA)
    def __init__(self, device="__PI__", url="0.0.0.0", cam=None):
        self.device = device
        self.cam = None
        if self.device == "__IP__":
            self.cam = cv2.VideoCapture(url)
        else:
            self.cam = cam

        self.boxes, self.scores, self.classes, self.num = None, None, None, None
        self.confidence = None
        self.image = None

        cwd = os.getcwd()
        dir = 'inference_graph'
        ckpt_path = os.path.join(cwd, dir, 'frozen_inference_graph.pb')
        labels_path = os.path.join(cwd, dir, 'labelmap.pbtxt')
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

    def sessionRun(self):
        image_tensor = self.detection_graph.get_tensor_by_name('image_tensor:0')
        detection_boxes = self.detection_graph.get_tensor_by_name('detection_boxes:0')
        detection_scores = self.detection_graph.get_tensor_by_name('detection_scores:0')
        detection_classes = self.detection_graph.get_tensor_by_name('detection_classes:0')
        num_detections = self.detection_graph.get_tensor_by_name('num_detections:0')
        if self.device == "__PI__":
            self.image = self.cam.read()
        else:
            _, self.image = self.cam.read()
        image_expanded = np.expand_dims(self.image, axis=0)
        (self.boxes, self.scores, self.classes, self.num) = self.sess.run([detection_boxes, detection_scores, detection_classes, num_detections], feed_dict={image_tensor: image_expanded})

    def getRawImage(self):
        return self.image

    def getProcessedImage(self):
        img = self.image.copy()
        vis_util.visualize_boxes_and_labels_on_image_array(
            img,
            np.squeeze(self.boxes),
            np.squeeze(self.classes).astype(np.int32),
            np.squeeze(self.scores),
            self.category_index,
            use_normalized_coordinates=True,
            line_thickness=3,
            min_score_thresh=0.80)

        return img

    def getObjectClass(self):
        label = self.classes[0][0]
        if label == 1.0:
            return "Bottle"
            self.classes = None
        elif label == 2.0:
            return "Damaged-Bottle"
            self.classes = None
        elif label == 3.0:
            return "Paper"
            self.classes = None
        elif label == 4.0:
            return "Plastic-Bag"
            self.classes = None

    def getObjectScore(self):
        return self.scores

    def release(self):
        self.cam.release()

    def rest(self):
        if self.device == "__PI__":
            self.cam.pause()

if __name__ == "__main__":
    recog = ObjectClassifier("__IP__", "http://192.168.1.3:8080/video")
    while True:
        recog.sessionRun()
        img = recog.getProcessedImage()
        print(recog.getObjectScore()[0][0])
        cv2.imshow('img', img)
        q = cv2.waitKey(1)
        if q == ord('q'):
            break
    cv2.destroyAllWindows()
    recog.release()
