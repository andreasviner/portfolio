from soco import SoCo, discover
import time
import threading
import RPi.GPIO as GPIO

Relay_Ch1 = 26
Relay_Ch2 = 20
Relay_Ch3 = 21

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(Relay_Ch1,GPIO.OUT)
GPIO.setup(Relay_Ch2,GPIO.OUT)
GPIO.setup(Relay_Ch3,GPIO.OUT)

class time_keeper_class():
    def __init__(self, sonos):
        self.sonos = sonos
        self.base = time.time()
        self.threads = []
        self.running = True
        
    def time_thread(self, title):
        self.base = time.time()
        moving = False
        last_pos = 0
        cd = 10
        track = (self.sonos.get_current_track_info())
        while track['title'] == title:
            if not self.running:
                return
            track = (self.sonos.get_current_track_info())
            pos = time_sec(track['position'])
            
            if pos == last_pos+1:
                if moving == False:
                    self.base = time.time()-pos
                moving = True
                
            last_pos = pos
            new_base = time.time()-pos
            
            if abs(new_base - self.base) > 2:
                self.base = new_base
                moving = False
                cd = 5

            if cd != 0:
                cd -= 1
                self.base = new_base
                #print("pause", cd)

            else:
                if self.base > new_base:
                    self.base = new_base
                
            print(self.base, moving, pos, time.time()-self.base)
            if moving == False:
                cd = 5
                time.sleep(0.1)
                continue

        
        

               
    def keep_time(self):
        track = (self.sonos.get_current_track_info())
        
        t1 = threading.Thread(target=self.time_thread, args=(track['title'],))
        t1.start()
        self.threads.append(t1)
        
    def time(self):
        return time.time()-self.base

    def kill(self):
        self.running = False
        for item in self.threads:
            item.join()
 

def time_sec(st):
    arr = st.split(":")
    return int(arr[0])*60*60 + int(arr[1])*60 + int(arr[2])

rattling = [16.47, 19.26, 32.03, 35.67, 48.02, 52.065, 65.2, 70.25, 82.72, 89.29, 101.50, 109.20, 121.31, 129.32, 141.95,
            150.92, 163.53, 173.41, 186.10, 196.22, 208.39, 220.28, 232.32, 244.91, 257.25, 270.88, 282.78, 296.01]


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


def rattling_light(track,what):
    tk.keep_time()
    print("LIGHT RED")
    light_red = True
    base = 0
    moving = False
    last_pos = 0
    cd = 10
    while track['title'] == "Rattlin' Bog":
        
        index = 0
        for item in rattling:
            if item <= tk.time():
                index += 1
        #print(index)
        if index%2 == 0:
            if light_red == False:
                light_red = True
                flight_red()
                print(rattling[index-1])
        else:
            if light_red == True:
                light_red = False
                flight_green()
                print(rattling[index-1])
        time.sleep(0.02)
        #if index == len(rattling):
         #    print("PARTY")
        #time.sleep(0.17777777)
                
sonos = None        
for item in discover():
    if item.player_name == "Living Room":
        sonos = item

tk = time_keeper_class(sonos)
        
try:
    while True:
        time.sleep(1)
        print(sonos)
        track = (sonos.get_current_track_info())

        print(track['title'])
        if track['title'] == "Rattlin' Bog":
            print("RATTLING")
            rattling_light(track,item)

except KeyboardInterrupt:
        print("excepttion")
        tk.kill()
        GPIO.cleanup()


