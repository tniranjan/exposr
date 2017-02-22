import cv2
import numpy as np

class Processr(object):
    def __init__(self,filename):
        self.video = cv2.VideoCapture(filename)
        ret, ref_cframe = self.video.read()
        while not(ret):
            ret, ref_cframe = self.video.read()
        ref_frame = cv2.cvtColor(ref_cframe, cv2.COLOR_BGR2GRAY)
        self.ref_frame=cv2.equalizeHist(ref_frame)
        self.orb =  cv2.ORB_create()
        self.kpr, self.desr = self.orb.detectAndCompute(ref_frame,None)
        self.sum_im=np.asarray( ref_cframe[:,:,:])
        [H,W,C]=self.sum_im.shape
        self.pixnum=np.ones((H,W,C))
        self.isImage=0
    def __del__(self):
        self.video.release()

    def get_frame(self):
        ret, cframe = self.video.read()
        if ret:
            frame = cv2.cvtColor(cframe, cv2.COLOR_BGR2GRAY)
            frame=cv2.equalizeHist(frame)
            kp, des = self.orb.detectAndCompute(frame,None)
            bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
            matches = bf.match(des,self.desr)
            matches = sorted(matches, key = lambda x:x.distance)
            src_pts = np.float32([ kp[m.queryIdx].pt for m in matches ]).reshape(-1,1,2)
            dst_pts = np.float32([ self.kpr[m.trainIdx].pt for m in matches ]).reshape(-1,1,2)
            M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC,10.0)
            matchesMask = mask.ravel().tolist()
            h,w = self.ref_frame.shape
            warp = cv2.warpPerspective(cframe, M, (w, h))
            npWarp=np.asarray( warp[:,:,:]).astype('float64')
            self.pixnum[npWarp.nonzero()]=self.pixnum[npWarp.nonzero()]+1
            self.sum_im=self.sum_im+npWarp
            avg=self.sum_im/self.pixnum
            srcerr=np.array([[1,1],[1,1],[1,1]]).astype('float32')
            srcerr=np.array([srcerr])
            dstrr=cv2.perspectiveTransform(srcerr,M)
            avg8=cv2.convertScaleAbs(avg)
            ret, self.jpeg = cv2.imencode('.jpg', avg8)
            self.isImage=1
        else:
            self.isImage=0
        return (self.jpeg.tobytes(),self.isImage)
