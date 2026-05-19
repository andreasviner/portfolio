import andy
from mpl_toolkits import mplot3d
import numpy as np
import matplotlib.pyplot as plt
import os 
import cv2  
from PIL import Image  



try:
    os.mkdir(".\\pics\\")
except:
    pass
#andy.count()   
#aa

data = andy.data()
#data.save()
data.sort_remove_duplicate_ids = True
data.config()
#data.refresh_filter()
#data.save()


res = 8
def multi(arr):
    #print(str(hex(arr[0])+ "0")[2:3]+str(hex(arr[0])+ "00")[2:4]+str(hex(arr[0])+ "00")[2:4])
    return [int(arr[0]/(256/res)), int(arr[1]/(256/res)), int(arr[2]/(256/res))]

def de_quality(arr):
    return int(int(arr[0])/(256/res)), int(int(arr[1])/(256/res)), int(int(arr[2])/(256/res))



def sort_by_num(arry):
    a = []
    lowest = 0
    for b in arry:
        for item in arry:
            if int(item.split(".")[0][5:]) == lowest:
                a.append(item)
                lowest += 1
    return a
        

# Video Generating function 
def generate_video(name): 
    image_folder = ".\\pics\\" # make sure to use your folder 
    video_name = '.\\' + name + '.avi'
      
    images = [img for img in os.listdir(image_folder) 
              if img.endswith(".jpg") or
                 img.endswith(".jpeg") or
                 img.endswith("png")] 
     
    # Array images should only consider 
    # the image files ignoring others if any 
    print(images)

    images = sort_by_num(images)

    print(images)
  
    frame = cv2.imread(os.path.join(image_folder, images[0])) 
  
    # setting the frame width, height width 
    # the width, height of first image 
    height, width, layers = frame.shape   
  
    video = cv2.VideoWriter(video_name, 0, 48, (width, height))  
  
    # Appending the images to the video one by one 
    for image in images:  
        video.write(cv2.imread(os.path.join(image_folder, image)))  
      
    # Deallocating memories taken for window creation 
    cv2.destroyAllWindows()  
    video.release()  # releasing the video generated 
  
  
# Calling the generate_video function 
def make_jenter():
    a = []
    for x in range(res):
        a.append([])
        for y in range(res):
            a[-1].append([])
            for z in range(res):
                a[-1][-1].append(0)

    arrr = []

    for item in data.data:
        if item[5] == "j":
            arrr.append(item[8])


    for item in arrr:
        #print(item)
        #print(multi(de_quality(item[3])))
        try:
            a[multi(item[3])[0]][multi(item[3])[1]][multi(item[3])[2]] += 2
            for ite in item[2]:
                a[multi(ite)[0]][multi(ite)[1]][multi(ite)[2]] += 2
            for ite in item[1]:
                a[multi(ite)[0]][multi(ite)[1]][multi(ite)[2]] += 2
            for ite in item[0]:
                if ite not in item[1]:
                    a[multi(ite)[0]][multi(ite)[1]][multi(ite)[2]] += -1
        except Exception as e:
            print(e)
            print(item)
            
    higest = 0
    higest2 = 0

    for x in range(res):
        for y in range(res):
            for z in range(res):
                if a[x][y][z] > higest:
                    higest = a[x][y][z]
                    higest2 = [x,y,z]


    print(higest)




    zdata = []
    xdata = []
    ydata = []
    mdata = []

    for x in range(res):
        xdata.append(x)

    for x in range(res):
        ydata.append(x)

    for x in range(res):
        zdata.append(x)



    fig = plt.figure()
    ax = plt.axes(projection='3d')
    def cto_hex(a):
        return (hex(a)+"0000")[2:4]



    def data_to_color(a,b,c):
        return "#" + cto_hex(a) + cto_hex(b) + cto_hex(c)
    # Data for three-dimensional scattered points






        

    ydata.sort()
    for x in range(res):
        for y in range(res):
            for z in range(res):
                ab = int(a[x][y][z]/(higest/255))
                if ab > 0:
                    ax.scatter(xdata[x], ydata[y], zdata[z], c=("#" + (str(hex(int((255/res)*x)))+"00")[2:4]+(str(hex(int((255/res)*y)))+"00")[2:4]+(str(hex(int((255/res)*z)))+"00")[2:4]), s = ab)
    #plt.show()
    for ii in range(0,360):
        ax.view_init(elev=10, azim=(ii))
        plt.savefig(".\\pics\\movie%d.png" % (ii))
    generate_video("jenter")

def make_gutter():
    a = []
    for x in range(res):
        a.append([])
        for y in range(res):
            a[-1].append([])
            for z in range(res):
                a[-1][-1].append(0)

    arrr = []

    for item in data.data:
        if item[5] == "g":
            arrr.append(item[8])


    for item in arrr:
        #print(item)
        #print(multi(de_quality(item[3])))
        try:
            a[multi(item[3])[0]][multi(item[3])[1]][multi(item[3])[2]] += 2
            for ite in item[2]:
                a[multi(ite)[0]][multi(ite)[1]][multi(ite)[2]] += 2
            for ite in item[1]:
                a[multi(ite)[0]][multi(ite)[1]][multi(ite)[2]] += 2
            for ite in item[0]:
                if ite not in item[1]:
                    a[multi(ite)[0]][multi(ite)[1]][multi(ite)[2]] += -1
        except Exception as e:
            print(e)
            print(item)
            
    higest = 0
    higest2 = 0

    for x in range(res):
        for y in range(res):
            for z in range(res):
                if a[x][y][z] > higest:
                    higest = a[x][y][z]
                    higest2 = [x,y,z]


    print(higest)




    zdata = []
    xdata = []
    ydata = []
    mdata = []

    for x in range(res):
        xdata.append(x)

    for x in range(res):
        ydata.append(x)

    for x in range(res):
        zdata.append(x)



    fig = plt.figure()
    ax = plt.axes(projection='3d')
    def cto_hex(a):
        return (hex(a)+"0000")[2:4]



    def data_to_color(a,b,c):
        return "#" + cto_hex(a) + cto_hex(b) + cto_hex(c)
    # Data for three-dimensional scattered points






        

    ydata.sort()
    for x in range(res):
        for y in range(res):
            for z in range(res):
                ab = int(a[x][y][z]/(higest/255))
                if ab > 0:
                    ax.scatter(xdata[x], ydata[y], zdata[z], c=("#" + (str(hex(int((255/res)*x)))+"00")[2:4]+(str(hex(int((255/res)*y)))+"00")[2:4]+(str(hex(int((255/res)*z)))+"00")[2:4]), s = ab)
    #plt.show()
    for ii in range(0,360):
        ax.view_init(elev=10, azim=(ii))
        plt.savefig(".\\pics\\movie%d.png" % (ii))
    generate_video("gutter")

def make_alder():
    a = []
    for x in range(res):
        a.append([])
        for y in range(res):
            a[-1].append([])
            for z in range(res):
                a[-1][-1].append(0)

    arrr = []

    for item in data.data:
        if item[5] == "g":
            arrr.append(item[8])


    for item in arrr:
        #print(item)
        #print(multi(de_quality(item[3])))
        try:
            a[multi(item[3])[0]][multi(item[3])[1]][multi(item[3])[2]] += 2
            for ite in item[2]:
                a[multi(ite)[0]][multi(ite)[1]][multi(ite)[2]] += 2
            for ite in item[1]:
                a[multi(ite)[0]][multi(ite)[1]][multi(ite)[2]] += 2
            for ite in item[0]:
                if ite not in item[1]:
                    a[multi(ite)[0]][multi(ite)[1]][multi(ite)[2]] += -1
        except Exception as e:
            print(e)
            print(item)
            
    higest = 0
    higest2 = 0

    for x in range(res):
        for y in range(res):
            for z in range(res):
                if a[x][y][z] > higest:
                    higest = a[x][y][z]
                    higest2 = [x,y,z]


    print(higest)




    zdata = []
    xdata = []
    ydata = []
    mdata = []

    for x in range(res):
        xdata.append(x)

    for x in range(res):
        ydata.append(x)

    for x in range(res):
        zdata.append(x)



    fig = plt.figure()
    ax = plt.axes(projection='3d')
    def cto_hex(a):
        return (hex(a)+"0000")[2:4]



    def data_to_color(a,b,c):
        return "#" + cto_hex(a) + cto_hex(b) + cto_hex(c)
    # Data for three-dimensional scattered points



        

    ydata.sort()
    for x in range(res):
        for y in range(res):
            for z in range(res):
                ab = int(a[x][y][z]/(higest/255))
                if ab > 0:
                    ax.scatter(xdata[x], ydata[y], zdata[z], c=("#" + (str(hex(int((255/res)*x)))+"00")[2:4]+(str(hex(int((255/res)*y)))+"00")[2:4]+(str(hex(int((255/res)*z)))+"00")[2:4]), s = ab)
    #plt.show()
    for ii in range(0,360):
        ax.view_init(elev=10, azim=(ii))
        plt.savefig(".\\pics\\movie%d.png" % (ii))
    generate_video("alder")
    
#make_gutter()
make_jenter()
