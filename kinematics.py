from quick_maths import quick_maths as qm


class KinematicsCalculator(object):
    """adapted from https://www.marginallyclever.com/other/samples/fk-ik-test.html"""
    def __init__(self, **config):
        self.r_top = 1
        self.r_bottom = 1
        self.bicep = 1
        self.forearm = 1
        self.steps_per_rev = 360
        self.__dict__.update(config)

    def get_xyz(self, theta_1_degs, theta_2_degs, theta_3_degs):
        t = (self.r_top - self.r_bottom)*qm.tan30/2

        # get position of elbow 1
        x1 = 0
        y1 = -(t + self.bicep*qm.cosd(theta_1_degs))
        z1 = -self.bicep*qm.sind(theta_1_degs)

        # get position of elbow 2
        x2 = (t + self.bicep*qm.cosd(theta_2_degs))*qm.sin30*qm.tan60
        y2 = x2/qm.tan60
        z2 = -self.bicep*qm.sind(theta_2_degs)

        # get position of elbow 3
        x3 = -(t + self.bicep*qm.cosd(theta_3_degs))*qm.sin30*qm.tan60
        y3 = -x3/qm.tan60
        z3 = -self.bicep*qm.sind(theta_3_degs)

        denominator = (y2 - y1) * x3 - (y3 - y1) * x2

        w1 = x1 ** 2 + y1 ** 2 + z1 ** 2
        w2 = x2 ** 2 + y2 ** 2 + z2 ** 2
        w3 = x3 ** 2 + y3 ** 2 + z3 ** 2

        # x = (a1*z + b1)/denominator
        a1 = (z2 - z1) * (y3 - y1) - (z3 - z1) * (y2 - y1)
        b1 = -((w2 - w1) * (y3 - y1) - (w3 - w1) * (y2 - y1)) / 2

        # y = (a2*z + b2)/denominator
        a2 = -(z2 - z1) * x3 + (z3 - z1) * x2
        b2 = ((w2 - w1) * x3 - (w3 - w1) * x2) / 2

        #  a*z^2 + b*z + c = 0
        a = a1 ** 2 + a2 ** 2 + denominator ** 2
        b = 2.0 * (a1 * b1 + a2 * (b2 - y1 * denominator) - z1 * denominator ** 2)
        c = (b2 - y1 * denominator) ** 2 + b1 ** 2 + (denominator ** 2) * (z1 ** 2 - self.forearm ** 2)

        # determinant
        determinant = b ** 2 - 4 * a * c

        if determinant < 0:
            return None, None, None

        # get position of center of bottom plate
        z0 = -0.5 * (b + determinant ** 0.5) / a
        x0 = (a1 * z0 + b1) / denominator
        y0 = (a2 * z0 + b2) / denominator

        return x0, y0, z0

    def _calc_angle_yz(self, x0, y0, z0):
        edge_y = y0 - (self.r_bottom / 2) * qm.tan30

        y1 = -(self.r_top / 2) * qm.tan30

        # z = a + b * y
        a = (x0 ** 2 + edge_y ** 2 + z0 ** 2 + self.bicep ** 2 - self.forearm ** 2 - y1 ** 2) / (2 * z0)
        b = (y1 - edge_y) / z0

        discriminant = -(a + b * y1) * (a + b * y1) + self.bicep * (b ** 2 * self.bicep + self.bicep)
        if discriminant < 0:
            return None

        yj = (y1 - a*b - discriminant**0.5)/(b**2 + 1)
        zj = a + b * yj

        theta_degs = qm.degrees(qm.atan(-zj/(y1 - yj))) + 180 * (yj > y1)
        return theta_degs

    def get_angles(self, x0, y0, z0):
        theta_1_degs = self._calc_angle_yz(x0, y0, z0)
        theta_2_degs = self._calc_angle_yz(x0 * qm.cos120 + y0 * qm.sin120, y0*qm.cos120-x0 * qm.sin120, z0) # rotate coords to +120 deg
        theta_3_degs = self._calc_angle_yz(x0 * qm.cos240 + y0 * qm.sin240, y0*qm.cos240-x0 * qm.sin240, z0) # rotate coords to +240 deg
        return theta_1_degs, theta_2_degs, theta_3_degs

    def get_bounds(self):
        max_z = -self.r_bottom - self.r_top - self.forearm - self.bicep
        min_z = -max_z
        step_degs = self.steps_per_rev / 360

        zs_360 = [self.get_xyz(step_degs*degs, step_degs*degs, step_degs*degs)[2] for degs in range(0, self.steps_per_rev)]
        min_z = min(zs_360 + [min_z])
        max_z = max(zs_360 + [max_z])
        mid_z = (min_z + max_z)/2
        original_dist = max_z - mid_z

        s = 0
        min_t1, max_t1 = 360, -360
        min_t2, max_t2 = 360, -360
        min_t3, max_t3 = 360, -360
        dist = original_dist * 0.5
        while original_dist > s and dist > 0.1:
            s += dist
            r = [self.get_angles((2*(i in [0,1,4,5])-1) * s, (2*(i in [0,1,3,4,7])-1) * s, mid_z + (2 * (i<4) - 1) * s) for i in range(8)]
            if any(None in v for v in r):
                s -= dist
                dist *= 0.5
            else:
                min_t1 = min([min_t1] + [v[0] for v in r])
                max_t1 = max([max_t1] + [v[0] for v in r])
                min_t2 = min([min_t1] + [v[1] for v in r])
                max_t2 = max([max_t1] + [v[1] for v in r])
                min_t3 = min([min_t1] + [v[2] for v in r])
                max_t3 = max([max_t1] + [v[2] for v in r])
        home = self.get_xyz(0, 0, 0)
        center = (0,0, mid_z)
        bounds = {
            'x': (-s, s),
            'y': (-s, s),
            'z': (mid_z - s, mid_z + s)
        }
        limits = {
            'theta1': (min_t1, max_t1),
            'theta2': (min_t2, max_t2),
            'theta3': (min_t3, max_t3),
        }
        r1_x, r1_y, r1_z = home
        r2_x, r2_y, r2_z = self.get_xyz(step_degs, 0, 0)
        x = r1_x - r2_x
        y = r1_y - r2_y
        res = (x ** 2 + y ** 2) ** 0.5
        info = {
            'home': home,
            'center': center,
            'bounds': bounds,
            'limits': limits,
            'resolution': res
        }
        return info



if __name__ == "__main__":
    from load_config import kinematics_config
    kc = KinematicsCalculator(**kinematics_config)
