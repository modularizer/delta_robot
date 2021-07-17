import math


class QuickMaths(object):
    clean_sines = {
        0: 0,
        30: 0.5,
        45: (2**0.5)/2,
        60: (3**0.5)/2,
        90: 1,
        120: (3**0.5)/2,
        135: (2**0.5)/2,
        150: 0.5,
        180: 0,
        210: -0.5,
        225: -(2**0.5)/2,
        240: -(3**0.5)/2,
        270: -1,
        300: -(3**0.5)/2,
        315: -(2**0.5)/2,
        330: -0.5,
    }

    @staticmethod
    def root(n):
        return n**0.5

    @staticmethod
    def sind(degs):
        degs = degs % 360
        if degs in QuickMaths.clean_sines:
            return QuickMaths.clean_sines[degs]
        return math.sin(math.radians(degs))

    @staticmethod
    def cosd(degs):
        degs = degs % 360
        if degs in QuickMaths.clean_sines:
            return QuickMaths.clean_sines[(degs + 90)%360]
        return math.cos(math.radians(degs))

    @staticmethod
    def tand(degs):
        return QuickMaths.sind(degs)/QuickMaths.cosd(degs)

    def __getattr__(self, item):
        if getattr(math, item, None) is not None:
            return getattr(math, item)

        if item.startswith('root'):
            return int(item[4:])**0.5

        if item.startswith('sin') and item[3:].isnumeric():
            return self.sind(int(item[3:]))

        if item.startswith('cos') and item[3:].isnumeric():
            return self.cosd(int(item[3:]))

        if item.startswith('tan') and item[3:].isnumeric():
            return self.tand(int(item[3:]))

        if item in ['atand', 'acosd', 'asind']:
            return lambda a: getattr(math, item[:-1])(math.radians(a))


quick_maths = QuickMaths()

if __name__ == "__main__":
    qm = quick_maths
    print(f"root49 = {qm.root49}")
    print(f"sin30 = {qm.sin30}")