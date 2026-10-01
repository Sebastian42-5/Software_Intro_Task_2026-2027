from ament_index_python import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration
import os

def generate_launch_description():

    use_sim_time = LaunchConfiguration('use_sim_time', default='false')
    urdf_file_name = 'intro_rover_description.urdf'

    urdf = os.path.join(
        get_package_share_directory('intro_rover_description'),
        'urdf',
        urdf_file_name)
    
    return LaunchDescription([
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{'use_sim_time': use_sim_time}, {'robot_description': open(urdf).read()}]
        ),
        Node(
            package='intro_rover_description',
            executable='state_publisher.py',
            name='state_publisher_node',
            output='screen',
            parameters=[{'param_name': 'param_value'}, {'use_sim_time': use_sim_time}]
        ), 
        Node(
            package='intro_rover_description',
            executable='joint_controller.py',
            name='joint_controller',
            output='screen',
            parameters=[{'use_sim_time': use_sim_time}]
        ), 
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=['-d', os.path.join(get_package_share_directory('intro_rover_description'), 'config', 'intro_rover.rviz')],
            parameters=[{'use_sim_time': use_sim_time}]
        )
    ])

