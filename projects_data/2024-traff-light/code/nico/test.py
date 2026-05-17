import RPi.GPIO as GPIO
import time
import random

Relay_Ch1 = 26
Relay_Ch2 = 20
Relay_Ch3 = 21

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(Relay_Ch1,GPIO.OUT)
GPIO.setup(Relay_Ch2,GPIO.OUT)
GPIO.setup(Relay_Ch3,GPIO.OUT)

print("Setup The Relay Module is [success]")
def g_on():
        GPIO.output(Relay_Ch3,GPIO.LOW)
        
def g_off():
        GPIO.output(Relay_Ch3,GPIO.HIGH)

def r1_on():
        GPIO.output(Relay_Ch1,GPIO.LOW)
        
def r1_off():
        GPIO.output(Relay_Ch1,GPIO.HIGH)

def r2_on():
        GPIO.output(Relay_Ch2,GPIO.LOW)
        
def r2_off():
        GPIO.output(Relay_Ch2,GPIO.HIGH)

def r_on():
        r1_on()
        r2_on()

def r_off():
        r1_off()
        r2_off()

        
try:
        while True:
                #Control the Channel 1
                r_off()
                g_on()
                time.sleep(30)
                for i in range(10):
                    time.sleep(0.3)
                    g_off()
                    time.sleep(0.3)
                    g_on()
                    print("blink",i)
                g_off()
                r_on()
                time.sleep(random.randint(1,600))
                
                
except:
        print("except")
        GPIO.cleanup()
