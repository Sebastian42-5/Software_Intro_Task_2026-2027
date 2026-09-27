from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='intro_rover_description',
            executable='intro_rover_node',
            name='intro_rover_node',
            output='screen',
            parameters=[{'param_name': 'param_value'}]
        )
    ])

