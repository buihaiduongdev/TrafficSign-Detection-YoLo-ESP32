import cv2
import numpy as np


class DistanceEstimator:
    def __init__(self, focal_length=800, real_width=1.2):
        self.focal_length = focal_length
        self.real_width = real_width
        
        print(f"   DistanceEstimator initialized")
        print(f"   Focal Length: {self.focal_length:.2f}")
        print(f"   Real Width: {self.real_width}m")
    
    def estimate_distance(self, bbox_width_pixels):
        if bbox_width_pixels <= 0:
            return float('inf')
        
        distance = (self.real_width * self.focal_length) / bbox_width_pixels
        return distance

