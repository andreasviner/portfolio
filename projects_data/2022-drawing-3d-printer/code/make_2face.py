import cv2  # Not actually necessary if you just want to create an image.
import numpy as np

arr = cv2.imread('testg.jpg', cv2.IMREAD_GRAYSCALE)

arr = arr >>5
arr = arr << 5

cv2.imshow("base",arr)
