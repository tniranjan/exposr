import cv2
import numpy as np

class Viewr(object):
    def __init__(self,filename):
        self.video = cv2.VideoCapture(filename)
        ret, ref_cframe = self.video.read()
        while not(ret):
            ret, ref_cframe = cap.read()

    def __del__(self):
        self.video.release()

    def get_frame(self):
        ret, cframe = self.video.read()
        ret, jpeg = cv2.imencode('.jpg', cframe)
        return jpeg.tobytes()
