from motion import Motion
from cam import MyCamera

from tools.key_controls import start_key_listener
from tools.load_config import motion_config, kinematics_config, stepper_config, leds_config

class Robot(Motion, MyCamera):
    def __init__(self,
                 motion_config=motion_config,
                 kinematics_config=kinematics_config,
                 stepper_config=stepper_config,
                 leds_config=leds_config):
        Motion.__init__(self, motion_config=motion_config, kinematics_config=kinematics_config, stepper_config=stepper_config)
        MyCamera.__init__(self, **leds_config)
        
    def key_control(self, overlay_fn=None):
        step = 2
        def get_step():
            print(step)
            return step
        
        def set_step(k):
            global step
            print(f"setting step to {k}")
            step = 1*k
            
            
        try:
            self.leds.on()
            self.start_preview()
            self.load_overlay(fn=overlay_fn)
            
            start_key_listener({
                # overlay controls
                'o': lambda k: self.adjust_overlay(),
                'p': lambda k: self.close_overlay(),
                'a': lambda k: self.adjust_overlay(dx=-step),
                'd': lambda k: self.adjust_overlay(dx=step),
                's': lambda k: self.adjust_overlay(dy=-step),
                'w': lambda k: self.adjust_overlay(dy=step),
                'e': lambda k: self.adjust_overlay(dz=get_step()),
                'q': lambda k: self.adjust_overlay(dz=-get_step()),
                't': lambda k: self.adjust_overlay(da=-get_step()),
                'r': lambda k: self.adjust_overlay(da=get_step()),
                'y': lambda k: self.set_alpha(0),
                'u': lambda k: self.set_alpha(100),
                'i': lambda k: self.set_alpha(255),
                
                # led controls
                '/': lambda k: self.leds.on(),
                '.': lambda k: self.leds.adjust_brightness(-10 * get_step()),
                ',': lambda k: self.leds.adjust_brightness(10 * get_step()),
                'x': lambda k: self.leds.set_group([2,3,4,5]),
                'c': lambda k: self.leds.set_group([6,7,8]),
                'v': lambda k: self.leds.set_group([9,10,11,12]),
                'b': lambda k: self.leds.set_group([13,14,15]),
                'n': lambda k: self.leds.all_on(0,255,0),
                'm': lambda k: self.leds.all_on(255, 0,255),
                'z': lambda k: self.leds.off(),
                
                # motion controls
                'right': lambda k: self.move(-get_step(), 0, 0),
                'left': lambda k: self.move(get_step(), 0, 0),
                'page_up': lambda k: self.move(0, 0, -get_step()),
                'page_down': lambda k: self.move(0, 0, get_step()),
                'up': lambda k: self.move(0, get_step(), 0),
                'down': lambda k: self.move(0, -get_step(), 0),
                'enter': lambda k: self.enable(),
                'backspace': lambda k: self.disable(),
            },{
                '123456789': lambda k: set_step(k),
                'ABCDEFGHIJKLMNOPQRSTUVWXYZ': lambda k: self.snap(f"{k}.png"),
            })
        finally:
            self.stop_preview()
            self.close_overlay()
            self.leds.off()


if __name__ == "__main__":
    r = Robot()
    