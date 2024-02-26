from PIL import Image
from picamera import PiCamera
import numpy as np

from cam.leds import LEDs


class MyCamera(PiCamera):
    def __init__(self, **led_config):
        self.leds = LEDs(**led_config)
        self.overlay_fn = None
        self.overlay_img = None
        self.overlay_crop_coords = None
        self.overlay = None
        self.overlay_params = [0, 0, 50, 120]  # right, up, zoom, alpha (dx, dy, dz, da)
        super().__init__()

    @staticmethod
    def get_crop_coords(img):
        arr = np.asarray(img)[:, :, 2]
        coords = np.argwhere(arr > 5)
        bottom, left = coords.min(axis=0)
        top, right = coords.max(axis=0)
        return left, right, top, bottom

    def load_overlay(self, fn=None, dx=None, dy=None, dz=None, da=None):
        if fn is None:
            self.close_overlay()
        else:
            self.overlay_fn = fn
            self.overlay_img = Image.open(self.overlay_fn).transpose(Image.FLIP_LEFT_RIGHT)
            self.overlay_crop_coords = self.get_crop_coords(self.overlay_img)
            self.adjust_overlay(dx, dy, dz, da)

    def adjust_overlay(self, dx=0, dy=0, dz=0, da=0):
        if dx is not None:
            self.overlay_params[0] += dx
        if dy is not None:
            self.overlay_params[1] += dy
        if dz is not None:
            self.overlay_params[2] += dz
        if da is not None:
            self.overlay_params[3] += da
        self.reload_overlay()
        
    def set_alpha(self, a):
        self.overlay_params[3] = a
        self.reload_overlay()

    def reload_overlay(self):
        left, right, top, bottom = self.overlay_crop_coords
        x, y, z, a = self.overlay_params
        img = self.overlay_img.crop((left - z - x, bottom - z + y, right + z - x, top + z + y))
        pad_x, pad_y = (32, 16)
        pad = Image.new('RGB',
                        (((img.size[0] + pad_x - 1) // pad_x) * pad_x, ((img.size[1] + pad_y - 1) // pad_y) * pad_y))
        pad.paste(img, (0, 0))
        self.close_overlay()
        self.overlay = self.add_overlay(pad.tobytes(), size=img.size)
        self.overlay.alpha = a
        self.overlay.layer = 3

    def close_overlay(self):
        if self.overlay is not None:
            self.remove_overlay(self.overlay)
        self.overlay = None

    def snap(self, fn):
        self.stop_preview()
        self.close_overlay()
        temp_res = self.resolution
        self.resolution = (2592, 1944)
        self.capture(fn)
        self.resolution = temp_res
        # self.leds.off()
        self.start_preview()
        self.adjust_overlay()

def main():
    from tools.load_config import leds_config
    cam = MyCamera(**leds_config)
    return cam

if __name__ == "__main__":
    cam = main()
    cam.preview("2840.png")

