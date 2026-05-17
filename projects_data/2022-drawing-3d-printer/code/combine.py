import cv2  # Not actually necessary if you just want to create an image.
import numpy as np

height = 1000
width = 1000
import os
arr1 = os.listdir("first")
arr2 = os.listdir("second")
arr1.sort()
arr2.sort()
print(arr1)
frames = []
for file1, file2 in zip(arr1, arr2):
    arr1 = cv2.imread('first\\' + file1, cv2.IMREAD_GRAYSCALE)
    arr2 = cv2.imread('second\\' + file2, cv2.IMREAD_GRAYSCALE)

    
    comb = np.concatenate(( arr2[:,:-225], arr1[:963, 200:]), axis=1)[150:,120:-150]
    frames.append(comb)

blank_image = np.zeros( (comb.shape[0],comb.shape[1]), np.uint8)

blank_image += 255

for i in range(15):
    frames.append(comb)

print(len(frames))
frames.insert(0,blank_image)

frames.insert(0,blank_image)

frames.insert(0,blank_image)
print(len(frames))
##while True:
##    for image in frames:
##        cv2.imshow("base",image)
##        if cv2.waitKey(25) & 0xFF == ord('q'):
##            break
##        pass
##base = cv2.imread('testg.jpg', cv2.IMREAD_GRAYSCALE)
##

fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output.avi',fourcc, 20.0, (comb.shape[1],comb.shape[0]),0)

for image in frames:
    out.write(image)
    
out.release()
