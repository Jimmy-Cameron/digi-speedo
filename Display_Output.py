import smbus
import time

HT16K33_ON      = 0x21  #  0 = off   1 = on
HT16K33_STANDBY = 0x20  #  bit xxxxxxx0

#  bit pattern 1000 0xxy
#  y    =  display on / off
#  xx   =  00=off     01=2Hz     10 = 1Hz     11 = 0.5Hz
HT16K33_DISPLAYON       = 0x81
HT16K33_DISPLAYOFF      = 0x80
HT16K33_BLINKON0_5HZ    = 0x87
HT16K33_BLINKON1HZ      = 0x85
HT16K33_BLINKON2HZ      = 0x83
HT16K33_STEADYON        = 0x81

#  bit pattern 1110 xxxx
#  xxxx    =  0000 .. 1111 (0 - F)
HT16K33_BRIGHTNESS      = 0xE0

display_characters = {
    # Numbers
    "0" : "0x0C3F",
    "1" : "0x0406",
    "2" : "0x00DB",
    "3" : "0x008F",
    "4" : "0x00E6",
    "5" : "0x00ED",
    "6" : "0x00FD",
    "7" : "0x1401",
    "8" : "0x00FF",
    "9" : "0x00E7",

    # Letters
    "A" : "0x00F7",
    "B" : "0x128F",
    "C" : "0x0039",
    "D" : "0x120F",
    "E" : "0x00F9",
    "F" : "0x00F1",
    "G" : "0x00BD",
    "H" : "0x00F6",
    "I" : "0x1209",
    "J" : "0x001E",
    "K" : "0x2470",
    "L" : "0x0038",
    "M" : "0x0536",
    "N" : "0x2136",
    "O" : "0x003F",
    "P" : "0x00F3",
    "Q" : "0x203F",
    "R" : "0x20F3",
    "S" : "0x018D",
    "T" : "0x1201",
    "U" : "0x003E",
    "V" : "0x0C30",
    "W" : "0x2836",
    "X" : "0x2D00",
    "Y" : "0x1500",
    "Z" : "0x0C09",

    # Special characters
    " "  : "0x0000",
    "_"  : "0x0008",
    "*"  : "0x3f00",
    "?"  : "0x1083",
    "-"  : "0x00C0",
    "+"  : "0x12C0",
    "="  : "0x00C8",
    "$"  : "0x12ED",
    "<"  : "0x2400",
    ">"  : "0x0900",
    "/"  : "0x0C00",
    "\\" : "0x2100",
    "["  : "0x0039",
    "]"  : "0x000F",
}

class HT16K33_quad_alpha:
    def __init__(self, i2c_channel, dev_address):
        self.__addr = dev_address
        self.__bus = smbus.SMBus(i2c_channel)

        self.__bus.write_byte(self.__addr, HT16K33_ON)
        self.__bus.write_byte(self.__addr, HT16K33_DISPLAYON)
        self.__bus.write_byte(self.__addr, HT16K33_BRIGHTNESS)
        self.__bus.write_byte(self.__addr, HT16K33_STEADYON)

        self.clear_display()

    # If the message is longer than 4 characters, the display will scroll at 0.5Hz
    def print_string(self, message):
        self.clear_display()

        # Dictionary only contains upper case letters
        upper_message = message.upper()

        # Display the string
        if len(upper_message) > 4:
            # Message is longer than the display, must be scrolled
            # Start with all characters blanked
            scrolling_buffer = [0, 0, 0, 0, 0, 0, 0, 0]
            for char in upper_message:
                # Append the next character to the list
                scrolling_buffer.append( int(display_characters.get(char, "0x2D00"), 16) & 0x00FF)
                scrolling_buffer.append((int(display_characters.get(char, "0x2D00"), 16) & 0xFF00) >> 8)
                # Delete the oldest character from the list
                scrolling_buffer.pop(0)
                scrolling_buffer.pop(0)

                # Show the scrolling buffer, updating at 0.5 Hz
                self.__bus.write_i2c_block_data(self.__addr, 0, scrolling_buffer)
                time.sleep(0.5)

            # All of the message has been displayed, but we need to carry on with some blank characters
            # to move the message off the display
            for blank in range(3):
                # Append a blank character
                scrolling_buffer.append(0x00)
                scrolling_buffer.append(0x00)
                # Delete the oldest character from the list
                scrolling_buffer.pop(0)
                scrolling_buffer.pop(0)

                self.__bus.write_i2c_block_data(self.__addr, 0, scrolling_buffer)
                time.sleep(0.5)
            self.clear_display()
        else:
            # Lookup each character from the dictionary and append the hex to the output list
            output = []
            for char in upper_message:
                output.append( int(display_characters.get(char, "0x2D00"), 16) & 0x00FF)
                output.append((int(display_characters.get(char, "0x2D00"), 16) & 0xFF00) >> 8)

            self.__bus.write_i2c_block_data(self.__addr, 0, output)

    def clear_display(self):
        all_clear = [0, 0, 0, 0, 0, 0, 0, 0]
        self.__bus.write_i2c_block_data(self.__addr, 0, all_clear)

    def close(self):
        self.clear_display()
        self.__bus.close()