from multiprocessing import Process
from multiprocessing import Queue
import numpy as np
import imutils
import cv2
import os


class ObjectClassifier:
    # device="__IP__"(IF USING IPWEBCAM) device="__PI__"(IF USING PI CAMERA)
    def __init__(self, device="__PI__", cam=None):
        self.device = device
        self.userpath = os.getenv("HOME")
        self.cam = cam
        self.CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
                        "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
                        "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
                        "sofa", "train", "tvmonitor"]
        self.COLORS = np.random.uniform(0, 255, size=(len(self.CLASSES), 3))
        self.inputQueue = Queue(maxsize=1)
        self.outputQueue = Queue(maxsize=1)
        self.detections = None
        self.idx = None
        self.detectedID = []
        self.numDetections = 0

    def getRawImage(self):
        _, frame = self.cam.read()
        return frame

    def start(self):
        proto_path = self.userpath + '/mrbin/MobileNetSSD/MobileNetSSD_deploy.prototxt.txt'
        caffe_path = self.userpath + '/mrbin/MobileNetSSD/MobileNetSSD_deploy.caffemodel'
        net = cv2.dnn.readNetFromCaffe(proto_path, caffe_path)
        p = Process(target=self.classify_frame, args=(net, self.inputQueue, self.outputQueue,))
        p.daemon = True
        p.start()

    def getProcessedImage(self):
        if self.device == "__IP__":
            _, frame = self.cam.read()
        else:
            frame = self.cam.read()
        frame = imutils.resize(frame, width=320)
        (fH, fW) = frame.shape[:2]

        if self.inputQueue.empty():
            self.inputQueue.put(frame)

        if not self.outputQueue.empty():
            self.detections = self.outputQueue.get()

        if self.detections is not None:
            for i in np.arange(0, self.detections.shape[2]):
                confidence = self.detections[0, 0, i, 2]

                if confidence < 0.2:
                    continue

                self.idx = int(self.detections[0, 0, i, 1])
                dims = np.array([fW, fH, fW, fH])
                box = self.detections[0, 0, i, 3:7] * dims
                (startX, startY, endX, endY) = box.astype("int")

                label = "{}: {:.2f}%".format(self.CLASSES[self.idx], confidence * 100)
                cv2.rectangle(frame, (startX, startY), (endX, endY), self.COLORS[self.idx], 2)
                y = startY - 15 if startY - 15 > 15 else startY + 15
                cv2.putText(frame, label, (startX, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.COLORS[self.idx], 2)
                self.numDetections += 1
                self.detectedID.append(self.idx)

        cv2.putText(frame, "Object Classifier", (65, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        return frame

    def classify_frame(self, net, inputQueue, outputQueue):
        while True:
            if not inputQueue.empty():
                frame = inputQueue.get()
                frame = cv2.resize(frame, (300, 300))
                blob = cv2.dnn.blobFromImage(frame, 0.007843, (300, 300), 127.5)

                net.setInput(blob)
                detections = net.forward()

                outputQueue.put(detections)

    def getDetection(self):
        classID = max(set(self.detectedID), key=self.detectedID.count)
        self.idx = None
        if classID is not None:
            return self.CLASSES[classID]

    def release(self):
        self.cam.release()

    def rest(self):
        self.numDetections = 0
        if self.device == "__PI__":
            self.cam.pause()


if __name__ == "__main__":
    recog = ObjectClassifier("__IP__", 0)
    recog.start()
    while True:
        img = recog.getProcessedImage()
        cv2.imshow('img', img)
        q = cv2.waitKey(1)
        if q == ord('q'):
            break
        print(recog.getDetection())
    cv2.destroyAllWindows()
    recog.release()
