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

        # this is where commands from the joint controller will be received

        self.joint_command_subscriber = self.create_subscription(JointState, 'joint_commands', self.joint_command_callback, qos_profile)  
        self.linear_movement_subscriber = self.create_subscription(Twist, 'cmd_vel', self.linear_movement_callback, qos_profile)  

        self.join_positions = { name: 0.0 for name in ['shoulder_pitch', 'shoulder_yaw', 'elbow_pitch', 'elbow_roll', 'wrist_pitch', 'wrist_roll',
                    'fr_swerve_yaw', 'fl_swerve_yaw', 'br_swerve_yaw', 'bl_swerve_yaw']}

        self.create_timer(0.1, self.timer_callback)
        self.get_logger().info(f"{self.nodeName} has been initialized.")


    def joint_command_callback(self, msg):
        for name, position in zip(msg.name, msg.position):
            if name in self.join_positions:
                self.join_positions[name] = position
            else:
                self.get_logger().warn(f"Received command for unknown joint: {name}", throttle_duration_sec=1.0)

    def linear_movement_callback(self, msg):
        # Here you can implement how the linear movement commands affect the robot's state
        self.get_logger().info(f"Received linear movement command: linear.x={msg.linear.x}, angular.z={msg.angular.z}")


    def timer_callback(self):
        now = self.get_clock().now().to_msg()
        joint_state = JointState()
        joint_state.header.stamp = now
        joint_state.name = list(self.join_positions.keys())
        joint_state.position = list(self.join_positions.values())
        self.joint_state_publisher.publish(joint_state)

        odom_transform = TransformStamped()
        odom_transform.header.stamp = now
        odom_transform.header.frame_id = 'odom'
        odom_transform.child_frame_id = 'base_link'

        # translation and rotation of the robot in the odom frame
        for joint_name, joint_position in self.join_positions.items():
            if 'shoulder' in joint_name or 'elbow' in joint_name or 'wrist' in joint_name:
                odom_transform.transform.rotation = Quaternion(x=0.0, y=0.0, z=math.sin(joint_position / 2), w=math.cos(joint_position / 2))
            elif 'swerve' in joint_name:
                odom_transform.transform.translation.x = 0.5 * math.sin(joint_position)
                odom_transform.transform.translation.y = 0.5 * math.cos(joint_position)
                odom_transform.transform.translation.z = 0.0
                break

        self.transform_broadcaster.sendTransform(odom_transform)


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

