import soco
from soco import events_twisted
soco.config.EVENTS_MODULE = events_twisted
from twisted.internet import reactor
import time
import threading
import pickle
import RPi.GPIO as GPIO

Relay_Ch1 = 26
Relay_Ch2 = 20
Relay_Ch3 = 21

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(Relay_Ch1,GPIO.OUT)
GPIO.setup(Relay_Ch2,GPIO.OUT)
GPIO.setup(Relay_Ch3,GPIO.OUT)


#rattling = [16.47, 19.26, 32.03, 35.67, 48.02, 52.075, 65.2, 70.25, 82.72, 89.59, 101.60, 109.20, 121.31, 129.32, 141.95,
#            150.92, 163.53, 173.41, 186.10, 196.22, 208.39, 220.28, 232.32, 244.91, 257.25, 270.88, 282.78, 296.01]

thunder = [29.51517062187195, 33.00933175086975, 36.59750609397888, 40.23241953849792, 43.86307983398437, 47.50048141479492, 51.05924921035766, 54.657491254806516, 58.28702979087829, 61.845240640640256, 70.85193042755127, 78.06092290878296, 85.20293979644775, 92.46000056266784, 112.02269821166992, 162.72894625663758, 166.36308007240297, 169.63424186706544, 173.4848430633545, 223.5798228263855, 227.20867495536805, 230.65493445396424, 234.35948328971864, 251.9153416633606, 255.33056883811952, 258.9080074310303, 262.43620400428773, 265.9279480457306, 269.6350372314453, 272.8297660827637, 276.3928456783295, 280.1342914581299]


def time_sec(st):
    arr = st.split(":")
    if len(arr) == 1:
        return 0
    return int(arr[0])*60*60 + int(arr[1])*60 + int(arr[2])



def make_timing(tk):
    print("MAKE TIMING")
    og_title = tk.song
    data = []
    while tk.song == og_title:
        if input("") == "stop":
            break
        print(tk.time())
        data.append(tk.time())
        with open(og_title + ".data", "wb") as file:
            pickle.dump(data,file)

         

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
    GPIO.output(Relay_Ch2,GPIO.HIGH)
    for i in range(50):
        GPIO.output(Relay_Ch1,GPIO.LOW)
        GPIO.output(Relay_Ch2,GPIO.LOW)

        time.sleep(0.2)
        GPIO.output(Relay_Ch1,GPIO.HIGH)
        GPIO.output(Relay_Ch2,GPIO.HIGH)

        time.sleep(0.2)
        
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
    
def rattling_light(tk):
    print("LIGHT RED")
    light_red = True
    base = 0
    moving = False
    last_pos = 0
    cd = 10
    with open("RattlinBog.data", "rb") as file:
        rattling = pickle.load(file)
        
    while tk.song == "Rattlin' Bog":
        #track = (tk.sonos.get_current_track_info())
        index = 0
        for item in rattling:
            if item <= tk.time() +0.05 +0.05*(index%2):
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

def thunder_light(tk):

    data = []
    old_index = 0
    while tk.song == "Thunderstruck":
        #track = (tk.sonos.get_current_track_info())
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



def pisk_light():
    GPIO.output(Relay_Ch1,GPIO.HIGH)
    GPIO.output(Relay_Ch2,GPIO.HIGH)
    print("pisk_start")
    time.sleep(0.35)
    print("PISK")
    GPIO.output(Relay_Ch3,GPIO.LOW)
    time.sleep(0.5)
    GPIO.output(Relay_Ch3,GPIO.HIGH)
    #time.sleep(0.05)
    GPIO.output(Relay_Ch1,GPIO.LOW)
    GPIO.output(Relay_Ch2,GPIO.LOW)    

def pisk_flight():
    GPIO.output(Relay_Ch1,GPIO.HIGH)
    GPIO.output(Relay_Ch2,GPIO.HIGH)
    print("pisk_start")
    time.sleep(0.35)
    print("FAKE PISK")

    time.sleep(0.5)
    GPIO.output(Relay_Ch1,GPIO.LOW)
    GPIO.output(Relay_Ch2,GPIO.LOW)    



def pisk_mig_light(tk):

    with open("PiskMig.data", "rb") as file:
        data = pickle.load(file)

    with open("PiskMig2.data", "rb") as file:
        data2 = pickle.load(file)
    old_index = 0
    fold_index = 0
    while tk.song == "Pisk Mig Hårdt!!!":
        #track = (tk.sonos.get_current_track_info())
        index = 0
        findex = 0
        for item in data:
            if item-0.9 <= tk.time():
                index += 1

        for item in data2:
            if item-0.9 <= tk.time():
                findex += 1
        #print(index)
                
        if index != old_index:
            old_index = index
            pisk_light()

        if findex != fold_index:
            fold_index = findex
            pisk_flight()        
        time.sleep(0.02)    
        
def opus_light(tk):
    GPIO_high = GPIO.HIGH
    GPIO_low = GPIO.LOW
    light_modes = [GPIO_high, GPIO_low]
    loop = 0
    while tk.song == "Opus":
        #track = (tk.sonos.get_current_track_info())

        loop += 1
        if tk.time() < 0:
            continue
        if tk.time() < 223.5:
            #timee = max(max(224-tk.time()+4,0.1)**0.05-1, 0.05)
            timee = max((224**0.75-tk.time()**0.75+15)*0.008, 0.05)

            GPIO.output(Relay_Ch3,light_modes[loop%2])
            print(timee)
            time.sleep(timee)
        elif tk.time() < 226:
            blink_opus()
        elif tk.time() < 292.5:
            timee = max((292.5**0.75-tk.time()**0.75+10)*0.01, 0.05)
            GPIO.output(Relay_Ch3,light_modes[loop%2])
            time.sleep(timee)
            print(timee)
        elif tk.time() < 294:
            blink_opus()
        elif tk.time() < 342:
            timee = max((342**0.75-tk.time()**0.75+10)*0.01, 0.05)
            GPIO.output(Relay_Ch3,light_modes[loop%2])
            time.sleep(timee)
            print(timee)
        elif tk.time() < 343:
            blink_opus()
        else:
            timee = max((tk.time()-343)*0.005, 0.05)
            GPIO.output(Relay_Ch3,light_modes[loop%2])
            time.sleep(timee)
        print(tk.time())

            
class time_keeper():
    def __init__(self, sonos):
        self.song = ""
        self.paused_pos = 0
        self.base = time.time()
        self.on_track = True
        self.sonos = sonos
        self.paused = True
        self.running = True
        self.ping = 0
        self.t = threading.Thread(target=self.check_time)
        print("STARTING THREAD")
        self.t.start()

        
    def kill(self):
        self.running = False
        self.song = ""
        self.t.join()
        
        
    def check_time(self):
        last_pos = 0
        while True:
            if not self.running:
                return
            
            if self.paused:
                time.sleep(0.2)
                continue

            start = time.time()
            track = (self.sonos.get_current_track_info())
            pos = time_sec(track['position'])
            self.ping = time.time()-start

            if pos < int(time.time()-self.base):
                self.base += 0.002
            
            new_base = time.time()-pos
            if new_base < self.base:
                self.base = new_base
            #print(pos, time.time()-self.base, self.ping, self.base)
            
            if pos == last_pos+1:
                time.sleep(max(1-(time.time()-self.base)%1-self.ping,0))

                #if self.paused_pos not in [pos, last_pos]:
                 #   self.acc *= 0.5
            else:
                self.paused_pos = pos

                
            last_pos = pos

            
    def time(self):
        if self.paused:
            return self.paused_pos # self.paused_time-self.base
        return time.time()-self.base
            
        
    def event_update(self, event):
        if 'transport_state' not in event.variables:
            return
        
        track = (self.sonos.get_current_track_info())
        pos = time_sec(track['position'])
        
        print(event.variables)
        #if event.variables['current_track_meta_data'] != self.song:
        if track['title'] != self.song:
            self.paused = True
            print("NEW SONG")
            self.song = track['title']

        if event.variables['transport_state'] == 'PAUSED_PLAYBACK':
            self.paused = True
            self.paused_time = event.timestamp-self.base
            self.paused_pos = pos

        if event.variables['transport_state'] == 'TRANSITIONING':
            if not self.paused:
                self.base = time.time()+30


        if event.variables['transport_state'] == 'PLAYING':
            if pos == 0:
                #self.base = event.timestamp+10
                print("on_track")
                self.on_track = True
                    
##            else:
##                if self.paused:
##                    if self.paused_pos == pos:
##                        self.base = event.timestamp-self.paused_time+10
##                    else:
##                        self.base = time.time()
##                else:
##                    self.on_track = False
            self.paused = False
            self.base = time.time()+30

        
        
def light_controller(tk):
    print("LIGHT CONTOLLER STARTED")
    while tk.running:
        time.sleep(0.1)
        print(tk.time(), tk.song)
        if tk.song == "Rattlin' Bog":
            #make_timing(tk)
            flight_red()
            print("RATTLING")
            rattling_light(tk)
        elif tk.song == "Thunderstruck":
            flight_red()
            thunder_light(tk)
        elif tk.song == "Opus":
            #time.time()
            flight_green()
            opus_light(tk)
        elif tk.song == "Pisk Mig Hårdt!!!":
            flight_red()
            #make_timing(tk)
            pisk_mig_light(tk)


        
def main():
    for item in soco.discover():
        if item.player_name == "Living Room":
            device = item
    tk = time_keeper(device)
    #sub = device.renderingControl.subscribe().subscription
    sub2 = device.avTransport.subscribe().subscription
    #sub.callback = tk.event_update
    sub2.callback = tk.event_update
    t1 = threading.Thread(target=light_controller, args=(tk,))
    t1.start()
    def before_shutdown():
        #sub.unsubscribe()
        sub2.unsubscribe()
        events_twisted.event_listener.stop()
        tk.kill()
        t1.join()
        
    reactor.addSystemEventTrigger(
                'before', 'shutdown', before_shutdown)

    #while True:
     #   print(tk.time())
      #  time.sleep(0.1)
        
if __name__=='__main__':
    reactor.callWhenRunning(main)
    reactor.run()
    print("ENDED")
