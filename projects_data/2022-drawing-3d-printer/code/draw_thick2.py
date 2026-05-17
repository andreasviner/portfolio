import cv2  # Not actually necessary if you just want to create an image.
import numpy as np

height = 1000
width = 1000

base = cv2.imread('testss.jpg', cv2.IMREAD_GRAYSCALE)
height,width = base.shape
#base = cv2.resize(base, dsize=(int(height/4), int(width/4)), interpolation=cv2.INTER_CUBIC)
##temp = cv2.GaussianBlur(base, (3,3), 0) 
##img_blur = cv2.GaussianBlur(temp, (3,3), 0)
##
##edges = cv2.Canny(image=img_blur, threshold1=70, threshold2=150)
##base = 255-edges
##cv2.imshow('Canny Edge Detection', base)
##cv2.waitKey(0)
##
base = np.pad(base,pad_width=200,mode="constant",constant_values = 255)

height,width = base.shape


start = np.where(base == np.amin(base))


force = np.array([0.9,0.])
position = [start[0][0],start[1][0]]
rot_arr = np.array([0.9,0.])


def get_score(arr,test_v,rot_vec):
    #if np.sum(np.linalg.norm(test_v/test_v)/2) < np.sum(test_v)/2:
     #   force = np.linalg.norm(test_v/test_v)/2

    sum_ = 0
    p = [101,101]
    for i in range(5):
        #sum_ += 255-arr[int(p[0]),int(p[1])]
        arr[int(p[0]),int(p[1])] = 255
        
        p += test_v
        test_v = np.dot(rot_vec, test_v)
    #cv2.imshow("base",arr)
    #cv2.waitKey(25)
    #return sum_

    
    return np.sum(np.absolute(arr-127))


from math import cos, sin

def update_force(arr,force2):
    global force
    global rot_arr
    base_shiit = [0.1,0]
    theta = np.deg2rad(-60)
    rot = np.array([[cos(theta), -sin(theta)], [sin(theta), cos(theta)]])
    force2 = np.dot(rot,force2)

    theta = np.deg2rad(2)
    rot = np.array([[cos(theta), -sin(theta)], [sin(theta), cos(theta)]])
    
    best = 0

    
    for i in range(60):
        force2 = np.dot(rot,force2)
        for i in range(10):
            
            #base_shiit = np.dot(rot,base_shiit)
            #score = get_score(np.copy(arr),np.copy(force2+base_shiit))
            theta = np.deg2rad((i-5+0.5))
            rot2 = np.array([[cos(theta), -sin(theta)], [sin(theta), cos(theta)]])

        
            score = get_score(np.copy(arr),np.copy(force2),rot2)
            
            if score > best:
                #print(i)
                best = score
                force = force2.copy()
                rot_arr = rot2.copy()


        




blank_image = np.zeros((height,width,3), np.uint8)

blank_image += 255


##for i in range(100):
##    blank_image[int(position[0]),int(position[1])] = (0,0,0)
##    position[0] += force[0]
##    position[1] += force[1]
##    force[0] += 0.001

#blank_image[:,0:width//2] = (255,0,0)      # (B, G, R)
#blank_image[:,width//2:width] = (0,255,0)


loop_nr = 0

while True:
    loop_nr += 1
    update_force(base[ int(position[0]-100) : int(position[0]+100) , int(position[1]-100) : int(position[1]+100) ], force)

    
    #if np.sum(np.linalg.norm(force/force)/2) < np.sum(force)/2:
        #print("DID")
        #force = np.linalg.norm(force/force)/2
        
    if 0 == 0:
        cv2.imshow("base",blank_image)
    if cv2.waitKey(25) & 0xFF == ord('q'):
        break


    for a in range(2):
        blank_image[int(position[0]),int(position[1])] = blank_image[int(position[0]),int(position[1])]*0.8
        base[int(position[0]),int(position[1])] = 255
        #base[int(position[0]-3):int(position[0]+4),int(position[1]-3):int(position[1]+4)]  = 255
        #print(base[int(position[0]-2):int(position[0]+3),int(position[1]-2):int(position[1]+3)])
        #print(int(position[0]+3))
        position += force
        force = np.dot(rot_arr, force)
        #print(force)

    #print(loop_nr)

    
    


    #print(force)

cv2.imshow("base",blank_image)
cv2.waitKey(0)
