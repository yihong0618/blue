import serial


def set_bluetooth_config(serial_path):
    """
    set the config for this bluetooth printer
    return the serial had set
    """
    ser = serial.Serial(serial_path)
    # enable the printer
    ser.write(bytes.fromhex("10FF40"))
    ser.write(bytes.fromhex("10FFF103"))
    # disable shutdown
    ser.write(bytes.fromhex("10FF120000"))
    # set density (0000 for low, 0100 for normal, 0200 for high)
    ser.write(bytes.fromhex("10FF10000200".ljust(256, "0")))
    return ser
