from soco import SoCo, discover
import time
import RPi.GPIO as GPIO

Relay_Ch1 = 26
Relay_Ch2 = 20
Relay_Ch3 = 21

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(Relay_Ch1,GPIO.OUT)
GPIO.setup(Relay_Ch2,GPIO.OUT)
GPIO.setup(Relay_Ch3,GPIO.OUT)



def time_sec(st):
    arr = st.split(":")
    return int(arr[0])*60*60 + int(arr[1])*60 + int(arr[2])

rattling = [15.68, 18.6, 31.16, 34.83, 47.17, 52.065, 64.32, 70.21, 82.72, 89.29, 101.50, 109.20, 121.31, 129.32, 141.95,
            150.92, 163.53, 173.41, 186.19, 196.02, 208.19, 220.28, 232.32, 244.91, 257.25, 270.88, 282.78, 296.01]

def flight_red():
    print("LIGHT RED")
    GPIO.output(Relay_Ch3,GPIO.HIGH)
    GPIO.output(Relay_Ch1,GPIO.LOW)
    GPIO.output(Relay_Ch2,GPIO.LOW)

def flight_green():
    print("LIGHT GREEN")
    GPIO.output(Relay_Ch1,GPIO.HIGH)
    GPIO.output(Relay_Ch2,GPIO.HIGH)
    GPIO.output(Relay_Ch3,GPIO.LOW)

def lights_off():
    print("LIGHTS OFF")
    GPIO.output(Relay_Ch1,GPIO.HIGH)
    GPIO.output(Relay_Ch2,GPIO.HIGH)
    GPIO.output(Relay_Ch3,GPIO.HIGH)


def rattling_light(track,what):
    #print("LIGHT RED")
    flight_red()
    light_red = True
    base = 0
    MOVING = False
    last_pos = 0
    cd = 10
    while track['title'] == "Rattlin' Bog":
        base += 0.001
        track = (what.get_current_track_info())
        index = 0
        pos = time_sec(track['position'])
        
        if pos != last_pos:
            moving = True

            
        last_pos = pos
        new_base = time.time()-pos
        
        if abs(new_base - base) > 2:
            base = new_base
            moving = False
            cd = 20

        if cd != 0:
            cd -= 1
        else:
            if base > new_base:
                base = new_base
            
        #print(base, moving, pos, time.time()-base)
        if moving == False:
            time.sleep(0.17)
            continue
        
        
        for item in rattling:
            if item <= time.time()-base:
                index += 1

        if index%2 == 0:
            if light_red == False:
                light_red = True
                flight_red()
        else:
            if light_red == True:
                light_red = False
                flight_green()

        #if index == len(rattling):
         #    print("PARTY")
        #time.sleep(0.17777777)
    lights_off()
                

try:
    lights_off()
    for item in discover():   
        print(item.player_name)
        if item.player_name == "Living Room":
            while True:
                time.sleep(1)
                print(item)
                track = (item.get_current_track_info())
                #for item in track:
                #    print(item)
                #print(track['metadata'])
                #aa
                print(track['title'])
                if track['title'] == "Rattlin' Bog":
                    print("RATTLING")
                    rattling_light(track,item)


except Exception as e:
        print("except")
        print(e)
        GPIO.cleanup()


