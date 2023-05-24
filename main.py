import sys
from Display_Output import HT16K33_quad_alpha as quad_display

# i2c setup
I2C_CHANNEL = 1
HT16K33_ADDR = 0x70

if __name__ == "__main__":
    # Initialize display
    output = quad_display(i2c_channel=I2C_CHANNEL, dev_address=HT16K33_ADDR)

    # Turn it on!
    output.print_string(message="Hi")

    while(1):
        try:
            text = input("Update display? ")
            output.print_string(message=text)
            pass
        except KeyboardInterrupt:
            # Turn it off, and close the bus!
            output.close()
            sys.exit()
