from flask import Flask, render_template, url_for, request
from flask.json import jsonify
import time
from multiprocessing import Process, Value
import random

Relay_Ch1 = 26
Relay_Ch2 = 20
Relay_Ch3 = 21

cache = {}

debug = False

if debug != True:
    import RPi.GPIO as GPIO
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(Relay_Ch1,GPIO.OUT)
    GPIO.setup(Relay_Ch2,GPIO.OUT)
    GPIO.setup(Relay_Ch3,GPIO.OUT)

app = Flask(__name__)

cache['grønn'] = "False"
cache['rød1'] = "False"
cache['rød2'] = "False"
cache['loop'] = "False"

def r1():
    if cache["rød1"] == "True":
        r1_off()
    else:
        r1_on()
    print(cache['rød1'])

def r2():
    if cache["rød2"] == "True":
        r2_off()
    else:
        r2_on()
    print(cache['rød2'])
        
def g():
    if cache["grønn"] == "True":
        g_off()
    else:
        g_on()
    print(cache['grønn'])

def r1_on():
     cache['rød1'] = "True"
     if debug != True:
        GPIO.output(Relay_Ch1,GPIO.LOW)
    
def r1_off():
     cache['rød1'] = "False"
     if debug != True:
        GPIO.output(Relay_Ch1,GPIO.HIGH)

def r2_on():
     cache['rød2'] = "True"
     if debug != True:
        GPIO.output(Relay_Ch2,GPIO.LOW)

def r2_off():
    cache['rød2'] = "False"
    if debug != True:
            GPIO.output(Relay_Ch2,GPIO.HIGH)

def g_on():
     cache['grønn'] = "True"
     if debug != True:
        GPIO.output(Relay_Ch3,GPIO.LOW)

def g_off():
     cache['grønn'] = "False"
     if debug != True:
        GPIO.output(Relay_Ch3,GPIO.HIGH)
        
def r_on():
    print("røde på")
    r1_on()
    r2_on()

def r_off():
    print("røde av")
    r1_off()
    r2_off()
    
def all_off():
    print("alle av")
    r_off()
    g_off()

def all_on():
    print("alle på")
    g_on()
    r_on()

all_off()
valid_lys = [1,2,3,4,5]
lys_state = 0

def solbrille(loop_on):
   loop = True
   x = 0
   sov = random.randint(20,900)
   print(sov)
   while loop:
      if loop_on.value == True:
        if x >= sov:
            r_on()
            g_off()
            time.sleep(5)
            r_off()
            solbrille(Value('b',True))
        else:
            x += 1
            time.sleep(1)
            print(f"{x}/{sov} sek")


threads =[]
@app.route("/")
@app.route("/home")
def home():
    return render_template("index.html", name = cache)

#@app.route("/<int:lys>/<int:lys_state>")
@app.route("/res",methods=["POST","GET"])
def trigger_lys():
    output = request.form.to_dict()
    try:
        lys = int(output['lys'])
    except:
        lys = ""
    if lys == 1:
        r1()
    elif lys == 2:
        r2()
    elif lys == 3:
        g()
    elif lys == 4:
        r_off()
        g_on()
    elif lys == 5:
        r_on()
        g_off()
    elif lys == 6:
        all_off()
    elif lys == 7:
        all_on()
    elif output['mode']=="loop":
        if cache['loop'] =="True":
            cache['loop'] = 'False'
            threads[-1].kill()
            threads[-1].join()
            print(threads[-1].is_alive())
        else:
            recording_on = Value('b', True)
            threads.append(Process(target=solbrille, args=(recording_on,)))
            try:
                threads.pop(-2)
            except:
                pass
            cache['loop'] = 'True'
            threads[-1].start()
        print("cache loop:",cache['loop'])
    else:
        print("invalid")

    return render_template("index.html", name = cache)

if __name__ == "__main__":
    app.run(host ="0.0.0.0", port=8500)
    
all_off()