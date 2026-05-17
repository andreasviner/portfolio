import pygame
import pygame.math
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
import sprites
import shop
import socket,pickle

s = socket.socket()        


def recv_data(c):
    nr = int(c.recv(3),16)
    data = c.recv(nr)
    while len(data) != nr:
        data += c.recv(nr-len(data))
    return pickle.loads(data)

def send_data(c,arr):
    msg = pickle.dumps(arr)
    nr = hex(len(msg))[2:]
    c.send(("0"*(3-len(nr))+nr).encode()+msg)
    
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

array = np.zeros(20)

eye_open = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
night_mode = False
def get_blinks_thread():
    global eye_open
    global night_mode
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor("big.dat")

    (lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
    (rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

    vs = VideoStream(src=0).start()
    # loop over frames from the video stream
    i = 0
    a = 0
    last_z = 0
    while True:
        a += 1
        last_z += 1
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
            
            if np.average(array) > ear*1.2:
                eye_open.append(1)
                if last_z > 1:
                    night_mode = not night_mode
                last_z = 0
            else:
                eye_open.append(0)
                
            i += 1
            array[i%len(array)] =  ear
            eye_open.pop(0)
            

def get_what_eye():
    if eye_open[-1] == 0 :
        return 0
    return 1

    




def get_data_thread():
    while True:
        data0 = recv_data(s)
        whaa = data0[0]
        data = data0[1]
        #0 = player, 1 = proj
        if data[0] not in id_indexes:
            id_indexes.append(data[0])
            other_player_sprites.append(data)
            what_indexes.append(0)

        #print(data)
        #print("\n")

        if what_indexes[id_indexes.index(data[0])] < whaa:
            what_indexes[id_indexes.index(data[0])] = whaa
            other_player_sprites[id_indexes.index(data[0])] = data
                
        for proj in data[5]:
            if proj[5]:
                projectiles_n.add(sprites.Projectile(proj[0],proj[1],proj[2],proj[3],proj[4],proj[5],proj[6],proj[7],proj[8],proj[9]))
            else:
                 projectiles.add(sprites.Projectile(proj[0],proj[1],proj[2],proj[3],proj[4],proj[5],proj[6],proj[7],proj[8],proj[9]))
                    
        

        
        
#########################################################################
#########################################################################
#########################################################################

def check_collide():
    if player.penalty == 0:
        if night_mode:
            for item in pygame.sprite.spritecollide(player, objects_n, False,  pygame.sprite.collide_mask):
                print(player.penalty)
                item.hurt()
                player.penalty = 10
                return
        else:
            for item in pygame.sprite.spritecollide(player, objects, False,  pygame.sprite.collide_mask):
                item.hurt()
                player.penalty = 10
                return

def number_pressed(what):
    global points_val 
    if points_val != 0:
        if player.spent_arr[what-1] < 21:
            points_val += -1
            player.data[what-1] += player_modifier_arr[what-1]
            player.spent_arr[what-1] += 1
        
        
def get_mouse_angle():
    v3 = pygame.Vector2()
    x, y = pygame.mouse.get_pos()
    v3.xy = (x-player.x+offset[0],y-player.y+offset[1])
    return v3.angle_to((0,1))

id_indexes = []
what_indexes = []
other_player_sprites = []

player_modifier_arr = [0.25,5,1,-1,1,0.25,-0.04,1,0.25]



all_sprites = pygame.sprite.Group()
projectiles = pygame.sprite.Group()
projectiles_n = pygame.sprite.Group()
objects_n = pygame.sprite.Group()
objects = pygame.sprite.Group()

shoot_place = [[[((50,20),0,0)]],
                [[((50,15),0,0),((50,85),180,0)],[((50,20),0,0)],[((50,20),0,1)],[((60,15),0,0),((40,15),0,0)]],
                [[((50,20),0,2)],[((60,15),0,1),((40,15),0,1)],[((50,10),0,1)],[((34,20),0,0),((50,10),0,0),((66,20),0,0)],[((50,10),0,0),((50,90),180,0)],[((50,10),0,0),((10,50),90,0),((50,90),180,0),((90,50),270,0)],
                 [((60,10),0,0),((40,10),0,0),((60,90),180,0),((40,90),180,0)],[((50,10),0,1),((50,90),180,1)],[((50,10),0,1),((38,90),180,0),((62,90),180,0)],[((56,10),0,0),((44,10),0,0)]]
                ]

player = sprites.Player()



port = 1337
s.connect(('51.175.184.127', port))
data = recv_data(s)
my_id = data[0]
player.x = data[1][0]
player.y = data[1][1]
arr = ([0, "first"])

#data_string = pickle.dumps(arr)
#s.send(data_string)


#arr = pickle.loads(s.recv(1024))
print(arr)



all_sprites.add(player)
for i in range(1000):

    if randint(0,1):
        objects_n.add(sprites.Object((randint(0,5000),randint(0,5000)), randint(4,9), 1))
    else:
        objects.add(sprites.Object((randint(0,5000),randint(0,5000)), randint(4,9), 0))

  
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

thread2 = Thread( target=get_data_thread )
thread2.start()

screen_min_cords = (-100,-100)
screen_max_cords = (5100-SCREENWIDTH,5100-SCREENHEIGHT)
offset = [1000,1000]

for i in range(200):
    #print(eye_open)
    loading_screen.pattern(screen,(255,255,255),(0,0,0),SCREENWIDTH,SCREENHEIGHT,inited,arrow_size, i,2)
    pygame.display.update()
    clock.tick(60)
        #MÅ SENDE OG READE FRA SOCKET I DENNE





current_cooldown = 0
points = 0
points_val = 0
loop_nr = 0
while True:
    loop_nr += 1
    if points > 10:
        points += -10

        points_val += 1
    current_cooldown += 1
    events = pygame.event.get()

    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                number_pressed(1)
            elif event.key == pygame.K_2:
                number_pressed(2)
            elif event.key == pygame.K_3:
                number_pressed(3)
            elif event.key == pygame.K_4:
                number_pressed(4)
            elif event.key == pygame.K_5:
                number_pressed(5)
            elif event.key == pygame.K_6:
                number_pressed(6)
            elif event.key == pygame.K_7:
                number_pressed(7)
            elif event.key == pygame.K_8:
                number_pressed(8)
            elif event.key == pygame.K_9:
                number_pressed(9)
                
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.pos[0]  > SCREENWIDTH-110:
                shop2 = (shop.check(event.pos,SCREENWIDTH, player.lvl))
                if shop2 != 1000:
                    #player.change_color(night_mode)
                    player.lvl[0] += 1
                    player.lvl[1] = shop2

            
    #print(eye_open)

    player.change_color(night_mode)



    
    keys_pressed = pygame.key.get_pressed()
    v = pygame.Vector2()
    if keys_pressed[pygame.K_a]:
        v.x += -1

    if keys_pressed[pygame.K_d]:
        v.x += 1

    if keys_pressed[pygame.K_w]:
        v.y += -1

    if keys_pressed[pygame.K_s]:
        v.y += 1

    send_pro = []
    if pygame.mouse.get_pressed(3)[0]:
    #if keys_pressed[pygame.K_SPACE]:
        if current_cooldown > player.data[3]:
            current_cooldown = 0
            x2, y2 = pygame.mouse.get_pos()
            
            if night_mode:
                for item in shoot_place[player.lvl[0]][player.lvl[1]]:
                    v2 = pygame.Vector2()
                    v2.xy = item[0]
                    v2.x += -50
                    v2.y += -50

                    ang = get_mouse_angle()

                    if  ang != 0:
                        v2 = v2.rotate(ang)

                    projectiles_n.add(sprites.Projectile((x2-player.x+offset[0],y2-player.y+offset[1]),(player.x+v2[0],player.y-v2[1]),item[2],0.5,player.data[5],night_mode,offset,item[1],player.data[4],my_id))
                    send_pro.append(((x2-player.x+offset[0],y2-player.y+offset[1]),(player.x+v2[0],player.y-v2[1]),item[2],0.5,player.data[5],night_mode,offset,item[1],player.data[4],my_id))
                    
            else:
                for item in shoot_place[player.lvl[0]][player.lvl[1]]:
                    v2 = pygame.Vector2()
                    v2.xy = item[0]
                    v2.x += -50
                    v2.y += -50

                    ang = get_mouse_angle()

                    if  ang != 0:
                        v2 = v2.rotate(ang)

                    projectiles.add(sprites.Projectile((x2-player.x+offset[0],y2-player.y+offset[1]),(player.x+v2[0],player.y-v2[1]),item[2],0.5,player.data[5],night_mode,offset,item[1],player.data[4],my_id))
                    send_pro.append(((x2-player.x+offset[0],y2-player.y+offset[1]),(player.x+v2[0],player.y-v2[1]),item[2],0.5,player.data[5],night_mode,offset,item[1],player.data[4],my_id))
                    
    if v.length() != 0:
        v = v.normalize()
        player.move(v[0],v[1])


    #SCREEN LOGIC
    if player.x-offset[0] > SCREENWIDTH/1.618 and offset[0] < screen_max_cords[0]:
        offset[0] += player.x-offset[0]-SCREENWIDTH/1.618
        if offset[0] > screen_max_cords[0]:
            offset[0] = screen_max_cords[0]

    elif player.x-offset[0] < SCREENWIDTH-SCREENWIDTH/1.618 and offset[0] > screen_min_cords[0]:
        offset[0] += player.x-offset[0]-SCREENWIDTH+SCREENWIDTH/1.618
        if offset[0] < screen_min_cords[0]:
            offset[0] = screen_min_cords[0]

    if player.y-offset[1] > SCREENHEIGHT/1.618 and offset[1] < screen_max_cords[1]:
        offset[1] += player.y-offset[1]-SCREENHEIGHT/1.618
        if offset[1] > screen_max_cords[1]:
            offset[1] = screen_max_cords[1]

    elif player.y-offset[1] < SCREENHEIGHT-SCREENHEIGHT/1.618 and offset[1] > screen_min_cords[1]:
        offset[1] += player.y-offset[1]-SCREENHEIGHT+SCREENHEIGHT/1.618
        if offset[1] < screen_min_cords[1]:
            offset[1] = screen_min_cords[1]


    #LAGGY BIT
    for sprite in objects_n:
        #print(sprite.rect.x)
        if  SCREENWIDTH + render > sprite.rect.x > -render and SCREENHEIGHT + render > sprite.rect.y > -render:
            for item in pygame.sprite.spritecollide(sprite, projectiles_n, True,  pygame.sprite.collide_mask):
                points += 3 + player.data[4]
                sprite.hurt()

    for sprite in objects:
        if  SCREENWIDTH + render > sprite.rect.x > -render and SCREENHEIGHT + render > sprite.rect.y > -render:
            for item in pygame.sprite.spritecollide(sprite, projectiles, True,  pygame.sprite.collide_mask):
                points += 3 + player.data[4]
                sprite.hurt()

    if night_mode:
        for item in pygame.sprite.spritecollide(player, projectiles_n, False,  pygame.sprite.collide_mask):
            if item.id != my_id:
                item.kill()
                player.data[1] += -item.dmg
                if player.data[1] < 1:
                    player.reset()
    else:      
        for item in pygame.sprite.spritecollide(player, projectiles, False,  pygame.sprite.collide_mask):
            if item.id != my_id:
                item.kill()
                player.data[1] += -item.dmg
                if player.data[1] < 1:
                    player.reset()
                    
    check_collide()

    

    projectiles.update(offset)
    projectiles_n.update(offset)
    all_sprites.update(offset)
    objects_n.update(offset)
    objects.update(offset)

    # Draw / render
    screen.fill((255,255,255))
    projectiles.draw(screen)
    projectiles_n.draw(screen)
    all_sprites.draw(screen)
    objects.draw(screen)
    objects_n.draw(screen)
    
    #if pygame.sprite.collide_mask(player,enemies[0]) != None:
        #screen.fill((0,0,0))
    shop.update(player.spent_arr)
    shop.update_upgrade(night_mode,SCREENWIDTH,player.lvl)
    shop.draw(screen)

    for arr in other_player_sprites:
        sprites.draw_player(screen, arr, offset)
        
    #other_players.draw(screen)

    shop.draw_upgrade(screen, SCREENWIDTH)
    sprites.draw_hp(screen,(player.x-offset[0]-50,player.y-offset[1]+50),player.data[1],night_mode)
    #pygame.draw.rect(screen,(255,0,0),(player.x-5-offset[0],player.y-5-offset[1],10,10))
    pygame.display.flip()
    
    pygame.display.update()
    
    #id, update.,
    send_data(s,[loop_nr,[my_id, player.lvl, night_mode, (player.x,player.y),player.angle, send_pro,player.data[1]]])
    clock.tick(60)
    

pygame.quit()
vs.stop()
