import serial

POSITION_FIX_NOT_AVAILABLE  = 0
POSITION_GPS_FIX            = 1
POSITION_DIFF_GPS_FIX       = 2

NMEA_GGA = "$GPGGA"
NMEA_GSA = "$GPGSA"
NMEA_GSV = "$GPGSV"
NMEA_RMC = "$GPRMC"
NMEA_VTG = "$GPVTG"

class ultimate_gps_module:
    def __init__(self, serial_port, baud_rate):
        # Connect to GPS module via serial port
        self.__ser = serial.Serial(serial_port, baud_rate)
        if self.__ser.is_open:
            # Check if it has a satellite fix
            # if self.check_satellite_fix() == False:
            self.check_satellite_fix()
            if self.__gps_fix == False:
                # Make sure to close the connection - if we connect to the GPS module before it has found a fix,
                # we can't seem to get coordinates out even after it does get a fix!
                self.__ser.close()
    
    def check_is_ready(self):
        if self.__ser.is_open and self.__gps_fix:
            return True
        return False

    def check_satellite_fix(self):
        nmea_sentence = self.read_nmea_sentence(NMEA_GGA)
        if (int)(nmea_sentence[6]) == POSITION_FIX_NOT_AVAILABLE:
            self.__gps_fix = False
        else:
            self.__gps_fix = True

    def read_nmea_sentence(self, option):
        if self.__ser.is_open:
            sentence_found = None
            while sentence_found == None:
                # Read from GPS module and strip unecessary characters from beginning and end of string
                nmea_sentence = (str)(self.__ser.readline())
                nmea_sentence = nmea_sentence.replace('\\r\\n\'', '')
                nmea_sentence = nmea_sentence[2:]
                if option in nmea_sentence:
                    nmea_sentence = nmea_sentence.split(",")
                    sentence_found = True
                    return nmea_sentence

    def get_current_location(self):
        if self.__gps_fix:
            gga_sentence = self.read_nmea_sentence(NMEA_GGA)
            latitude_nmea = (float)(gga_sentence[2])
            latitude_degrees = (int)(latitude_nmea / 100)
            latitude_minutes = latitude_nmea - (latitude_degrees * 100)
            latitude_dec = latitude_degrees + (latitude_minutes / 60)
            if gga_sentence[3] == 'S':
                latitude_dec = -latitude_dec
            latitude_dec = round(latitude_dec, 5)

            longitude_nmea = (float)(gga_sentence[4])
            longitude_degrees = (int)(longitude_nmea / 100)
            longitude_minutes = longitude_nmea - (longitude_degrees * 100)
            longitude_dec = longitude_degrees + (longitude_minutes / 60)
            if gga_sentence[5] == 'W':
                longitude_dec = -longitude_dec
            longitude_dec = round(longitude_dec, 5)

            print(f"{latitude_dec}, {longitude_dec}")

    def get_current_speed(self, print_to_console):
        if self.__gps_fix:
            rmc_sentence = self.read_nmea_sentence(NMEA_RMC)
            # Extract information required to find speed
            speed_knots = (float)(rmc_sentence[7])
            speed_mph = speed_knots * 1.151
            speed_kph = speed_mph * 1.609
            if print_to_console:
                print(f"{speed_knots} knots\n{speed_mph} mph\n{speed_kph} kph") 
            return speed_mph

    def deinit(self):
        # Disconnect from serial port
        if self.__ser.is_open:
            self.__ser.close()