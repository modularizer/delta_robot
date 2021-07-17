import board
import neopixel


class LEDs(neopixel.NeoPixel):
    """class to interact with NeoPixel LEDs using Raspberry Pi"""
    def __init__(self, pinout=18, default_inds=range(5), num_leds=60, default_brightness=255):
        self.pin = getattr(board, f"D{pinout}")
        self.default_inds = default_inds
        self.default_brightness = default_brightness
        self.num_leds = num_leds
        try:
            super().__init__(self.pin, self.num_leds)
        except:
            pass

    def display(self, r=None, g=None, b=None, inds=None):
        try:
            if r is None:
                r = self.default_brightness
            if g is None:
                g = r
            if b is None:
                b = r
            if inds is None:
                inds = self.default_inds
            for i in inds:
                self[i] = (r, g, b)
        except:
            pass

    def adjust_brightness(self, db):
        self.default_brightness += db
        self.display()

    def on(self, inds=None):
        if inds is None:
            inds = self.default_inds
        self.display(inds=inds)

    def all_on(self, r=None, g=None, b=None):
        self.display(r=r, g=g, b=b, inds=range(self.num_leds))

    def off(self, inds=None):
        self.display(0, inds=inds)

    def set_single(self, ind):
        self.off()
        self.display(inds=[ind])
        
    def set_group(self, inds):
        self.off()
        self.display(inds=inds)


if __name__ == "__main__":
    leds = LEDs()