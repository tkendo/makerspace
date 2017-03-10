
from keyboard_alike import reader
import string
import pykka

class BarCodeReader(reader.Reader):
    """
    """
    pass

def process_cardread( reader, ui_urn, lcd_urn  ):


    lcd_actor = pykka.ActorRegistry.get_by_urn ( lcd_urn )
    while ( 1 ): 
        cardData = reader.read().strip()
        start = string.find(cardData, ';')
        new = cardData[start+1:]
        end = string.find(new, "/")
        final = new[:end]
        print("FINAL:" + final)
        
        #ui_actor.tell ( {'type' : 'id',
        #                 'data' : digit } )
        lcd_actor.tell ( {'type' : 'id',
                         'data' : final } )
     

    reader.disconnect()




