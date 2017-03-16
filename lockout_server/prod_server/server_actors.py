import process_LCD
import process_keypad
import process_cardread

from threading import Timer
import pykka


import time
import serial

MAX_MACHINE_NUMBER_FIGURES = 2

CR_LF = '\r\n'

#LCDActor Messages
LCDActor_machine = 'machine'
LCDActor_id = 'id'
LCDActor_home_screen = 'homescreen'

#KeypadActor Messages
KeypadActor_start = 'start'
KeypadActor_stop = 'stop'

#CardreadActor Messages
CardreadActor_start = 'start'

#UIActor Messages
UIActor_receive_char = 'receive_char'
UIActor_receive_id  = 'receive_id'

class LCDActor ( pykka.ThreadingActor ):
    def __init__(self):
        super(LCDActor, self).__init__(use_daemon_thread=True)
        self.buf = []
   
    def on_failure(self, exception_type, exception_value, traceback ):
        print ( 'LCDActor error: {}; {}'.format(exception_type, exception_value) )
        print_tb(traceback)

    def on_receive ( self, msg ):

        if ( msg['type'] == LCDActor_machine ):
            process_LCD.process_lcd ( "MACHINE #:" + CR_LF + msg['data'] + CR_LF )
        elif ( msg['type'] == LCDActor_id ):
            process_LCD.process_lcd ( "ID:" + CR_LF + msg['data'] + CR_LF )
        elif ( msg['type'] == LCDActor_home_screen ):
            process_LCD.process_lcd ( 'Slide ID' + CR_LF + 'To Begin' + CR_LF )

class KeypadActor ( pykka.ThreadingActor ):
    def __init__(self, ui_urn ):
        super(KeypadActor, self).__init__(use_daemon_thread=True)
        self.ui_urn = ui_urn 
      
    def on_receive ( self, msg ):
        if ( msg['type'] == KeypadActor_start ):
            process_keypad.set_up_interrupts ( )
        elif ( msg['type'] == KeypadActor_stop ):
            process_keypad.kill_interrupts ( )         

    def on_failure(self, exception_type, exception_value, traceback ):
        print ( 'KeypadActor error: {}; {}'.format(exception_type, exception_value) )
        print_tb(traceback)

class CardreadActor ( pykka.ThreadingActor ):
    def __init__(self, ui_urn ):
        super(CardreadActor, self).__init__(use_daemon_thread=True)
        self.ui_urn = ui_urn
        self.reader = process_cardread.BarCodeReader(0xc216, 0x0180, 208, 8, should_reset=False, 
                            timeout_msec=100, debug=False)
        self.reader.initialize ( )

    def on_receive ( self, msg ):
        if ( msg['type'] == CardreadActor_start ):
            process_cardread.process_cardread ( self.reader,  self.ui_urn )        
    
    def on_failure(self, exception_type, exception_value, traceback ):
        print ( 'KeypadActor error: {}; {}'.format(exception_type, exception_value) )
        print_tb(traceback)

class UIActor ( pykka.ThreadingActor ):
    STATE_ID = 1
    STATE_CONFIRM = 2
    STATE_MACHINE_NUMBER = 3
    STATE_LOCK_UI = 4

    def __init__(self, lcd_urn):
        super(UIActor, self).__init__(use_daemon_thread=True)
        self.buf = []
        self.ui_state = self.STATE_ID
        self.lcd_urn = lcd_urn
        self.id_buf = ""
 
    def on_failure(self, exception_type, exception_value, traceback ):
        print ( 'UIActor error: {}; {}'.format(exception_type, exception_value) )
        print_tb(traceback)

    def on_receive ( self, msg ):
        if ( msg['type'] == UIActor_receive_id ):
            self.handle_id ( msg['data'] )

        elif ( msg['type'] == UIActor_receive_char ):
            if ( self.ui_state == self.STATE_CONFIRM ):
                self.handle_confirm ( msg['data'] )
            elif ( self.ui_state == self.STATE_MACHINE_NUMBER ):
                self.handle_char ( msg['data'] )

    def handle_confirm (self, char ):
        if ( char == '#' ):
            self.ui_state = self.STATE_MACHINE_NUMBER
            self.buf = []
            pykka.ActorRegistry.get_by_urn ( self.lcd_urn ).tell ( {'type': LCDActor_machine, 
                                                                    'data' : ''.join ( self.buf ) } )
        elif ( char == '*' ):
            self.ui_state = self.STATE_ID
            self.id_buf = ""
            pykka.ActorRegistry.get_by_urn ( self.lcd_urn ).tell ( {'type': LCDActor_home_screen } )

    def handle_char ( self, char ):
        if ( char == '#' ):
            self.ui_state = self.STATE_ID
            self.buf = []
            pykka.ActorRegistry.get_by_urn ( self.lcd_urn ).tell ( {'type': LCDActor_home_screen } )
 
        elif ( char == '*' ):
            if ( len ( self.buf ) > 0 ):
                self.buf.pop(-1)
                pykka.ActorRegistry.get_by_urn ( self.lcd_urn ).tell ( {'type': LCDActor_machine,
                                                                   'data' : ''.join ( self.buf ) } )    
        else:
            if ( len ( self.buf ) < MAX_MACHINE_NUMBER_FIGURES ):
                self.buf.append ( char ) 
                pykka.ActorRegistry.get_by_urn ( self.lcd_urn ).tell ( {'type': LCDActor_machine,
                                                                   'data' : ''.join ( self.buf ) } )
    def handle_id ( self, cardid ):
        pykka.ActorRegistry.get_by_urn ( self.lcd_urn ).tell ( {'type' : LCDActor_id,
                                                                'data' : cardid} )
        self.id_buf = cardid
        self.ui_state = self.STATE_CONFIRM


if __name__ == '__main__':
    print  'starting actors'
    
    lcd = LCDActor.start ( )
    ui = UIActor.start ( lcd.actor_urn )
    
    keypad = KeypadActor.start ( ui.actor_urn )
    cardId = CardreadActor.start ( ui.actor_urn )   
    keypad.tell({'type': KeypadActor_start})
    cardId.tell({'type': CardreadActor_start})
    lcd.tell({'type' : LCDActor_home_screen })

    while ( 1 ): 
        pass
