#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import math, sys, select, termios, tty

class KeybindController(Node):
    def __init__(self):
        super().__init__('keybind_controller')
        self.get_logger().info("Keybind Controller Node has been initialized.")
        self.publisher = self.create_publisher(JointState, 'joint_commands', 10)
        self.t = 0.0
        self.positions = [0.0] * 14
        self.create_timer(0.1, self.timer_callback)
        self.joint_state = JointState()
        self.joint_state.name = ['shoulder_pitch', 'shoulder_yaw', 'elbow_pitch', 'elbow_roll', 'wrist_pitch', 'wrist_roll', 'fr_swerve_yaw', 'fl_swerve_yaw', 'br_swerve_yaw', 'bl_swerve_yaw', 'fr_wheel', 'fl_wheel', 'br_wheel', 'bl_wheel']    

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


