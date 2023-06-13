import sys
import time
import serial

from Display_Output import HT16K33_quad_alpha as quad_display

# i2c setup
I2C_CHANNEL = 1
HT16K33_ADDR = 0x70

if __name__ == "__main__":
    # Initialize display
    output = quad_display(i2c_channel=I2C_CHANNEL, dev_address=HT16K33_ADDR)
    output.print_string(message="Hi")

    # Open serial port - connected to GPS module
    ser = serial.Serial ("/dev/ttyS0", 9600)

    while(1):
        try:
            gps_sentence = (str)(ser.readline())

            # Strip unecessary characters from beginning and end of string
            gps_sentence = gps_sentence.replace('\\r\\n\'', '')
            gps_sentence = gps_sentence[2:]
            
            if "$GPGGA" in gps_sentence:
                gps_sentence = gps_sentence.split(",")

                # Extract information required to find location
                latitude_nmea = (float)(gps_sentence[2])
                latitude_degrees = (int)(latitude_nmea / 100)
                latitude_minutes = latitude_nmea - (latitude_degrees * 100)
                latitude_dec = latitude_degrees + (latitude_minutes / 60)
                if gps_sentence[3] == 'S':
                    latitude_dec = -latitude_dec

                longitude_nmea = (float)(gps_sentence[4])
                longitude_degrees = (int)(longitude_nmea / 100)
                longitude_minutes = longitude_nmea - (longitude_degrees * 100)
                longitude_dec = longitude_degrees + (longitude_minutes / 60)
                if gps_sentence[5] == 'W':
                    longitude_dec = -longitude_dec

                print(f"{latitude_dec}, {longitude_dec}")
                text = str(latitude_dec) + str(longitude_dec)
                output.print_string(message=text)

            # text = input("Update display? ")
            # output.print_string(message=text)
            pass
        except KeyboardInterrupt:
            # Turn it off, and close the bus!
            output.close()
            sys.exit()
