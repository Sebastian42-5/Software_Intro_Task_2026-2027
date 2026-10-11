#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import math, sys, select, termios, tty
from std_msgs.msg import Float64MultiArray
from geometry_msgs.msg import Twist, TransformStamped
from nav_msgs.msg import Odometry
from tf2_ros import TransformBroadcaster
import os

JOINT_NAMES = ['shoulder_pitch', 'shoulder_yaw', 'elbow_pitch', 'elbow_roll', 'wrist_pitch', 'wrist_roll',
               'fr_swerve_yaw', 'fl_swerve_yaw', 'br_swerve_yaw', 'bl_swerve_yaw',
               'fr_wheel', 'fl_wheel', 'br_wheel', 'bl_wheel']

# every tuple of the arm keys represents index followed by direction

ARM_KEYS = {
    'q': (0, 1), 'a': (0, -1),   # shoulder_pitch
    'w': (1, 1), 's': (1, -1),   # shoulder_yaw
    'e': (2, 1), 'd': (2, -1),   # elbow_pitch
    'r': (3, 1), 'f': (3, -1),   # elbow_roll
    't': (4, 1), 'g': (4, -1),   # wrist_pitch
    '1': (5, 1), '2': (5, -1),   # wrist_roll
}

DRIVE_KEYS = {
    'i': (1, 0, 0), 'k': (-1, 0, 0), # moving forward and backward
    'j': (0, 1, 0), 'l': (0, -1, 0), # going left to right 
    'u': (0, 0, 1), 'o': (0, 0, -1) # rotation left to right
}

class KeybindController(Node):
    def __init__(self):
        super().__init__('keybind_controller')
        self.get_logger().info("Keybind Controller Node has been initialized.")

        self.declare_parameter('joint_topic', 'joint_commands')
        self.declare_parameter('joint_step', 0.1)        # rad per keypress
        self.declare_parameter('lin_speed', 0.5)         # m/s
        self.declare_parameter('ang_speed', 1.0)         # rad/s
        self.declare_parameter('hold_time', 0.3)         # s a drive key stays "held"
        self.declare_parameter('wheel_radius', 0.05)     # m  (set to your rover)
        self.declare_parameter('module_x', 0.2)          # m, half wheelbase
        self.declare_parameter('module_y', 0.2)          # m, half track width
        self.declare_parameter('publish_odom', True)
        self.declare_parameter('odom_frame', 'odom')
        self.declare_parameter('base_frame', 'base_link')

        self.declare_parameter('mode', 'gazebo')
        self.mode = self.get_parameter('mode').value
        self.wheel_vel = [0.0] * 4
        self.arm_pub = self.create_publisher(Float64MultiArray, '/arm_swerve_position_controller/commands', 10)
        self.wheel_pub = self.create_publisher(Float64MultiArray, '/wheel_velocity_controller/commands', 10)

        p = lambda n: self.get_parameter(n).value
        self.joint_step = p('joint_step')
        self.lin_speed = p('lin_speed')
        self.ang_speed = p('ang_speed')
        self.hold_time = p('hold_time')
        self.wheel_radius = p('wheel_radius')
        self.publish_odom = p('publish_odom')
        self.odom_frame = p('odom_frame')
        self.base_frame = p('base_frame')

        # module order matches JOINT_NAMES: fr, fl, br, bl  (x fwd, y left)
        # these module are used for the orientation of the wheels
        mx, my = p('module_x'), p('module_y')
        self.modules = [(mx, -my), (mx, my), (-mx, -my), (-mx, my)]

        self.joint_pub = self.create_publisher(JointState, p('joint_topic'), 10)
        self.cmd_vel_pub = self.create_publisher(Twist, 'cmd_vel', 10)
        self.odom_pub = self.create_publisher(Odometry, 'odom', 10)
        self.tf_broadcaster = TransformBroadcaster(self)

        self.positions = [0.0] * len(JOINT_NAMES)
        self.cmd = (0.0, 0.0, 0.0)             # vx, vy, wz
        self.x = self.y = self.yaw = 0.0       # dead-reckoned pose
        self.last_drive = self.get_clock().now()

        self.dt = 0.05
        self.create_timer(self.dt, self.update)
        print("""
            press q/a to control the shoulder pitch
            press w/s to control the shoulder yaw
            press e/d to control the elbow pitch
            press r/f to control the elbow roll
            press t/g to control the wrist pitch 
            press 1/2 to control the wrist roll

            press i/k to drive forward or backward
            press j/l to drive to the left or to the right 
            press u/o to rotate to the left or to the right
        """)


    def read_keys(self):
        keys = ''
        fd = sys.stdin.fileno()
        while select.select([fd], [], [], 0)[0]:
            keys += os.read(fd, 32).decode(errors = 'ignore')
        return keys

        
    def update(self):
        now = self.get_clock().now()

        for key in self.read_keys():
            if key in ARM_KEYS:
                i, direction =  ARM_KEYS[key]
                self.positions[i] += direction * self.joint_step
            elif key in DRIVE_KEYS:
                dx, dy, d_omega = DRIVE_KEYS[key]
                self.cmd = (dx * self.lin_speed, dy * self.lin_speed, d_omega * self.ang_speed)
                self.last_drive = now
            elif key == ' ':
                self.cmd = (0.0, 0.0, 0.0)

        # if a key gets pressed too briefly and there is no message sent 

        if (now - self.last_drive).nanoseconds * 1e-9 > self.hold_time:
            self.cmd = (0.0, 0.0, 0.0)

        # send transforms for linear or angular positions

        vx, vy, wz = self.cmd
        self.update_swerve_drive(vx, vy, wz)
        self.integrate_odom(vx, vy, wz)
        self.publish(now, vx, vy, wz)

    def update_swerve_drive(self, vx, vy, wz):
        '''rotation inverse kinematics logic and robot orientation'''
        for i, (mx, my) in enumerate(self.modules):
            vxi = vx - wz * my
            vyi = vy + wz * mx
            speed = math.hypot(vxi, vyi)
            if speed > 1e-3:                         # hold last angle when stopped
                self.positions[6 + i] = math.atan2(vyi, vxi)
            self.wheel_vel[i] = speed / self.wheel_radius     # restore this
            # this is to control the wheel linear velocity in rviz
            self.positions[10 + i] += self.wheel_vel[i] * self.dt 

    def integrate_odom(self, vx, vy, wz):
        self.x += (vx * math.cos(self.yaw) - vy * math.sin(self.yaw)) * self.dt
        self.y += (vx * math.sin(self.yaw) + vy * math.cos(self.yaw)) * self.dt
        self.yaw += wz * self.dt

    def publish(self, now, vx, vy, wz):
        if self.mode == 'gazebo':
                self.arm_pub.publish(Float64MultiArray(data=self.positions[:10]))
                self.wheel_pub.publish(Float64MultiArray(data=list(self.wheel_vel)))
        else:
            self.publish_rviz(now, vx, vy, wz)


    def publish_rviz(self, now, vx, vy, wz):
        stamp = now.to_msg()

        joint_state = JointState()
        joint_state.header.stamp = stamp
        joint_state.name = JOINT_NAMES
        joint_state.position = list(self.positions)
            
        # velocity commands

        twist = Twist()
        twist.linear.x, twist.linear.y, twist.angular.z = vx, vy, wz
        self.cmd_vel_pub.publish(twist)

        if not self.publish_odom:
            return

        # yaw to quaternion conversion for z rotation 

        qz, qw = math.sin(self.yaw / 2.0), math.cos(self.yaw / 2.0)

        # 3D spatial translation between parent and child link frame

        tf = TransformStamped()
        tf.header.stamp = stamp
        tf.header.frame_id = self.odom_frame
        tf.child_frame_id = self.base_frame
        tf.transform.translation.x = self.x
        tf.transform.translation.y = self.y
        tf.transform.rotation.z = qz
        tf.transform.rotation.w = qw
        self.tf_broadcaster.sendTransform(tf)

        # pose publisher topic

        odom = Odometry()
        odom.header.stamp = stamp
        odom.header.frame_id = self.odom_frame
        odom.child_frame_id = self.base_frame
        odom.pose.pose.position.x = self.x
        odom.pose.pose.position.y = self.y
        odom.pose.pose.orientation.z = qz
        odom.pose.pose.orientation.w = qw
        odom.twist.twist = twist
        self.odom_pub.publish(odom)

        self.joint_pub.publish(joint_state)

        

def main(args=None):
    rclpy.init(args=args)
    settings = termios.tcgetattr(sys.stdin)
    controller = KeybindController()
    
    try:
        tty.setcbreak(sys.stdin.fileno())
        rclpy.spin(controller)
    except KeyboardInterrupt:
        pass
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
        controller.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()



