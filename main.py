import time
from Display_Output import HT16K33_quad_alpha
from GPS_Module import ultimate_gps_module

# i2c setup
I2C_CHANNEL = 0
HT16K33_ADDR = 0x70

# gps setup
SERIAL_CHANNEL = 0
BAUDRATE = 9600
TX_PIN = 0
RX_PIN = 1

def format_speed(speed):
    """ Converts the speed from a float value into a 4 digit integer
        to be displayed on a 4 digit display."""
    speed = int(speed)
    speed = str(speed)
    speed = ((4 - len(speed)) * " ") + speed
    return speed

if __name__ == "__main__":
    # Initialize display
    output = HT16K33_quad_alpha(I2C_CHANNEL, HT16K33_ADDR)

    # Initialize GPS module
    gps = ultimate_gps_module(SERIAL_CHANNEL)
    gps_connected = False
    while gps_connected == False:
        gps.setup(BAUDRATE, TX_PIN, RX_PIN, 100)
        if gps.check_if_ready():
            gps_connected = True
        else:
            output.loading_sequence()
            time.sleep_ms(250)

    # main loop
    while(1):
        speed = gps.get_current_speed(print_to_console=0)
        print(speed)
        speed = format_speed(speed)
        output.print_string(message=speed)
        time.sleep(0.01)
