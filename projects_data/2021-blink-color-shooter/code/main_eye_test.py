import pygame
import win32api
import win32con
import win32gui
import pyautogui
import loading_screen
import sprites
from random import randint
from scipy.spatial import distance as dist
from imutils.video import FileVideoStream
from imutils.video import VideoStream
from imutils import face_utils
import numpy as np
import argparse
import imutils
import time
import dlib
import cv2
from threading import Thread


def eye_aspect_ratio(eye):
    # compute the euclidean distances between the two sets of
    # vertical eye landmarks (x, y)-coordinates
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])

    # compute the euclidean distance between the horizontal
    # eye landmark (x, y)-coordinates
    C = dist.euclidean(eye[0], eye[3])

    # compute the eye aspect ratio
    ear = (A + B) / (2.0 * C)

    # return the eye aspect ratio
    return ear

print("[INFO] loading facial landmark predictor...")


# grab the indexes of the facial landmarks for the left and
# right eye, respectively

# vs = VideoStream(usePiCamera=True).start()
print("HII")

array = np.zeros(1000)

eye_open = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

def get_blinks_thread():
    global eye_open
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor("big.dat")

    (lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
    (rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

    vs = VideoStream(src=0).start()
    # loop over frames from the video stream
    i = 0
    a = 0
    while True:
        a += 1
        if a == 1000:
            print("LOL")
        # if this is a file video stream, then we need to check if
        # there any more frames left in the buffer to process

        # grab the frame from the threaded video file stream, resize
        # it, and convert it to grayscale
        # channels)
        frame = vs.read()
        frame = imutils.resize(frame, width=450)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # detect faces in the grayscale frame
        rects = detector(gray, 0)

        # loop over the face detections
        for rect in rects:
            # determine the facial landmarks for the face region, then
            # convert the facial landmark (x, y)-coordinates to a NumPy
            # array
            shape = predictor(gray, rect)
            shape = face_utils.shape_to_np(shape)

            # extract the left and right eye coordinates, then use the
            # coordinates to compute the eye aspect ratio for both eyes
            leftEye = shape[lStart:lEnd]
            rightEye = shape[rStart:rEnd]
            leftEAR = eye_aspect_ratio(leftEye)
            rightEAR = eye_aspect_ratio(rightEye)

            # average the eye aspect ratio together for both eyes
            ear = (leftEAR + rightEAR)
            #a.append(100)
            
            #print(ear)
            #print(np.average(array))
            
            if np.average(array) > ear*1.1:
                
                if leftEAR < rightEAR:
                    eye_open.append(1)
                else:
                    eye_open.append(2)
            else:
                eye_open.append(0)
                i += 1
                array[i%1000] =  ear
            eye_open.pop(0)
            

def get_what_eye():
    arr = [0,0,0]

    
    for i in range(len(eye_open)):
        arr[eye_open[i]] += i+3
    if eye_open[-1] == 0 :
        return 0
    if arr[1]> arr[2]:
        return 1
    return 2
    


        
        
#########################################################################
#########################################################################
#########################################################################


clock = pygame.time.Clock()
arrow_size = 300
inited = loading_screen.init(arrow_size)
pygame.init()

screen = pygame.display.set_mode((0, 0),pygame.NOFRAME,pygame.FULLSCREEN) # For borderless, use pygame.NOFRAME
infoObject = pygame.display.Info()
SCREENWIDTH = infoObject.current_w
SCREENHEIGHT = infoObject.current_h
render = 1000

thread1 = Thread( target=get_blinks_thread )
thread1.start()

for i in range(1000):
    #print(eye_open)
    loading_screen.pattern(screen,(255,255,255),(0,0,0),SCREENWIDTH,SCREENHEIGHT,inited,arrow_size, i,2)
    pygame.display.update()
    clock.tick(60)
        #MÅ SENDE OG READE FRA SOCKET I DENNE

while True:

    pygame.draw.rect(screen, (255,0,0), pygame.Rect(0,0, SCREENWIDTH/2, SCREENHEIGHT))
    pygame.draw.rect(screen, (0,0,255), pygame.Rect(SCREENWIDTH/2,0, SCREENWIDTH/2, SCREENHEIGHT))
    print(eye_open)
    
    if get_what_eye() == 1:
        pygame.draw.rect(screen, (0,255,0), pygame.Rect(SCREENWIDTH/2,0, SCREENWIDTH/2, SCREENHEIGHT))
    elif get_what_eye() == 2:
        pygame.draw.rect(screen, (0,255,0), pygame.Rect(0,0, SCREENWIDTH/2, SCREENHEIGHT))
        
    pygame.display.flip()
    
    pygame.display.update()
    clock.tick(60)
    

pygame.quit()
vs.stop()
