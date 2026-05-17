import cv2  # Not actually necessary if you just want to create an image.
import numpy as np

height = 1000
width = 1000





def bnw_color(main_arr, barr, carr):
    height,width = main_arr.shape
    barr = barr.astype(np.int16)
##    print(carr)
##    print(barr)
##    print(main_arr[0][0])
##    print(np.absolute(barr-main_arr[0][0]))
##    aa
    ret_arr = np.zeros((height,width,3), np.uint8)

    for x in range(len(main_arr)):
        for y in range(len(main_arr[0])):
            #print(np.amin(np.absolute(barr-main_arr[x][y])))
            ret_arr[x][y] = carr[np.where(np.absolute(barr-main_arr[x][y]) == np.amin(np.absolute(barr-main_arr[x][y])))[0][0]]

    return ret_arr
        


colors = [[
[113,55,149],
[96,67,147],
[173,93,130],
[186,121,155],
[133,41,54],
[152,63,67],
[158,89,48],
[202,179,120],
[201,203,70],
[45,59,159],
[77,95,109],
[58,110,176]],[
[90,125,146],
[104,155,176],
[118,125,58],
[142,178,52],
[60,98,77],
[95,71,93],
[109,83,70],
[125,100,70],
[187,156,104],
[81,79,92],
[142,145,150],
[38,43,45]
]]

colors = np.array(colors).astype(np.uint8)
colors_color = cv2.cvtColor(colors, cv2.COLOR_RGB2BGR)
colors_gray = cv2.cvtColor(colors, cv2.COLOR_RGB2GRAY)
colors_color.shape = (24,3)
colors_gray.shape = (24,1)
##p = colors_gray.flatten().argsort()
##print(p)
##colors_color.shape = (24,3)
##c = colors_color[p]
##c.shape = (12,2,3)
###colors_color.astype(np.uint8)
##
##base = cv2.resize(c.astype(np.uint8), dsize=(500, 500), interpolation=cv2.INTER_AREA)
###colors = cv2.cvtColor(base.astype(np.uint8), cv2.COLOR_BGR2GRAY)
##cv2.imshow("image", base)
##cv2.waitKey()

base = cv2.imread('test3.jpg', cv2.IMREAD_GRAYSCALE)
img = bnw_color(base,colors_gray,colors_color)
cv2.imshow("image",img)
cv2.waitKey()
print(base.shape)
orgx = base.shape[0]
orgy = base.shape[1]
base = cv2.resize(base, dsize=(3000, 4769), interpolation=cv2.INTER_CUBIC)
#blank_image = np.zeros((height,width,3), np.uint8)
##temp = cv2.GaussianBlur(base, (3,3), 0) 
##img_blur = cv2.GaussianBlur(temp, (3,3), 0)
##
##edges = cv2.Canny(image=img_blur, threshold1=70, threshold2=150)
##base = 255-edges
##cv2.imshow('Canny Edge Detection', base)
##cv2.waitKey(0)
##
#base = np.pad(base,pad_width=200,mode="constant",constant_values = 255)

import matplotlib.pyplot as plt
#plt.plot([1,2,3,4], [1,4,9,16], 'ro')
#plt.axis([0, 6, 0, 20])
#plt.show()

from random import randint

place = 0
X = []
Y = []
for i in range(len(base)):
    place = randint(0,255)
    #place = i%2 * 1000
    for x in range(len(base[i])):
        place += ((255-int(base[i][x]))**3)/(255**3)*2
        if place > 255:
            place -= 255
            X.append(x)
            Y.append(len(base)-i)

print(len(X))
print(max(X))
print(max(Y))
print(min(X))
print(min(Y))
plt.plot(X,Y,'ro')

plt.show()

def sort_list_cool_style(arr1,arr2):

    global Y
    rx = []
    ry = []
    lx = arr1[0]
    ly = arr2[0]
    bd = 0
    for i in range(len(arr1)):
        points_x = np.array(arr1)
        points_y = np.array(arr2)
        dist = np.sqrt((points_x-lx)**2 + (points_y-ly)**2)
        best = np.argmin(dist)
        #print(dist[best])

        lx = arr1.pop(best)
        ly = arr2.pop(best)
        rx.append(lx)
        ry.append(ly)

    return rx, ry

print("AA")
print(len(X))
X, Y = sort_list_cool_style(X,Y)
print(len(X))

with open("out.gcode", "w") as file:
    file.write("G91\n")
    cx = 0
    cy = 0
    for x,y in zip(X,Y):
        file.write("G0 X" + str(((x-cx)/3000)*210) + " Y" + str(((y-cy)/4769)*210))

        file.write("\nG0 Z-2.5\nG0 Z2.5\n")
        cx = x
        cy = y
        #base[i][x] = base[i][x] // 8
        #base[i][x] *= 8
##        if base[i][x] == last:
##            count += -1
##        else:
##            last = base[i][x]
##            count = -1
##
##        if count == -1:
##            count = base[i][x]
##            base[i][x] = 0
##        else:
##            base[i][x] = 255
##        if randint(0,base[i][x]>>5+1) == 0 and base[i][x] != 224:
##            base[i][x] = 0
##        else:
##            base[i][x] = 255

base = cv2.resize(base, dsize=(orgy, orgx), interpolation=cv2.INTER_CUBIC) 
cv2.imshow("base",base)
cv2.waitKey(0)
