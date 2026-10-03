#!/usr/bin/env python3

import rclpy 
from rclpy.node import Node
from geometry_msgs.msg import Twist

class LinearMovementController(Node):
    def __init__(self):
        super().__init__('linear_movement_node')
        self.publisher = self.create_publisher(Twist, 'cmd_vel', 10)
        self.create_timer(0.1, self.timer_callback)

    def move_forward(self, speed):
        msg = Twist()
        msg.linear.x = speed
        self.publisher.publish(msg)
        self.get_logger().info(f"Published Twist message: linear.x={msg.linear.x}")

    def turn(self, angular_speed):
        msg = Twist()
        msg.angular.z = angular_speed
        self.publisher.publish(msg)
        self.get_logger().info(f"Published Twist message: angular.z={msg.angular.z}")

    def timer_callback(self):
        msg = Twist()

        msg.linear.x = 0.5  # Move forward at 0.5 m/s
        msg.linear.y = 0.0  # No lateral movement
        msg.linear.z = 0.0  # No vertical movement

        msg.angular.x = 0.0  # No rotation around x-axis
        msg.angular.y = 0.0  # No rotation around y-axis
        msg.angular.z = 0.0  # No rotation
        self.publisher.publish(msg)
        self.get_logger().info(f"Published Twist message: linear.x={msg.linear.x}, linear.y={msg.linear.y}, linear.z={msg.linear.z}, angular.x={msg.angular.x}, angular.y={msg.angular.y}, angular.z={msg.angular.z}")


def main(args=None):
    rclpy.init(args=args)
    node = LinearMovementController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
