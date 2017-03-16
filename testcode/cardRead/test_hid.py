from keyboard_alike import reader
import string

class BarCodeReader(reader.Reader):
    """
    """
    pass


if __name__ == "__main__":

    print("Scan card now...")

    # Tested with my card reader: 208 bytes for student IDs
    # and chunk size is 8 bytes -tk 1/25/16
    # Device vendor ID and product ID can be found using lsbusb 
    reader = BarCodeReader(0xc216, 0x0180, 208, 8, should_reset=False, 
                            timeout_msec=100, debug=False)
    reader.initialize()
    cardData = reader.read().strip()

    print("ORIG:" + cardData)

    start = string.find(cardData, ';')

    print("START:" + str(start))

    new = cardData[start+1:]
    print("NEW:" + new)

    end = string.find(new, "/")
    final = new[:end]
    print("FINAL:" + final)

#    if start == -1 | end == -1 | 

    reader.disconnect()
