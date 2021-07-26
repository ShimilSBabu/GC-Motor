import cv2,threading
import RPi.GPIO as GPIO
import numpy as np
from time import sleep

global toggle
global x
global chk
global t1
global t2
global frame
global count

count = 1
x2 = 0
chk = 1
x=0
toggle = 0

GPIO.setmode(GPIO.BOARD)
GPIO.setup(16,GPIO.OUT)
GPIO.setup(18,GPIO.OUT)
GPIO.setup(22,GPIO.OUT)

cap = cv2.VideoCapture(0)

open_cascade = cv2.CascadeClassifier('test1.xml')
hand_cascade = cv2.CascadeClassifier('test2.xml')


font = cv2.FONT_HERSHEY_SIMPLEX

def mtr_clkwise():
    global chk
    chk = 0
    GPIO.output(16,GPIO.HIGH)
    GPIO.output(18,GPIO.LOW)
    GPIO.output(22,GPIO.HIGH)
    sleep(12)
    GPIO.output(22,GPIO.LOW)
    chk = 1

def mtr_anticlkwise():
    global chk
    chk = 0
    GPIO.output(16,GPIO.LOW)
    GPIO.output(18,GPIO.HIGH)
    GPIO.output(22,GPIO.HIGH)
    sleep(12)
    GPIO.output(22,GPIO.LOW)
    chk = 1
    
while(True):
    ret,frame = cap.read()
    if frame.all() == None:
        continue
    gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    face = open_cascade.detectMultiScale(gray, 1.5, 2)
    
    if len(np.array(face)) == 0:
        continue
    
    if chk == 1:
        hands = hand_cascade.detectMultiScale(gray, 1.5, 2)
        contour = np.array(hands)
        
        if len(contour>0):
            for (x, y, w, h) in hands:
                dif = abs(x-x2)
                x2 = x
                if dif < 20:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (70, 55, 0), 2)
                    t1 = threading.Thread(target = mtr_clkwise)
                    t2 = threading.Thread(target = mtr_anticlkwise)   
                    if toggle == 0:
                        t1.start()
                        del t1
                        toggle = (toggle+1)%2
                    else:
                        t2.start()
                        del t2         
                        toggle = (toggle+1)%2
    
    if chk ==0 and toggle == 0:
        cv2.putText(frame,'clockwise',(0,50), font, 2, (0,0,255), 3, cv2.LINE_AA)
    if chk ==0 and toggle == 1:
        cv2.putText(frame,'anti-clockwise',(0,50), font, 2, (0,0,255), 3, cv2.LINE_AA)
    
    cv2.imshow('Driver_frame', frame)
    count += 1
    
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        GPIO.output(22,GPIO.LOW)
        GPIO.cleanup()
        break

cap.release()
cv2.destroyAllWindows()