from keyboard_alike import reader


class BarCodeReader(reader.Reader):
    """
    """
    pass


if __name__ == "__main__":

    print("Scan card now...")

    # Tested with my card reader: 208 bytes for student IDs
    # and chunk size is 8 bytes -tk 1/25/16
    # Device vendor ID and product ID can be found using lsbusb 
    reader = BarCodeReader(0xc216, 0x0180, 208, 8, should_reset=False, debug=False)
    reader.initialize()
    print(reader.read().strip())

    reader.disconnect()
