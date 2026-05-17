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
        new_base = time.time()
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
            elif pos != last_pos:
                moving=False
                cd = 5
                self.base = new_base
                
            last_pos = pos
            new_base = time.time()-pos
            
            #if abs(new_base - self.base) > 2:
                #self.base = new_base
                #moving = False
                #cd = 5

            if cd != 0:
                cd -= 1
                self.base = new_base
                #print("pause", cd)

            else:
                if self.base > new_base:
                    self.base = new_base
                
            #print(self.base, moving, pos, time.time()-self.base)
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

rattling = [16.47, 19.26, 32.03, 35.67, 48.02, 52.075, 65.2, 70.25, 82.72, 89.59, 101.60, 109.20, 121.31, 129.32, 141.95,
            150.92, 163.53, 173.41, 186.10, 196.22, 208.39, 220.28, 232.32, 244.91, 257.25, 270.88, 282.78, 296.01]

thunder = [29.51517062187195, 33.00933175086975, 36.59750609397888, 40.23241953849792, 43.86307983398437, 47.50048141479492, 51.05924921035766, 54.657491254806516, 58.28702979087829, 61.845240640640256, 70.85193042755127, 78.06092290878296, 85.20293979644775, 92.46000056266784, 112.02269821166992, 162.72894625663758, 166.36308007240297, 169.63424186706544, 173.4848430633545, 223.5798228263855, 227.20867495536805, 230.65493445396424, 234.35948328971864, 251.9153416633606, 255.33056883811952, 258.9080074310303, 262.43620400428773, 265.9279480457306, 269.6350372314453, 272.8297660827637, 276.3928456783295, 280.1342914581299]

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
    print("LIGHTs OFF")
    GPIO.output(Relay_Ch1,GPIO.HIGH)
    GPIO.output(Relay_Ch2,GPIO.HIGH)
    GPIO.output(Relay_Ch3,GPIO.HIGH)

def blink_opus():
    GPIO.output(Relay_Ch3,GPIO.HIGH)
    #GPIO.output(Relay_Ch2,GPIO.HIGH)
    for i in range(100):
        GPIO.output(Relay_Ch1,GPIO.LOW)
        GPIO.output(Relay_Ch2,GPIO.HIGH)

        time.sleep(0.2)
        GPIO.output(Relay_Ch1,GPIO.HIGH)
        GPIO.output(Relay_Ch2,GPIO.LOW)

        time.sleep(0.2)
    #GPIO.output(Relay_Ch1,GPIO.LOW)
    #GPIO.output(Relay_Ch2,GPIO.LOW)
        
def fthunder():
    print("THUNDER")
    time.sleep(0.2)
    GPIO.output(Relay_Ch1,GPIO.HIGH)
    GPIO.output(Relay_Ch2,GPIO.HIGH)
    GPIO.output(Relay_Ch3,GPIO.LOW)
    time.sleep(0.4)
    GPIO.output(Relay_Ch3,GPIO.HIGH)
    time.sleep(0.15)
    GPIO.output(Relay_Ch3,GPIO.LOW)
    time.sleep(0.4)
    GPIO.output(Relay_Ch3,GPIO.HIGH)
    GPIO.output(Relay_Ch1,GPIO.LOW)
    GPIO.output(Relay_Ch2,GPIO.LOW)

def fthunder_struck():
    print("THUNDERSTRUCK")
    GPIO.output(Relay_Ch1,GPIO.HIGH)
    GPIO.output(Relay_Ch2,GPIO.HIGH)
    GPIO.output(Relay_Ch3,GPIO.LOW)
    time.sleep(1.4)
    GPIO.output(Relay_Ch3,GPIO.HIGH)
    GPIO.output(Relay_Ch1,GPIO.LOW)
    GPIO.output(Relay_Ch2,GPIO.LOW)
    
def rattling_light(track, sonos):
    tk.keep_time()
    print("LIGHT RED")
    light_red = True
    base = 0
    moving = False
    last_pos = 0
    cd = 10
    while track['title'] == "Rattlin' Bog":
        track = (sonos.get_current_track_info())
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

def thunder_light(track, sonos):
    tk.keep_time()
    data = []
    old_index = 0
    while track['title'] == "Thunderstruck":
        track = (sonos.get_current_track_info())
        index = 0
        for item in thunder:
            if item-0.1 <= tk.time():
                index += 1
        #print(index)
                
        if index != old_index:
            old_index = index
            if index < 15:
                fthunder()
            else:
                fthunder_struck()
        
        time.sleep(0.02)

def opus_light(track,sonos):
    tk.keep_time()
    light_modes = [GPIO.HIGH, GPIO.LOW]
    loop = 0
    while track['title'] == "Opus":
        track = (sonos.get_current_track_info())

        loop += 1  
        if tk.time() < 224:
            #timee = max(max(224-tk.time()+4,0.1)**0.05-1, 0.05)
            timee = max((224**0.75-tk.time()**0.75+10)*0.005, 0.05)

            GPIO.output(Relay_Ch3,light_modes[loop%2])
            #GPIO.output(Relay_Ch2,light_modes[loop%2])
            print(timee)
            time.sleep(timee)
        elif tk.time() < 226:
            blink_opus()
        elif tk.time() < 292.5:
            timee = max((292.5**0.75-tk.time()**0.75+10)*0.005, 0.05)
            GPIO.output(Relay_Ch3,light_modes[loop%2])
            #GPIO.output(Relay_Ch2,light_modes[loop%2])
            time.sleep(timee)
            print(timee)
        elif tk.time() < 294:
            blink_opus()
        elif tk.time() < 342:
            timee = max((342**0.75-tk.time()**0.75+10)*0.005, 0.05)
            GPIO.output(Relay_Ch3,light_modes[loop%2])
            #GPIO.output(Relay_Ch2,light_modes[loop%2])
            time.sleep(timee)
            print(timee)
        elif tk.time() < 343:
            blink_opus()

        else:
            timee = max((tk.time()-343)*0.005, 0.05)
            GPIO.output(Relay_Ch3,light_modes[loop%2])
            #GPIO.output(Relay_Ch2,light_modes[loop%2])
            time.sleep(timee)
        print(tk.time())
            
        
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
            flight_red()
            print("RATTLING")
            rattling_light(track, sonos)
        elif track['title'] == "Thunderstruck":
            flight_red()
            thunder_light(track, sonos)
        elif track['title'] == "Opus":
            flight_green()
            opus_light(track, sonos)
        else:
            lights_off()
except KeyboardInterrupt:
        print("excepttion")
        tk.kill()
        GPIO.cleanup()


