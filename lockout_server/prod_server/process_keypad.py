# #####################################################
# Python Library for 3x4 matrix keypad using
# 7 of the avialable GPIO pins on the Raspberry Pi.
#
# This could easily be expanded to handle a 4x4 but I
# don't have one for testing. The KEYPAD constant
# would need to be updated. Also the setting/checking
# of the colVal part would need to be expanded to
# handle the extra column.
#
# Written by Chris Crumpacker
# May 2013
#
# main structure is adapted from Bandono's
# matrixQPI which is wiringPi based.
# https://github.com/bandono/matrixQPi?source=cc
# #####################################################
import pykka
import RPi.GPIO as GPIO
import time
import server_actors


ROW         = [21,20,16,12] 
COLUMN      = [25,24,23]
   

class keypad():
    # CONSTANTS   
    KEYPAD = [
    ["1","2","3"],
    ["4","5","6"],
    ["7","8","9"],
    ["*","0","#"]
    ]
   
    ROW         = [21,20,16,12] 
    COLUMN      = [25,24,23]
   
    def __init__(self):
        GPIO.setmode(GPIO.BCM)

    def getKey(self): 
        # Set all columns as output low
        for j in range(len(self.COLUMN)):
            GPIO.setup(self.COLUMN[j], GPIO.OUT)
            GPIO.output(self.COLUMN[j], GPIO.HIGH)
       
        # Set all rows as input
        for i in range(len(self.ROW)):
            GPIO.setup(self.ROW[i], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
       
        # Scan rows for pushed key/button
        # A valid key press should set "rowVal"  between 0 and 3.
        rowVal = -1
        for i in range(len(self.ROW)):
            tmpRead = GPIO.input(self.ROW[i])
            if tmpRead == 1:
                rowVal = i
               
        # if rowVal is not 0 thru 3 then no button was pressed and we can exit
        if rowVal <0 or rowVal >3:
            self.exit()
            return
       
        # Convert columns to input
        for j in range(len(self.COLUMN)):
                GPIO.setup(self.COLUMN[j], GPIO.IN, pull_up_down=GPIO.PUD_UP)
       
        # Switch the i-th row found from scan to output
        GPIO.setup(self.ROW[rowVal], GPIO.OUT)
        GPIO.output(self.ROW[rowVal], GPIO.LOW)

        # Scan columns for still-pushed key/button
        # A valid key press should set "colVal"  between 0 and 2.
        colVal = -1
        for j in range(len(self.COLUMN)):
            tmpRead = GPIO.input(self.COLUMN[j])
            if tmpRead == 0:
                colVal=j
               
        # if colVal is not 0 thru 2 then no button was pressed and we can exit
        if colVal <0 or colVal >2:
            self.exit()
            return

        # Return the value of the key pressed
        self.exit()
        return self.KEYPAD[rowVal][colVal]
       
    def exit(self):
        
        # Reinitialize all rows and columns as input at exit
        for i in range(len(self.ROW)):
                GPIO.setup(self.ROW[i], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        for j in range(len(self.COLUMN)):
                GPIO.setup(self.COLUMN[j], GPIO.IN, pull_up_down=GPIO.PUD_UP)

def set_up_interrupts ( ):
    GPIO.setmode(GPIO.BCM)
    for pin in ROW:
        GPIO.setup ( pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN )
        GPIO.add_event_detect ( pin, GPIO.RISING, process_keypad, bouncetime=400)

def kill_interrupts ( ):
    for pin in ROW:
        GPIO.remove_event_detect ( pin ) 
    GPIO.cleanup ( ROW )
    GPIO.cleanup ( COLUMN )

   
def process_keypad ( baka ):
    kp = keypad ()
     # Initialize the keypad class
    ui_actor = pykka.ActorRegistry.get_by_class_name ( "UIActor" )
    # Loop while waiting for a keypress
    digit = None
    while digit == None:
        time.sleep ( 0.1 )
        digit = kp.getKey()
    for actor in ui_actor:
        actor.tell ( {'type' : server_actors.UIActor_receive_char,
                     'data' : digit } )

