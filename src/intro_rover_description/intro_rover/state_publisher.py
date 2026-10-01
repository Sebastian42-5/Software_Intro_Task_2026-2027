#!/usr/bin/env python3

from math import pi, cos, sin
from intro_rover_description.intro_rover.joint_controller import JointController
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile
from geometry_msgs.msg import Quarternion, Twist
from sensor_msgs.msg import JointState
from tf2_ros import TransformBroadcaster

from joint_controller import JointController

# This is the node that will make the rover dance

class StatePublisherNode(Node):
    def __init__(self):
        super().__init__('state_publisher_node')

        qos_profile = QoSProfile(depth=10)
        self.joint_state_publisher = self.create_publisher(JointState, 'joint_states', qos_profile)
        self.transform_broadcaster = TransformBroadcaster(self, qos_profile=qos_profile)
        self.nodeName = self.get_name()
        self.get_logger().info(f"{self.nodeName} has been initialized.")

        self.degree = pi / 180.0
        self.loop_rate = self.create_timer(0.1, self.timer_callback)

        # initial robot state 

        tilt = 0.0
        tilt_increment = 0.5 * self.degree
        swivel = 0.0
        angle = 0.0
        height = 0.0
        height_increment = 0.005

        def timer_callback(self):
            now = self.get_clock().now().to_msg()
            joint_state = JointState()
            joint_state.header.stamp = now
            joint_state.name = ['tilt_joint', 'swivel_joint', 'height_joint']



def main(args=None):
    rclpy.init(args=args)
    node = StatePublisherNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

