import sys
import time
import threading
import serial

from Display_Output import HT16K33_quad_alpha
from GPS_Module import ultimate_gps_module

# i2c setup
I2C_CHANNEL = 1
HT16K33_ADDR = 0x70

# gps setup
SERIAL_CHANNEL = "/dev/ttyS0"
BAUDRATE = 9600

if __name__ == "__main__":
    # Initialize display
    output = HT16K33_quad_alpha(i2c_channel=I2C_CHANNEL, dev_address=HT16K33_ADDR)

    # Initialize GPS module
    gps_connected = False
    while gps_connected == False:
        gps = ultimate_gps_module(SERIAL_CHANNEL, BAUDRATE)
        if gps.check_is_ready():
            gps_connected = True
        else:
            output.loading_sequence()
    
    output.print_string(message="DIGI")

    while(1):
        try:
            speed = round(gps.get_current_speed(print_to_console=0))
            speed = str(speed)
            speed = ((4 - len(speed)) * " ") + speed
            output.print_string(message=speed)
            print(speed)
            time.sleep(0.01)
            
            # text = input("Update display?")
            # text = text.lower()
            # if text == "gps":
            #     gps.get_current_location()
            # elif text == "speed":
            #     gps.get_current_speed()
            # else:  
            #     output.print_string(message=text)

        except KeyboardInterrupt:
            gps.deinit()
            output.deinit()
            sys.exit()
