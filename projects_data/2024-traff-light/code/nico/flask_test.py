from flask import Flask, render_template, url_for, request
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


app = Flask(__name__)

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
    
def all_off():
    r_off()
    g_off()

def all_on():
    g_on()
    r_on()

all_off()
g_on()
valid_lys = [1,2,3,4,5]


@app.route("/")
@app.route("/home")
def home():
    return render_template("index.html")

#@app.route("/<int:lys>/<int:lys_state>")
@app.route("/res",methods=["POST","GET"])
def trigger_lys():
    output = request.form.to_dict()
    lyset = output["name"]
    lyset_state = output["state"]
    lys = int(lyset)
    lys_state = int(lyset_state)
    if lys not in valid_lys:
        return render_template("index.html", name = "error not in ")
    if lys == 1:
        if lys_state == 0:
            g_off()
        else:
            g_on()
    elif lys == 2:
        if lys_state == 0:
            r1_off()
        else:
            r1_on()
    elif lys == 3:
        if lys_state == 0:
            r2_off()
        else:
            r2_on()
    elif lys == 4:
        if lys_state == 0:
            r_on()
        else:
            r_off()
    elif lys == 5:
        if lys_state == 0:
            all_off()
        else:
            all_on()
    else:
        return render_template("index.html", name = "du er balle")
    return render_template("index.html", name = "done")

if __name__ == "__main__":
    app.run(host ="0.0.0.0", port=8500)

all_off()