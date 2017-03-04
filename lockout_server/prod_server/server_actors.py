import process_LCD
import process_keypad


from threading import Timer
import pykka


import time
import serial

       # (note that I happend a \r\n carriage return and line feed to the characters - this is requested by my device)
#        ser.write(input + '\r\n')
CR_LF = '\r\n'

class LCDActor ( pykka.ThreadingActor ):
    def __init__(self):
        super(LCDActor, self).__init__(use_daemon_thread=True)
        self.buf = []
   
    def on_failure(self, exception_type, exception_value, traceback ):
        print ( 'LCDActor error: {}; {}'.format(exception_type, exception_value) )
        print_tb(traceback)

    def on_receive ( self, msg ):
        if ( msg['type'] == 'char'):
            self.handle_char ( msg['data'] )
   
    def handle_char ( self, char ):
        if ( char == '#' or char == '*' ):
            self.buf = []
            process_LCD.process_lcd ( CR_LF + CR_LF )
        else:
            self.buf.append ( char ) 
            #process_LCD.process_lcd ( CR_LF )
            process_LCD.process_lcd ( ''.join(self.buf) + CR_LF + CR_LF )
 
class KeypadActor ( pykka.ThreadingActor ):
    def __init__(self, ui_urn, lcd_urn ):
        super(KeypadActor, self).__init__(use_daemon_thread=True)
        self.ui_urn = ui_urn
        self.lcd_urn = lcd_urn

    def on_receive ( self, msg ):
        if ( msg['type'] == 'start'):
            process_keypad.process_keypad ( self.ui_urn, self.lcd_urn )        
    
    def on_failure(self, exception_type, exception_value, traceback ):
        print ( 'KeypadActor error: {}; {}'.format(exception_type, exception_value) )
        print_tb(traceback)




class UIActor ( pykka.ThreadingActor ):
    def __init__(self):
        super(UIActor, self).__init__(use_daemon_thread=True)
        self.buf = []

    def on_failure(self, exception_type, exception_value, traceback ):
        print ( 'UIActor error: {}; {}'.format(exception_type, exception_value) )
        print_tb(traceback)


    def on_receive ( self, msg ):
        if ( msg['type'] == 'char'):
            self.handle_char ( msg['data'] )
    
    def handle_char ( self, char ):
        if ( char == '#' or char == '*' ):
            print self.buf
            self.buf = []
        else:
            self.buf.append ( char )           


if __name__ == '__main__':
    print  'starting actors'
    ui = UIActor.start ( )
    lcd = LCDActor.start ( )
    keypad = KeypadActor.start ( ui.actor_urn, lcd.actor_urn )
  
    #hajimaru yo!
    keypad.tell({'type': 'start'})
    
    while ( 1 ):
        pass
