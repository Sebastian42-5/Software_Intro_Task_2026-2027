#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import math 


class JointController(Node):
    def __init__(self):
        self.angle = 0.0
        super().__init__('joint_controller')
        self.get_logger().info("Joint Controller Node has been initialized.")
        self.publisher = self.create_publisher(JointState, 'joint_commands', 10)
        self.t = 0.0
        self.create_timer(0.1, self.timer_callback)

    def timer_callback(self):
        joint_names = ['shoulder_pitch', 'shoulder_yaw', 'elbow_pitch', 'elbow_roll', 'wrist_pitch', 'wrist_roll', 'fr_swerve_yaw', 'fl_swerve_yaw', 'br_swerve_yaw', 'bl_swerve_yaw']
        joint_positions = [0.5 * math.sin(self.t), 0.5 * math.cos(self.t), 0.5 * math.sin(self.t), 0.5 * math.cos(self.t), 0.5 * math.sin(self.t), 0.5 * math.cos(self.t), 0.5 * math.sin(self.t), 0.5 * math.cos(self.t), 0.5 * math.sin(self.t), 0.5 * math.cos(self.t)]
        self.move_joints(joint_names, joint_positions)
        self.t += 0.1

    def move_joints(self, joint_name, joint_position):
        msg = JointState()
        msg.name = joint_name
        msg.position = joint_position
        self.publisher.publish(msg)
        msg.header.stamp = self.get_clock().now().to_msg()


def main(args=None):
    rclpy.init(args=args)
    node = JointController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()

        