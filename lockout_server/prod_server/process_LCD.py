import time
import serial

def process_lcd ( string ):   
    # configure the serial connections (the parameters differs on the device you are connecting to)
    ser = serial.Serial(
        port='/dev/ttyACM0',
        baudrate=9600,
        parity=serial.PARITY_ODD,
        stopbits=serial.STOPBITS_TWO,
        bytesize=serial.SEVENBITS
    )

    ser.isOpen()

    ser.write(string)
    out = ''

    time.sleep(1)
    while ser.inWaiting() > 0:
        out += ser.read(1)
