import numpy as np
import pydart2 as pydart
import bvh
import math

class MyWorld(pydart.World):

    def eulerToRotationMatrix(self, z, x, y, isdeg=True):
        rad_z, rad_x, rad_y = z, x, y
        if isdeg:
            rad_z = z * math.pi/180.
            rad_x = x * math.pi/180.
            rad_y = y * math.pi/180.

        c1 = math.cos(rad_z)
        s1 = math.sin(rad_z)
        c2 = math.cos(rad_x)
        s2 = math.sin(rad_x)
        c3 = math.cos(rad_y)
        s3 = math.sin(rad_y)

        mat = np.zeros((3, 3))
        mat[0, 0] = c1*c3 - s1 * s2 * s3
        mat[0, 1] = -c2 * s1
        mat[0, 2] = c1*s3 + c3 * s1 * s2
        mat[1, 0] = c3*s1 + c1 * s2 * s3
        mat[1, 1] = c1 * c2
        mat[1, 2] = s1 * s3 - c1*c3*s2
        mat[2, 0] = -c2 * s3
        mat[2, 1] = s2
        mat[2, 2] = c2*c3

        return mat

    def rotationMatrixToAxisAngles(self, R):
        temp_r = np.array([R[2,1]-R[1,2], R[0,2]-R[2,0], R[1,0]-R[0,1]])
        angle = math.acos((R[0, 0]+R[1, 1]+R[2, 2] - 1)/2.)
        temp_r_norm = np.linalg.norm(temp_r)
        if temp_r_norm < 0.000001:
            return np.zeros(3)
        return temp_r/temp_r_norm * angle

    # def euler2axis_angle(self, roll, pitch, yaw):
    #
    #     bank = roll * math.pi/180.
    #     attitude = pitch * math.pi/180.
    #     heading = yaw * math.pi/180.
    #
    #     #   Assuming the angles are in radians.
    #
    #     c1 = math.cos(heading/2)
    #     s1 = math.sin(heading/2)
    #     c2 = math.cos(attitude/2)
    #     s2 = math.sin(attitude/2)
    #     c3 = math.cos(bank/2)
    #     s3 = math.sin(bank/2)
    #     c1c2 = c1*c2
    #     s1s2 = s1*s2
    #     w =c1c2*c3 - s1s2*s3
    #     x =c1c2*s3 + s1s2*c3
    #     y =s1*c2*c3 + c1*s2*s3
    #     z =c1*s2*c3 - s1*c2*s3
    #     angle = 2 * math.acos(w)
    #     norm = x*x+y*y+z*z
    #
    #     if norm < 0.001:  # when all euler angles are zero angle =0 so
    #         #we can set axis to anything to avoid divide by zero
    #         x=1
    #         y=0
    #         z=0
    #     else:
    #         norm = math.sqrt(norm)
    #         x = x/norm
    #         y = y/norm
    #         z = z/norm
    #
    #     out_angle = angle * 180./math.pi
    #
    #     axis = np.array([x, y, z])
    #     return out_angle, axis

    def __init__(self, ):
        pydart.World.__init__(self, 1.0 / 1000.0, './data/skel/cart_pole_blade_zxy.skel')
        bvh_file = open('./data/mocap/local_dance1.bvh', "r")
        bvh_data = bvh_file.read()
        mybvh = bvh.Bvh(bvh_data)

        # print("bvh frame time : ", mybvh.frame_time)
        # print(mybvh.get_joints())
        # print(mybvh.get_joints_names())
        # print(mybvh.frame_joint_channel(1, 'root', 'Xposition'))
        # print(mybvh.joint_channels('root'))
        # print(mybvh.frame_joint_channels(0, 'root', ['Xposition', 'Yposition', 'Zposition', 'Zrotation', 'Xrotation', 'Yrotation']))
        # print(mybvh.frame_joint_channels(0, 'root', mybvh.joint_channels('root')))

        # print("frame num : ", mybvh.nframes)

        self.bvh_fn = mybvh.nframes
        # self.bvh_fn = 300
        # print("End frame:", self.bvh_fn)
        bvh_joint_list = mybvh.get_joints_names()
        self.bvh_motion_list = []

        for i in range(self.bvh_fn):
            motion_q = []
            for j in bvh_joint_list:
                x = mybvh.frame_joint_channel(i, j, 'Xrotation')
                y = mybvh.frame_joint_channel(i, j, 'Yrotation')
                z = mybvh.frame_joint_channel(i, j, 'Zrotation')
                rm = self.eulerToRotationMatrix(z, x, y)
                axis_v = self.rotationMatrixToAxisAngles(rm)
                if j == 'root':
                    motion_q.append(axis_v[0])
                    motion_q.append(axis_v[1])
                    motion_q.append(axis_v[2])

                    motion_q.append(mybvh.frame_joint_channel(i, j, 'Xposition')/100)
                    motion_q.append(mybvh.frame_joint_channel(i, j, 'Yposition')/100-0.92)
                    motion_q.append(mybvh.frame_joint_channel(i, j, 'Zposition')/100)
                elif j == 'lfemur':
                    motion_q.append(axis_v[0])
                    motion_q.append(axis_v[1])
                    motion_q.append(axis_v[2])
                elif j == 'ltibia':
                    # motion_q.append(z * math.pi / 180.)
                    # motion_q.append(x* math.pi / 180.)
                    motion_q.append(y* math.pi / 180.)
                elif j == 'lfoot':
                    motion_q.append(axis_v[0])
                    motion_q.append(axis_v[1])
                    motion_q.append(axis_v[2])
                elif j == 'rfemur':
                    motion_q.append(axis_v[0])
                    motion_q.append(axis_v[1])
                    motion_q.append(axis_v[2])
                elif j == 'rtibia':
                    # motion_q.append(z* math.pi / 180.)
                    # motion_q.append(x* math.pi / 180.)
                    motion_q.append(y* math.pi / 180.)
                elif j == 'rfoot':
                    motion_q.append(axis_v[0])
                    motion_q.append(axis_v[1])
                    motion_q.append(axis_v[2])
                elif j == 'lowerback':
                    motion_q.append(axis_v[0])
                    motion_q.append(axis_v[1])
                    motion_q.append(axis_v[2])
                elif j == 'upperback':
                    motion_q.append(z* math.pi / 180.)
                    # motion_q.append(x* math.pi / 180.)
                    # motion_q.append(y* math.pi / 180.)
                elif j == 'head':
                    motion_q.append(axis_v[0])
                    motion_q.append(axis_v[1])
                    motion_q.append(axis_v[2])
                elif j == 'lclavicle':
                    motion_q.append(z* math.pi / 180.)
                    # motion_q.append(x* math.pi / 180.)
                    # motion_q.append(y* math.pi / 180.)
                elif j == 'lhumerus':
                    motion_q.append(axis_v[0])
                    motion_q.append(axis_v[1])
                    motion_q.append(axis_v[2])
                elif j == 'lradius':
                    motion_q.append(z* math.pi / 180.)
                    # motion_q.append(x* math.pi / 180.)
                    # motion_q.append(y* math.pi / 180.)
                elif j == 'lwrist':
                    # motion_q.append(z* math.pi / 180.)
                    motion_q.append(x* math.pi / 180.)
                    # motion_q.append(y* math.pi / 180.)
                elif j == 'rclavicle':
                    motion_q.append(z* math.pi / 180.)
                    # motion_q.append(x* math.pi / 180.)
                    # motion_q.append(y* math.pi / 180.)
                elif j == 'rhumerus':
                    motion_q.append(axis_v[0])
                    motion_q.append(axis_v[1])
                    motion_q.append(axis_v[2])
                elif j == 'rradius':
                    motion_q.append(z * math.pi / 180.)
                    # motion_q.append(x * math.pi / 180.)
                    # motion_q.append(y * math.pi / 180.)
                elif j == 'rwrist':
                    # motion_q.append(z * math.pi / 180.)
                    motion_q.append(x * math.pi / 180.)
                    # motion_q.append(y* math.pi / 180.)

            # degree 2 radian
            # for ii in range(len(motion_q)):
            #     motion_q[ii] = motion_q[ii] * math.pi / 180.
            # print("q: ", motion_q)

            self.bvh_motion_list.append(motion_q)

        print('bvh file load successfully')

        self.skeletons[3].set_positions(self.bvh_motion_list[0])
        print(self.skeletons[3].num_dofs())
        print(len(self.bvh_motion_list[0]))
        self.fn_bvh = 0

        self.duration = mybvh.frame_time
        print("duration: ", self.duration)
        self.elapsedTime = 0.0

    def step(self):
        # print(self.time())

        if self.time() > 9.0:
            self.skeletons[3].set_positions(self.bvh_motion_list[self.fn_bvh])
        elif self.time() - self.elapsedTime > self.duration:
        # if self.fn_bvh < self.bvh_fn:
            self.elapsedTime = self.time()
            self.fn_bvh = self.fn_bvh + 1
            print("frame num: ", self.fn_bvh)
            # self.skeletons[3].set_positions(self.curr_state.angles)
            self.skeletons[3].set_positions(self.bvh_motion_list[self.fn_bvh])

        super(MyWorld, self).step()



if __name__ == '__main__':
    print('Example: Skating -- pushing side to side')

    pydart.init()
    print('pydart initialization OK')

    world = MyWorld()
    print('MyWorld  OK')

    # print('[Joint]')
    # for joint in skel.joints:
    #     print("\t" + str(joint))
    #     print("\t\tparent = " + str(joint.parent_bodynode))
    #     print("\t\tchild = " + str(joint.child_bodynode))
    #     print("\t\tdofs = " + str(joint.dofs))

    pydart.gui.viewer.launch_pyqt5(world)