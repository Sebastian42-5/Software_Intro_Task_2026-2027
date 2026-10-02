#!/usr/bin/env python3

import math
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile
from geometry_msgs.msg import Quaternion, Twist, TransformStamped
from sensor_msgs.msg import JointState
from tf2_ros import TransformBroadcaster


# This is the node that will make the rover dance

class StatePublisherNode(Node):
    def __init__(self):
        super().__init__('state_publisher_node')

        qos_profile = QoSProfile(depth=10)
        self.joint_state_publisher = self.create_publisher(JointState, 'joint_states', qos_profile)
        self.transform_broadcaster = TransformBroadcaster(self)
        self.nodeName = self.get_name()
        self.get_logger().info(f"{self.nodeName} has been initialized.")

        self.degree = math.pi / 180.0
        self.create_timer(0.1, self.timer_callback)


    def timer_callback(self):
        now = self.get_clock().now().to_msg()
        joint_state = JointState()
        joint_state.header.stamp = now
        joint_state.name = ['shoulder_pitch', 'shoulder_yaw', 'elbow_pitch', 'elbow_roll', 'wrist_pitch', 'wrist_roll',
                            'fr_swerve_yaw', 'fl_swerve_yaw', 'br_swerve_yaw', 'bl_swerve_yaw']
        joint_state.position = [math.sin(self.degree)] * len(joint_state.name)
        self.joint_state_publisher.publish(joint_state)

        odom_transform = TransformStamped()
        odom_transform.header.stamp = now
        odom_transform.header.frame_id = 'odom'
        odom_transform.child_frame_id = 'base_link'

        # translation and rotation of the robot in the odom frame
        odom_transform.transform.translation.x = math.cos(self.degree) * 2.0
        odom_transform.transform.translation.y = math.sin(self.degree) * 2.0
        odom_transform.transform.translation.z = 0.0

        odom_transform.transform.rotation.x = 0.0
        odom_transform.transform.rotation.y = 0.0
        odom_transform.transform.rotation.z = math.sin(self.degree / 2.0)
        odom_transform.transform.rotation.w = math.cos(self.degree / 2.0)

        self.transform_broadcaster.sendTransform(odom_transform)

        self.degree += 1.0


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

