from math import pi, cos, sin
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile
from geometry_msgs.msg import Quarternion, Twist
from sensor_msgs.msg import JointState
from tf2_ros import TransformBroadcaster

class StatePublisherNode(Node):
    def __init__(self):
        super().__init__('state_publisher_node')

        qos_profile = QoSProfile(depth=10)
        self.joint_state_publisher = self.create_publisher(JointState, 'joint_states', qos_profile)
        self.transform_broadcaster = TransformBroadcaster(self, qos_profile=qos_profile)
        self.nodeName = self.get_name()
        self.get_logger().info(f"{self.nodeName} has been initialized.")

        degree = pi / 180.0

        # initial robot state 

        tilt = 0.0
        tilt_increment = 0.5 * degree
        swivel = 0.0
        angle = 0.0
        height = 0.0
        height_increment = 0.005


