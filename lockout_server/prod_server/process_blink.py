import RPi.GPIO as GPIO
import time

pin = 19

def blink ( ):
    GPIO.setmode ( GPIO.BOARD )
    GPIO.setp ( pin, GPIO.OUT )
    
    while ( 1 ):
        GPIO.output ( pin, GPIO.HIGH )
        time.sleep ( 1 )
        GPIO.output ( pin, GPIO.LOW )
        time.sleep ( 1 )

    #this should never be reached
    GPIO.cleanup ()
