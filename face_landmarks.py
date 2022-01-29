import cv2
import numpy as np
import dlib
import time

class FaceLandMarkPts:
    def __init__(self):
        # Landmark detector
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
    
    def get_landmark_pts(self, img):
        # Face 1
        img1_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.detector(img1_gray)
        face = faces[0]
        landmarks = self.predictor(img1_gray, face)
        landmarks_points = []
        for n in range(0, 68):
            x = landmarks.part(n).x
            y = landmarks.part(n).y
            landmarks_points.append((x, y))
        
        return landmarks_points