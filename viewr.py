import cv2
import numpy as np

class Viewr(object):
    def __init__(self,filename):
        self.video = cv2.VideoCapture(filename)
        ret, ref_cframe = self.video.read()
        while not(ret):
            ret, ref_cframe = self.video.read()
        self.isImage=0

    def __del__(self):
        self.video.release()

    def get_frame(self):
        ret, cframe = self.video.read()
        if ret:
            ret, self.jpeg = cv2.imencode('.jpg', cframe)
            self.isImage=1
        else:
            self.isImage=0
        return (self.jpeg.tobytes(),self.isImage)
