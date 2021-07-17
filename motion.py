import time
from kinematics import KinematicsCalculator
from stepper import BYJStepper
from log import LOG as log
from key_controls import start_key_listener

log.level = "info"


class Motion(object):
    log = log

    def __init__(self, motion_config={}, kinematics_config={}, stepper_config={}):
        self.kc = KinematicsCalculator(**kinematics_config)
        self.log.info("created KinematicsCalculator")
        steppers = {k: BYJStepper(steps_per_rev=stepper_config['steps_per_rev'], pinout=v) for k, v in stepper_config['pinout'].items()}
        self.__dict__.update(steppers)
        self.log.info("initialized steppers")
        self.steps_per_rev = kinematics_config['steps_per_rev']
        self.degs_per_step = 360 / self.steps_per_rev

        self.max_z = motion_config['max_z']
        start_angles = motion_config["start_angles"]
        start_xyc = motion_config["start_xyc"]

        if start_angles == () and (isinstance(start_xyc, tuple) or isinstance(start_xyc, list)) and len(start_xyc) == 3:
            self.x, self.y, self.cam_dist = start_xyc
            self.t1, self.t2, self.t3 = self._get_angles(*start_xyc)
            start_angles = (self.t1, self.t2, self.t3)
        elif start_angles in [(),[]] and start_xyc in [(),[]]:
            start_angles = (90, 90, 90)
            self.t1, self.t2, self.t3 = start_angles
            self.x, self.y, self.cam_dist = self._get_xyc(self.t1, self.t2, self.t3)
        elif (isinstance(start_angles, tuple) or isinstance(start_angles, list)) and len(start_angles) == 3 and start_xyc in [(),[]]:
            self.t1, self.t2, self.t3 = start_angles
            self.x, self.y, self.cam_dist = self._get_xyc(self.t1, self.t2, self.t3)
        else:
            raise Exception("overconstrained")

        self.start_angles = start_angles
        self.s1, self.s2, self.s3 = [self._nearest_step(theta_degs) for theta_degs in start_angles]
        # self.enable()

    def _get_cam_dist(self, z):
        return self.max_z - z

    def _get_z(self, cam_dist):
        return self.max_z - cam_dist

    def _get_xyc(self, theta_1_degs, theta_2_degs, theta_3_degs):
        x, y, z = self.kc.get_xyz(theta_1_degs, theta_2_degs, theta_3_degs)
        cam_dist = self._get_cam_dist(z)
        return x, y, cam_dist

    def set_xyc(self, x, y, cam_dist):
        self.t1, self.t2, self.t3 = self._get_angles(x, y, cam_dist)
        self.s1, self.s2, self.s3 = self._nearest_steps(self.t1, self.t2, self.t3)
        self.x = x
        self.y = y
        self.cam_dist = cam_dist

    def _get_angles(self, x, y, cam_dist):
        z = self._get_z(cam_dist)
        theta_1_degs, theta_2_degs, theta_3_degs = self.kc.get_angles(x, y, z)
        return theta_1_degs, theta_2_degs, theta_3_degs

    def set_angles(self, theta_1_degs, theta_2_degs, theta_3_degs):
        self.t1, self.t2, self.t3 = theta_1_degs, theta_2_degs, theta_3_degs
        self.s1, self.s2, self.s3 = self._nearest_steps(theta_1_degs, theta_2_degs, theta_3_degs)
        self.x, self.y, self.cam_dist = self._get_xyc(theta_1_degs, theta_2_degs, theta_3_degs)

    def _step_angle(self, steps):
        return self.degs_per_step*steps

    def _step_angles(self, s1, s2, s3):
        theta_1_degs, theta_2_degs, theta_3_degs = [self._step_angle(steps) for steps in (s1, s2, s3)]
        return theta_1_degs, theta_2_degs, theta_3_degs

    def _nearest_step(self, theta_degs):
        return round(theta_degs/self.degs_per_step)

    def _nearest_steps(self, theta_1_degs, theta_2_degs, theta_3_degs):
        s1, s2, s3 = [self._nearest_step(theta_degs) for theta_degs in (theta_1_degs, theta_2_degs, theta_3_degs)]
        return s1, s2, s3

    def _get_steps(self, x, y, cam_dist):
        theta_1_degs, theta_2_degs, theta_3_degs = self._get_angles(x, y, cam_dist)
        s1, s2, s3 = self._nearest_steps(theta_1_degs, theta_2_degs, theta_3_degs)
        return s1, s2, s3

    def _get_angles_xyc(self, s1, s2, s3):
        theta_1_degs, theta_2_degs, theta_3_degs = self._step_angles(s1, s2, s3)
        x, y, cam_dist = self._get_xyc(theta_1_degs, theta_2_degs, theta_3_degs)
        return (theta_1_degs, theta_2_degs, theta_3_degs), (x, y, cam_dist)

    def set_steps(self, s1, s2, s3):
        (self.t1, self.t2, self.t3), (self.x, self.y, self.cam_dist) = self._get_angles_xyc(s1, s2, s3)

    def move_to(self, x, y, cam_dist):
        s1, s2, s3 = self._get_steps(x, y, cam_dist)
        max_chunk_angle = 10
        max_chunk_steps = self._nearest_step(max_chunk_angle)
        # max_chunk_steps = 1

        i = 0
        self.log.info(f"moving from {(self.x, self.y, self.cam_dist)} ({(self.s1, self.s2, self.s3)} steps) to {(x, y, cam_dist)}({(s1, s2, s3)} steps)")
        while not self._move_towards(s1, s2, s3, max_chunk_steps) and i < ((self.steps_per_rev/2) // max_chunk_steps):
            i += 1
        self.set_steps(s1, s2, s3)
        
    def move(self, dx, dy, dcam_dist):
        return self.move_to(self.x + dx, self.y + dy, self.cam_dist + dcam_dist)

    def _move_towards(self, s1, s2, s3, max_steps=None):
        ds1 = s1 - self.s1
        ds2 = s2 - self.s2
        ds3 = s3 - self.s3
        if max_steps is not None:
            ds1 = [abs(ds1), max_steps][1 * (abs(ds1) > max_steps)] * (2 * (ds1 > 0) - 1)
            ds2 = [abs(ds2), max_steps][1 * (abs(ds2) > max_steps)] * (2 * (ds2 > 0) - 1)
            ds3 = [abs(ds3), max_steps][1 * (abs(ds3) > max_steps)] * (2 * (ds3 > 0) - 1)

        self.log.debug(f"moving from {(self.s1, self.s2, self.s3)} towards {(s1, s2, s3)}")
        self._move_stepper(1, ds1)
        #time.sleep(0.1)
        self._move_stepper(2, ds2)
        #time.sleep(0.1)
        self._move_stepper(3, ds3)
        #time.sleep(0.1)
        return all([s1 == self.s1, s2 == self.s2, s3 == self.s3])

    def _move_stepper(self, n, steps):
        stepper = getattr(self, f'stepper{n}')
        stepper.move(-steps)
        setattr(self, f's{n}', getattr(self, f's{n}') + steps)
        self.log.debug(f"moving stepper{n} {steps} steps")
        
    def disable(self):
        self.stepper1.disable()
        self.stepper2.disable()
        self.stepper3.disable()
    
    def enable(self):
        self.stepper1.enable()
        self.stepper2.enable()
        self.stepper3.enable()
        
    def zero(self):
        self.set_angles(90, 90, 90)
        
    def rezero(self):
        self.disable()
        input("Move arms to zero position, then press Enter: ")
        self.enable()
        self.zero()

    def position(self):
        return (self.x, self.y, self.cam_dist), (self.t1, self.t2, self.t3), (self.s1, self.s2, self.s3)

    def keyboard_motion(self, d=1):
        def get_step():
            return d
        
        def set_step(k):
            global d
            d = 1*k
        
        start_key_listener({
                'left': lambda k: self.move(-get_step(), 0, 0),
                'right': lambda k: self.move(get_step(), 0, 0),
                'enter': lambda k: self.move(0, 0, -get_step()),
                'shift': lambda k: self.move(0, 0, get_step()),
                'up': lambda k: self.move(0, get_step(), 0),
                'down': lambda k: self.move(0, -get_step(), 0),
            },{
                '1234567890': set_step,
            })


if __name__ == "__main__":
    from load_config import motion_config, kinematics_config, stepper_config
    mp = Motion(motion_config=motion_config, kinematics_config=kinematics_config, stepper_config=stepper_config)
