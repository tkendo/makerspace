
from keyboard_alike import reader
import string
import pykka
import server_actors

class BarCodeReader(reader.Reader):
    """
    """
    pass

def process_cardread( reader, ui_urn  ): 
    ui_actor = pykka.ActorRegistry.get_by_urn ( ui_urn )
    while ( 1 ): 
        cardData = reader.read().strip()
        start = string.find(cardData, ';')
        new = cardData[start+1:]
        end = string.find(new, "/")
        final = new[:end]
        
        ui_actor.tell ( {'type' : server_actors.UIActor_receive_id,
                         'data' : final } )

     

    reader.disconnect()




