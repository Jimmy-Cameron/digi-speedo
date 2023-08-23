import time
import Display_Output
from GPS_Module import ultimate_gps_module

# i2c setup
I2C_CHANNEL = 0
HT16K33_ADDR = 0x70

# gps setup
SERIAL_CHANNEL = 0
BAUDRATE = 9600

if __name__ == "__main__":
    # Initialize display
    output = Display_Output.HT16K33_quad_alpha(I2C_CHANNEL, HT16K33_ADDR)

    # Initialize GPS module
    gps_connected = False
    while gps_connected == False:
        gps = ultimate_gps_module(SERIAL_CHANNEL, BAUDRATE)
        if gps.check_is_ready():
            gps_connected = True
        else:
            output.loading_sequence()
            time.sleep_ms(250)

    # main loop
    while(1):
        # speed = round(gps.get_current_speed(print_to_console=0))
        speed = gps.get_current_speed(print_to_console=0)
        print(speed)
        speed = int(speed)
        speed = str(speed)
        speed = ((4 - len(speed)) * " ") + speed
        output.print_string(message=speed)
        time.sleep(0.01)
