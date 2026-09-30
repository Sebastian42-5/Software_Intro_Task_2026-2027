import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import math 


class JointController(Node):
    def __init__(self):
        self.angle = 0.0
        super().__init__('joint_controller')
        self.get_logger().info("Joint Controller Node has been initialized.")

        self.publisher = self.create_publisher(JointState, 'joint_states', 10)

    def move_joints(self, joint_name, joint_position):
        msg = JointState()
        msg.name = joint_name
        msg.position = joint_position
        self.publisher.publish(msg)
        msg.header.stamp = self.get_clock().now().to_msg()


        self.angle += 0.04
        joint_positions = [joint_position + 0.1 * math.sin(self.angle) for joint_position in msg.position]    

        msg.velocity = []
        msg.effort = []

        self.publisher.publish(msg)
        
        

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

        