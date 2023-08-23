from machine import UART, Pin

POSITION_FIX_NOT_AVAILABLE  = 0
POSITION_GPS_FIX            = 1
POSITION_DIFF_GPS_FIX       = 2

NMEA_GGA = "$GPGGA"
NMEA_GSA = "$GPGSA"
NMEA_GSV = "$GPGSV"
NMEA_RMC = "$GPRMC"
NMEA_VTG = "$GPVTG"

DEBUG_PRINTS = 0    # Set to print debug info to console 

class ultimate_gps_module:
    """ Open connection over a UART port

    ...

    Attributes
    ----------
    serial_port : int
        ID of the UART port to be used

    Methods
    -------
    setup(baud_rate, tx_pin, rx_pin, timeout)
        Configures the serial connection and checks if the GPS module has a satellite fix

    deinit():
        Closes the serial connection
        
    check_if_ready()
        Returns True if UART has been configured and GPS has a satellite fix

    read_nmea_sentence(option)
        Reads the requested sentence from the GPS module

    get_current_location()
        Returns the current location in the format {latitude, longitude} in decimal

    get_current_speed()
        Returns the current speed in mph (as a float)
    """
    
    def __init__(self, serial_port):
        self.__uart = UART(serial_port)
    

    def setup(self, baud_rate, tx_pin, rx_pin, timeout):
        """ Configures the serial connection and checks if the GPS module has a satellite fix.

        Parameters
        ----------
        baud_rate : int
            Speed of the UART connection
        
        tx_pin : int
            GPIO number of the pin used for transmitting
        
        rx_pin : int
            GPIO number of the pin used for receiving

        timeout : int
            Maximum time to wait for the first character of a new line and als between characters. 
        """
        
        self.__uart.init(baudrate=baud_rate, tx=Pin(tx_pin), rx=Pin(rx_pin), timeout=timeout, timeout_char=timeout)
        # Check if there is a satellite fix
        self.check_satellite_fix()
        if self.__gps_fix == False:
            if DEBUG_PRINTS:
                print("No connection yet...")
        pass


    def deinit(self):
        """ Closes the serial connection.

        After calling this, a new instance needs to be created before calling setup() again.
        """
        
        # Disconnect from serial port
        self.__uart.deinit()


    def check_if_ready(self):
        if self.__uart and self.__gps_fix:
            return True
        return False


    def check_satellite_fix(self):
        nmea_sentence = self.read_nmea_sentence(NMEA_GGA)
        if nmea_sentence != None:
            if (int)(nmea_sentence[6]) == POSITION_FIX_NOT_AVAILABLE:
                self.__gps_fix = False
            else:
                self.__gps_fix = True


    def read_nmea_sentence(self, option):
        if self.__uart:
            sentence_found = None
            while sentence_found == None:
                # Read from GPS module and strip unecessary characters from beginning and end of string
                nmea_sentence = (str)(self.__uart.readline())
                nmea_sentence = nmea_sentence.replace('\\r\\n\'', '')
                nmea_sentence = nmea_sentence[2:]
                if option in nmea_sentence:
                    nmea_sentence = nmea_sentence.split(",")
                    sentence_found = True
                    return nmea_sentence


    def get_current_location(self):
        if self.__gps_fix:
            gga_sentence = self.read_nmea_sentence(NMEA_GGA)
            if gga_sentence != None:
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


    def get_current_speed(self):
        if self.__gps_fix:
            rmc_sentence = self.read_nmea_sentence(NMEA_RMC)
            if rmc_sentence != None:
                # Extract information required to find speed
                speed_knots = (float)(rmc_sentence[7])
                speed_mph = speed_knots * 1.151
                speed_kph = speed_mph * 1.609
                if DEBUG_PRINTS:
                    print(f"{speed_knots} knots\n{speed_mph} mph\n{speed_kph} kph") 
                return speed_mph