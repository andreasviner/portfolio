import cv2  # Not actually necessary if you just want to create an image.
import numpy as np

height = 1000
width = 1000

base = cv2.imread('testss.jpg', cv2.IMREAD_GRAYSCALE)
temp = cv2.GaussianBlur(base, (3,3), 0) 
img_blur = cv2.GaussianBlur(temp, (3,3), 0) 
# Canny Edge Detection
for i in range(20):
    edges = cv2.Canny(image=img_blur, threshold1=70, threshold2=150) # Canny Edge Detection
    cv2.imshow('Canny Edge Detection', edges)




    cv2.waitKey(0)
