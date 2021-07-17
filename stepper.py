import RPi.GPIO as GPIO
import time


class Stepper(object):
    def __init__(self, speed=1, base_delay=0.001, microsteps_per_step=8):
        self.speed = speed
        self.base_delay = base_delay

        self.positions = {
            'current': 0,
            'min': None,
            'max': None,
            'home': 0,
        }

        self.units = {
            'microstep': 1 / microsteps_per_step,
            'step': 1,
        }

    def set_position(self, name, n, units='step'):
        self.positions[name] = n * self.units[unit]

    def convert(self, n, input_units='step', output_units='step'):
        return n * self.units[output_units] / self.units[input_units]

    def _get_limit_error(which="min"):
        """create error message when position limit is reached"""
        return f"Limit Error: Unable to move due to {which} position limit."

    def _log_limit_error(self, which="min", log_func=print):
        """log error message when position limit is reached"""
        e = self._get_limit_error(which=which)
        log_func(e)
        return e

    def _check_limit(self, steps):
        """check if position limit is reached"""
        min_limit_failed = not (
                    self.positions['min'] is None or (self.positions['current'] + steps) >= self.positions['min'])
        max_limit_failed = not (
                    self.positions['max'] is None or (self.positions['current'] + steps) <= self.positions['max'])
        if not (min_limit_failed or max_limit_failed):
            return False
        elif min_limit_failed:
            return self._log_limit_error('min')
        elif max_limit_failed:
            return self._log_limit_error('max')

    def _get_delay(self, delay=None, speed=None):
        if speed is None:
            speed = self.speed
        if delay is None:
            delay = self.base_delay / speed
        return delay

    def set_speed(self, speed=None, delay=None, base_delay=None):
        if delay is not None:
            self.speed = delay / self.base_delay
        if speed is not None:
            self.speed = speed
        if base_delay is not None:
            self.base_delay = base_delay

    def _microstep(self, direction=1, delay=0.001):
        """move one microstep"""
        return direction * self.units['microstep']

    def set_microstep_mode(self, microsteps_per_step=8):
        self.units['microstep'] = 1 / microsteps_per_step

    def move(self, n, units='step', limit_condition="step", delay=None):
        """move n units"""
        # force, move, step, microstep
        direction = 2 * (n > 0) - 1
        steps = n * self.units[units]
        microsteps = steps / self.units['microstep']
        microsteps_moved = 0

        if limit_condition == 'force':
            for _ in range(abs(microsteps)):
                microsteps_moved += self._microstep(direction=direction, delay=delay)
        elif limit_condition == 'move':
            if not self._check_limit(steps=steps):
                for _ in range(abs(microsteps)):
                    microsteps_moved += self._microstep(direction=direction, delay=delay)
        elif limit_condition == 'step':
            for _ in range(abs(steps)):
                if not self._check_limit(steps=direction):
                    for _ in range(int(1 / self.units['microstep'])):
                        microsteps_moved += self._microstep(direction=direction, delay=delay)
        elif limit_condition == 'microstep':
            for _ in range(abs(microsteps)):
                if not self._check_limit(steps=direction):
                    microsteps_moved += self._microstep(direction=direction, delay=delay)
        else:
            raise Exception(f"Unknown limit condition: {limit_condition}")

        return microsteps_moved

    def move_to(self, position, units='step', limit_condition="step", delay=0.005):
        """move to a position"""
        if position in self.positions:
            position = self.positions[position]
            units = 'step'

        if units != 'step':
            position = self.units[units] * position
            units = 'step'

        n = position - self.positions['current']
        return self.move(n, units=units, limit_condition=limit_condition, delay=delay)


class BYJStepper(Stepper):
    step_sequence = [
        [1, 0, 0, 1],
        [0, 0, 0, 1],
        [0, 0, 1, 1],
        [0, 0, 1, 0],
        [0, 1, 1, 0],
        [0, 1, 0, 0],
        [1, 1, 0, 0],
        [1, 0, 0, 0],
    ]

    def __init__(self, pinout, steps_per_rev=509.4716, speed=1, base_delay=0.001, microsteps_per_step=8):
        self.IN1 = pinout['IN1']
        self.IN2 = pinout['IN2']
        self.IN3 = pinout['IN3']
        self.IN4 = pinout['IN4']
        self.pins = [self.IN1, self.IN2, self.IN3, self.IN4]
        super().__init__(speed=speed, base_delay=base_delay, microsteps_per_step=microsteps_per_step)
        self.units['rev'] = steps_per_rev
        self.setup()

    def setup(self):
        """setup GPIO pins"""
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        for pin in self.pins:
            GPIO.setup(pin, GPIO.OUT)

    def _microstep(self, direction=1, delay=None):
        """move one microstep"""
        delay = self._get_delay(delay=delay)
        microstep_sequence = self.step_sequence[
            int(self.positions['current'] / self.units['microstep'] % (1 / self.units['microstep']))]
        for i, pin in enumerate(self.pins):
            GPIO.output(pin, microstep_sequence[i])
        time.sleep(delay)
        self.positions['current'] += direction * self.units['microstep']
        return direction * self.units['microstep']

    def set_microstep_mode(self, microsteps_per_step=8):
        self.units['microstep'] = 1 / microsteps_per_step

    def disable(self):
        for i, pin in enumerate(self.pins):
            GPIO.output(pin, 0)
    
    def enable(self):
        for i, pin in enumerate(self.pins):
            GPIO.output(pin, 1)


if __name__ == '__main__':
    from load_config import stepper_config
    steppers = {k: BYJStepper(steps_per_rev=stepper_config['steps_per_rev'], pinout=v) for k, v in stepper_config['pinout'].items()}
