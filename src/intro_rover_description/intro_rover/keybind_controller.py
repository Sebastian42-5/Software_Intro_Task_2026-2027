#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import math, sys, select, termios, tty
from std_msgs.msg import Float64MultiArray
from geometry_msgs.msg import Twist, TransformStamped
from nav_msgs.msg import Odometry
from tf2_ros import TransformBroadcaster

JOINT_NAMES = ['shoulder_pitch', 'shoulder_yaw', 'elbow_pitch', 'elbow_roll', 'wrist_pitch', 'wrist_roll',
               'fr_swerve_yaw', 'fl_swerve_yaw', 'br_swerve_yaw', 'bl_swerve_yaw',
               'fr_wheel', 'fl_wheel', 'br_wheel', 'bl_wheel']

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
        print(HELP)


    def timer_callback(self, increment=0.1):
        self.joint_position += increment
        self.joint_state.header.stamp = self.get_clock().now().to_msg()
        joint_positions = [0.5 * math.sin(self.t), 0.5 * math.cos(self.t), 0.5 * math.sin(self.t), 0.5 * math.cos(self.t), 0.5 * math.sin(self.t), 0.5 * math.cos(self.t), 0.5 * math.sin(self.t), 0.5 * math.cos(self.t), 0.5 * math.sin(self.t), 0.5 * math.cos(self.t), 0.5 * math.sin(self.t), 0.5 * math.cos(self.t), 0.5 * math.sin(self.t), 0.5 * math.cos(self.t)]
        self.publish_joint_commands(self.joint_state.name, joint_positions)
        self.t += increment

    def publish_joint_commands(self, joint_names, joint_positions):
        msg = JointState()
        msg.name = joint_names
        msg.position = joint_positions
        self.publisher.publish(msg)
        self.get_logger().info(f"Published JointState message: {msg}")

    def get_key(settings):
        tty.setraw(sys.stdin.fileno())
        rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
        if rlist:
            key = sys.stdin.read(1)
        else:
            key = ''
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, termios.tcgetattr(sys.stdin))
        return key

    def run(self, args=None):
        settings = termios.tcgetattr(sys.stdin)
        rclpy.init(args=args)
        node = KeybindController()

        try:
            while True:
                key = node.get_key(settings)

                if key == 'q':
                    self.positions[0] += 0.1  # Increase shoulder_pitch
                elif key == 'a':
                    self.positions[0] -= 0.1  # Decrease shoulder_pitch

                elif key == 'w':
                    self.positions[1] += 0.1  # Increase shoulder_yaw
                elif key == 's':
                    self.positions[1] -= 0.1  # Decrease shoulder_yaw

                elif key == 'e':
                    self.positions[2] += 0.1  # Increase elbow_pitch
                elif key == 'd':
                    self.positions[2] -= 0.1  # Decrease elbow_pitch

                elif key == 'r':
                    self.positions[3] += 0.1  # Increase elbow_roll
                elif key == 'f':
                    self.positions[3] -= 0.1  # Decrease elbow_roll

                elif key == 't':
                    self.positions[4] += 0.1  # Increase wrist_pitch
                elif key == 'g':
                    self.positions[4] -= 0.1  # Decrease wrist_pitch

                elif key == '1':
                    self.positions[5] += 0.1  # Increase wrist_roll
                elif key == '2':
                    self.positions[5] -= 0.1  # Decrease wrist_roll

                elif key == '3':
                    self.positions[6] += 0.1  # Increase fr_swerve_yaw
                elif key == '4':
                    self.positions[6] -= 0.1  # Decrease fr_swerve_yaw

                elif key == '5':
                    self.positions[7] += 0.1  # Increase fl_swerve_yaw
                elif key == '6':
                    self.positions[7] -= 0.1  # Decrease fl_swerve_yaw

                elif key == '7':
                    self.positions[8] += 0.1  # Increase br_swerve_yaw
                elif key == '8':
                    self.positions[8] -= 0.1  # Decrease br_swerve_yaw

                elif key == '9':
                    self.positions[9] += 0.1  # Increase bl_swerve_yaw
                elif key == '0':
                    self.positions[9] -= 0.1  # Decrease bl_swerve_yaw

                elif key == '\x03':  # Ctrl+C
                    break

        except KeyboardInterrupt:
            pass
        finally:
            node.destroy_node()
            rclpy.shutdown()
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)


def main(args=None):
    controller = KeybindController()
    controller.run(args=args)

if __name__ == '__main__':
    main()


