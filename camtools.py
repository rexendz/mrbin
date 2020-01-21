import cv2
import numpy as np

pts = [(26, 34), (278, 26), (291, 188), (17, 191)]
pts = np.array(pts, dtype = "float32")

def order_points(pts):
    rect = np.zeros((4, 2), dtype = "float32")
    s = pts.sum(axis = 1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]

    diff = np.diff(pts, axis = 1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    
    return rect

def four_point_transform(image, pts):
    rect = order_points(pts)
    (tl, tr, br, bl) = rect
 

    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))


    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))

    dst = np.array([
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1]], dtype = "float32")

    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
 
    return warped


def getCropped(frame):
    warped = four_point_transform(frame, pts)
    return warped

if __name__ == "__main__":
    refPt = []
    def onClick(event, x, y, flags, param):
        global refPt
        if event == cv2.EVENT_LBUTTONDOWN:
            refPt.append((x, y))
            print(refPt)

    
    from picam import camera
    cam = camera().start()
    import time
    cv2.namedWindow('img')
    cv2.setMouseCallback('img', onClick)
    time.sleep(1)
    while True:
        img = cam.read()
        warped = four_point_transform(img, pts)
        cv2.imshow('warped', warped)
        cv2.imshow('img', img)
        q = cv2.waitKey(1)
        if q == ord('q'):
            break
    cam.close()
    cv2.destroyAllWindows()
        

