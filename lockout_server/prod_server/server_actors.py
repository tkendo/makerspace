import process_LCD
import process_keypad
import process_cardread
import controller

from threading import Timer
import pykka

import time
import serial

MAX_MACHINE_NUMBER_FIGURES = 2
SLEEP_TIME = 3
CR_LF = '\r\n'

#LCDActor Messages
LCDActor_machine = 'machine'
LCDActor_id = 'id'
LCDActor_home_screen = 'homescreen'
LCDActor_lock_screen = 'lockscreen'
LCDActor_swipe_card = 'swipecard'
LCDActor_unlock = 'unlock_auth'
LCDActor_lock = 'lock_auth' 
LCDActor_invalid = 'invalid'
LCDActor_machine_locked = 'locked'

#KeypadActor Messages
KeypadActor_start = 'start'
KeypadActor_stop = 'stop'

#ControlActor messages
ControlActor_auth = 'auth'
ControlActor_MachCheck = 'MachCheck'
ControlActor_lock = 'mach_lock'

MachineUnlock = "Unlocked"
MachineLock = "Locked"
MachineInvalid = "Invalid"

AuthApprove = "Approve"
AuthDeny = "Deny"
AuthError = "Error"
 
#CardreadActor Messages
CardreadActor_start = 'start'

#UIActor Messages
UIActor_receive_char = 'receive_char'
UIActor_receive_id  = 'receive_id'
UIActor_receive_mach_status = "receive_mach_status"
UIActor_auth = 'auth'

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
            process_LCD.process_lcd ( "Enter Machine #" + CR_LF + CR_LF )
        elif ( msg['type'] == LCDActor_swipe_card ):
            process_LCD.process_lcd ( 'Slide ID' + CR_LF + 'To Begin' + CR_LF )
        elif ( msg['type'] == LCDActor_lock_screen ):
            process_LCD.process_lcd ( 'Lock Machine' + CR_LF + str(msg['data']) + "?"+ CR_LF ) 
        elif ( msg['type'] == LCDActor_unlock ):
            process_LCD.process_lcd ( 'MACHINE #' + str(msg['data']) + CR_LF + "UNLOCKED" + CR_LF )
        elif ( msg['type'] == LCDActor_machine_locked ):
            process_LCD.process_lcd ( 'MACHINE #' + str(msg['data']) + CR_LF + "LOCKED" + CR_LF )
        elif ( msg['type'] == LCDActor_lock ):
            process_LCD.process_lcd ( 'NOT' + CR_LF + 'AUTHETICATED' + CR_LF )
        elif ( msg['type'] == LCDActor_invalid ):
            process_LCD.process_lcd ( 'INVALID' +CR_LF+ 'MACHINE' + CR_LF )

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

class ControlActor ( pykka.ThreadingActor ):
    def __init__(self):
        super(ControlActor, self).__init__(use_daemon_thread=True)
      
    def on_receive ( self, msg ):
        if ( msg['type'] == ControlActor_auth ):
            controller.handle_auth_req( msg['data'] )
        elif ( msg['type'] == ControlActor_MachCheck ):
            controller.get_mach_status( msg['data'] )
        elif ( msg['type'] == ControlActor_lock ):
            controller.relock_mach(msg['data'])
        else:
            print 'Invalid message ControlActor'

    def on_failure(self, exception_type, exception_value, traceback ):
        print ( 'ControlActor error: {}; {}'.format(exception_type, exception_value) )
        print_tb(traceback)

class CardreadActor ( pykka.ThreadingActor ):
    def __init__(self, ui_urn ):
        super(CardreadActor, self).__init__(use_daemon_thread=True)
        self.ui_urn = ui_urn
        self.reader = process_cardread.BarCodeReader(0xc216, 0x0180, 208, 8, should_reset=False, 
                            timeout_msec=100, debug=False)
        #self.reader = process_cardread.BarCodeReader(0x5131, 0x2007, 208, 8, should_reset=False, 
        #                    timeout_msec=100, debug=True)
        self.reader.initialize ( )

    def on_receive ( self, msg ):
        if ( msg['type'] == CardreadActor_start ):
            process_cardread.process_cardread ( self.reader,  self.ui_urn )        
    
    def on_failure(self, exception_type, exception_value, traceback ):
        print ( 'KeypadActor error: {}; {}'.format(exception_type, exception_value) )
        print_tb(traceback)

class UIActor ( pykka.ThreadingActor ):
    STATE_MACHINE_NUMBER = 1
    STATE_ID = 2
    STATE_CONFIRM = 3
    STATE_LOCK_UI = 4
    STATE_UNLOCK_UI = 5
    STATE_IDLE = 6
    STATE_SLEEP = 7
    STATE_CONFIRM_LOCK = 8
    def __init__(self, lcd_urn, ctrl_urn):
        super(UIActor, self).__init__(use_daemon_thread=True)
        self.buf = []
        self.ui_state = self.STATE_MACHINE_NUMBER
        self.lcd_urn = lcd_urn
        self.ctrl_urn = ctrl_urn
        self.id_buf = ""
        self.mach_num = 0
 
    def on_failure(self, exception_type, exception_value, traceback ):
        print ( 'UIActor error: {}; {}'.format(exception_type, exception_value) )
        print_tb(traceback)

    def on_receive ( self, msg ):
        if ( msg['type'] == UIActor_receive_id ):
            if ( self.ui_state == self.STATE_ID ):
                self.handle_id ( msg['data'] )

        elif ( msg['type'] == UIActor_receive_char ):
            if ( self.ui_state == self.STATE_CONFIRM ):
                self.handle_confirm ( msg['data'] )
            elif ( self.ui_state == self.STATE_MACHINE_NUMBER ):
                self.handle_char ( msg['data'] )
            elif ( self.ui_state == self.STATE_CONFIRM_LOCK ):
                self.handle_confirm_lock ( msg['data'] )
 
        elif ( msg['type'] == UIActor_receive_mach_status ):
            self.handle_mach_status_response ( msg['data'] )        
        elif ( msg['type'] == UIActor_auth ):
            self.handle_authentication ( msg['data'] )
    
    def handle_authentication ( self, data ):
        if ( data == AuthApprove ):
            self.ui_state = self.STATE_SLEEP
            pykka.ActorRegistry.get_by_urn ( self.lcd_urn ).tell ( {'type': LCDActor_unlock,
                                                                    'data': self.mach_num } )
        elif ( data == AuthDeny ):
            self.ui_state = self.STATE_SLEEP
            pykka.ActorRegistry.get_by_urn ( self.lcd_urn ).tell ( {'type': LCDActor_lock,
                                                                    'data': self.mach_num } )
        elif ( data == AuthError ):
            self.ui_state = self.STATE_SLEEP
            pykka.ActorRegistry.get_by_urn ( self.lcd_urn ).tell ( {'type': LCDActor_lock,
                                                                    'data': self.mach_num } )
 
        time.sleep ( SLEEP_TIME )
        self.ui_state = self.STATE_MACHINE_NUMBER 
        pykka.ActorRegistry.get_by_urn ( self.lcd_urn ).tell ( {'type': LCDActor_home_screen } )

    def handle_mach_status_response ( self, data ): 
        if ( data == MachineLock ):
            self.ui_state = self.STATE_CONFIRM_LOCK
            pykka.ActorRegistry.get_by_urn ( self.lcd_urn ).tell ( {'type': LCDActor_lock_screen,
                                                                    'data': self.mach_num } )
        elif ( data == MachineUnlock ):
            self.ui_state = self.STATE_ID
            pykka.ActorRegistry.get_by_urn ( self.lcd_urn ).tell ( {'type': LCDActor_swipe_card } )

        elif ( data == MachineInvalid ):
            self.ui_state = self.STATE_SLEEP
            pykka.ActorRegistry.get_by_urn ( self.lcd_urn ).tell ( {'type': LCDActor_invalid } )
            time.sleep ( SLEEP_TIME )
            self.ui_state = self.STATE_MACHINE_NUMBER
            pykka.ActorRegistry.get_by_urn ( self.lcd_urn ).tell ( {'type': LCDActor_home_screen } ) 
            

         
    def handle_confirm_lock ( self, char ):
        if ( char == '#' ):
            self.ui_state = self.STATE_SLEEP
            pykka.ActorRegistry.get_by_urn ( self.ctrl_urn ).tell ( { 'type' : ControlActor_lock, 'data' : self.mach_num} )
            pykka.ActorRegistry.get_by_urn ( self.lcd_urn ).tell ( { 'type' : LCDActor_machine_locked, 'data' : self.mach_num} )
            time.sleep ( SLEEP_TIME )
            self.ui_state = self.STATE_MACHINE_NUMBER 
            pykka.ActorRegistry.get_by_urn ( self.lcd_urn ).tell ( { 'type' : LCDActor_home_screen } )

        elif ( char == '*' ):
            self.ui_state = self.STATE_MACHINE_NUMBER 
            pykka.ActorRegistry.get_by_urn ( self.lcd_urn ).tell ( { 'type' : LCDActor_home_screen } )

                        
    def handle_confirm (self, char ):
        if ( char == '#' ):
            self.ui_state = self.STATE_UNLOCK_UI
            self.buf = [] 
            auth_request = (self.mach_num, self.id_buf)

            pykka.ActorRegistry.get_by_urn ( self.ctrl_urn ).tell ( {'type': ControlActor_auth,
                                                                     'data' : auth_request } )   

        elif ( char == '*' ):
            self.ui_state = self.STATE_ID
            self.id_buf = ""
            pykka.ActorRegistry.get_by_urn ( self.lcd_urn ).tell ( {'type': LCDActor_swipe_card } )

    def handle_char ( self, char ):
        if ( char == '#' ):
           
            # parse the machine number buffer 
            if (len(self.buf) == 1):
                self.mach_num = int(self.buf[0])
            elif (len(self.buf) == 2):
                self.mach_num = int(self.buf[0]) * 10 + int(self.buf[1])
            else:
                self.mach_num = -1  


            self.buf = []             
            pykka.ActorRegistry.get_by_urn ( self.ctrl_urn ).tell ( {'type': ControlActor_MachCheck,
                                                                   'data' :  self.mach_num } )    
            self.ui_state = self.STATE_IDLE

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
    control = ControlActor.start ( )
    ui = UIActor.start ( lcd.actor_urn, control.actor_urn )
    
    keypad = KeypadActor.start ( ui.actor_urn )
    cardId = CardreadActor.start ( ui.actor_urn )
 
    keypad.tell({'type': KeypadActor_start})
    cardId.tell({'type': CardreadActor_start})
    lcd.tell({'type' : LCDActor_home_screen })

