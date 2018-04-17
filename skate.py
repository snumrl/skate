# Copyright (c) 2015, Disney Research
# All rights reserved.
#
# Author(s): Sehoon Ha <sehoon.ha@disneyresearch.com>
# Disney Research Robotics Group
import pydart2 as pydart
import numpy as np
import control as ctrl



class Controller(object):
    def __init__(self, skel, h):
        self.h = h
        self.skel = skel
        ndofs = self.skel.ndofs
        self.qhat = self.skel.q
        self.Kp = np.diagflat([0.0] * 6 + [400.0] * (ndofs - 6))
        self.Kd = np.diagflat([0.0] * 6 + [40.0] * (ndofs - 6))
        self.preoffset = 0.0

    def compute(self):
        skel = self.skel



        #outputs of update functions
        #: dot(x) = Ax + Bu
        # self.A = np.matrix(dim*2, dim*2)
        # self.B = np.matrix(dim*2, cdim)
        # self.A:range(0, dim, 0, dim*2):set(0)
        # self.A:range(0, dim, dim, dim * 2):diag():set(0)
        # self.B:range[0, dim, 0, cdim]:set(0)
        #
        #
        #
        # self.K, self.S, self.E = ctrl.lqr(self.A, self.B, self.Q, self.R)



        # Algorithm:
        # Stable Proportional-Derivative Controllers.
        # Jie Tan, Karen Liu, Greg Turk
        # IEEE Computer Graphics and Applications, 31(4), 2011.

        invM = np.linalg.inv(skel.M + self.Kd * self.h)
        p = -self.Kp.dot(skel.q + skel.dq * self.h - self.qhat)
        d = -self.Kd.dot(skel.dq)
        qddot = invM.dot(-skel.c + p + d + skel.constraint_forces())
        tau = p + d - self.Kd.dot(qddot) * self.h

        # Check the balance
        COP = skel.body('h_heel_left').to_world([0.05, 0, 0])
        offset = skel.C[0] - COP[0] + 0.03
        preoffset = self.preoffset

        # Adjust the target pose -- translated from bipedStand app of DART
        foot = skel.dof_indices(["j_heel_left_1", "j_toe_left",
                                 "j_heel_right_1", "j_toe_right"])
        # if 0.0 < offset < 0.1:
        #     k1, k2, kd = 200.0, 100.0, 10.0
        #     k = np.array([-k1, -k2, -k1, -k2])
        #     tau[foot] += k * offset + kd * (preoffset - offset) * np.ones(4)
        #     self.preoffset = offset
        # elif -0.2 < offset < -0.05:
        #     k1, k2, kd = 2000.0, 100.0, 100.0
        #     k = np.array([-k1, -k2, -k1, -k2])
        #     tau[foot] += k * offset + kd * (preoffset - offset) * np.ones(4)
        #     self.preoffset = offset

        # # High-stiffness
        # k1, k2, kd = 200.0, 10.0, 10.0
        # k = np.array([-k1, -k2, -k1, -k2])
        # tau[foot] += k * offset + kd * (preoffset - offset) * np.ones(4)
        # print("offset = %s" % offset)
        # self.preoffset = offset

        # Low-stiffness
        k1, k2, kd = 20.0, 1.0, 10.0
        k = np.array([-k1, -k2, -k1, -k2])
        tau[foot] += k * offset + kd * (preoffset - offset) * np.ones(4)
        if offset > 0.03:
            tau[foot] += 0.3 * np.array([-100.0, -50.0, -100.0, -50.0])
            print("Discrete A")
        if offset < -0.02:
            tau[foot] += -1.0 * np.array([-100.0, 0.0, -100.0, 0.0])
            print("Discrete B")
        # print("offset = %s" % offset)
        self.preoffset = offset

        # Make sure the first six are zero
        tau[:6] = 0
        return tau


class MyWorld(pydart.World):
    def __init__(self, ):
        """
        """
        pydart.World.__init__(self, 1.0 / 2000.0, './data/skel/fullbody1.skel')
        self.force = None
        self.duration = 0
        # self.skeletons[0].body('ground').set_friction_coeff(0.02)

    def step(self, ):
        if self.force is not None and self.duration >= 0:
            self.duration -= 1
            self.skeletons[1].body('h_spine').add_ext_force(self.force)
        super(MyWorld, self).step()

    def on_key_press(self, key):
        if key == '1':
            self.force = np.array([50.0, 0.0, 0.0])
            self.duration = 100
            print('push backward: f = %s' % self.force)
        elif key == '2':
            self.force = np.array([-50.0, 0.0, 0.0])
            self.duration = 100
            print('push backward: f = %s' % self.force)

    def render_with_ri(self, ri):
        if self.force is not None and self.duration >= 0:
            p0 = self.skeletons[1].body('h_spine').C
            p1 = p0 + 0.01 * self.force
            ri.set_color(1.0, 0.0, 0.0)
            ri.render_arrow(p0, p1, r_base=0.05, head_width=0.1, head_len=0.1)


if __name__ == '__main__':
    print('Example: bipedStand')

    pydart.init()
    print('pydart initialization OK')

    world = MyWorld()
    print('MyWorld  OK')

    # Use SkelVector to configure the initial pose
    skel = world.skeletons[1]
    q = skel.q
    q["j_pelvis_pos_y"] = -0.05
    q["j_pelvis_rot_y"] = -0.2
    q["j_thigh_left_z", "j_shin_left", "j_heel_left_1"] = 0.15, -0.4, 0.25
    q["j_thigh_right_z", "j_shin_right", "j_heel_right_1"] = 0.15, -0.4, 0.25
    q["j_abdomen_2"] = 0.0
    skel.set_positions(q)
    print('skeleton position OK')

    # m0 =1
    # m1 = 30
    # m2 = 30
    # l1 = 0.8
    # l2 = 0.8
    # I1 = 7
    # I2 = 7
    # b = 0
    #
    # mPendulum = DIPCview(m0, m1, m2, l1, l2, I1, I2, dt, 300)
    # mPendulum.oneStep()
    #mPendulum.draw()

    # Initialize the controller
    skel.set_controller(Controller(skel, world.dt))
    print('create controller OK')

    print("'1'--'2': programmed interaction")
    print("    '1': push forward")
    print("    '2': push backward")


    pydart.gui.viewer.launch_pyqt5(world)