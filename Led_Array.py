from neopixel import Adafruit_NeoPixel

class Led_Array(object):
    def __init__(self):
        self.LED_COUNT      = 256      # Number of LED pixels.
        self.LED_PIN        = 18      # GPIO pin connected to the pixels (must support PWM!).
        self.LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
        self.LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
        self.LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
        self.LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
        self.ROW_WIDTH      = 8       # Number of LEDs in each row of the array

        # Create NeoPixel object with appropriate configuration.
        self.led_array = Adafruit_NeoPixel( self.LED_COUNT,
                                            self.LED_PIN,
                                            self.LED_FREQ_HZ,
                                            self.LED_DMA,
                                            self.LED_INVERT,
                                            self.LED_BRIGHTNESS)

    	# Intialize the library (must be called once before other functions).
        self.led_array.begin()
    
    def _info(self):
        return self.LED_COUNT, self.LED_PIN, self.LED_BRIGHTNESS, self.ROW_WIDTH

    def setRowColor(self, row_number, color):
        strip = self.led_array
        start = 0 + row_number*self.ROW_WIDTH
        end = start + self.ROW_WIDTH
        for i in range(start, end):
            strip.setPixelColor(i, color)
        # strip.show()

    def fill_up_to(self, row, color):
        #strip = self.led_array
        for i in range(row+1):
            self.setRowColor(i,color)

    def empty_array(self):
        strip = self.led_array
        for i in range(256):
            strip.setPixelColorRGB(i,0,0,0)
        # strip.show()

    def render(self):
        strip = self.led_array
        strip.show()

    def fill_rect(self, i, width, color):
        start = i
        end = start + width
        if (end < start):
            raise NameError('cant create a negative rectangle')
        if(start > 31):
            start = 31
            end = 31
        for i in range(start,end):
            self.setRowColor(i,color)


def Color(red, green, blue):
    """Convert the provided red, green, blue color to a 24-bit color value.
    Each color component should be a value 0-255 where 0 is the lowest intensity
    and 255 is the highest intensity.
    """
    return (red << 16) | (green << 8) | blue
