import os
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import Command, FindExecutable
from launch.actions import ExecuteProcess, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution, LaunchConfiguration
from launch_ros.parameter_descriptions import ParameterValue
from launch.actions import AppendEnvironmentVariable
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():

    set_gz_ressource_path = AppendEnvironmentVariable('GZ_SIM_RESOURCE_PATH', os.path.dirname(get_package_share_directory('intro_rover_description')))

    gazebo_launch = IncludeLaunchDescription(
    PythonLaunchDescriptionSource([
        PathJoinSubstitution([FindPackageShare('ros_gz_sim'), 'launch', 'gz_sim.launch.py'])
    ]),
    launch_arguments={
        'gz_args': '-r empty.sdf'
    }.items()
    )      

    robot_description = ParameterValue(
        Command([
            PathJoinSubstitution([FindExecutable(name='xacro')]),
            ' ',
            PathJoinSubstitution([FindPackageShare('intro_rover_description'), 'urdf', 'intro_rover_description.urdf']),
            ' use_sim_time:=true'
        ]),
        value_type=str
    )

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description, 'use_sim_time': True}]
    )

    robot_spawn_node = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description', '-name', 'intro_rover'],
        output='screen'
    )

    load_joint_state_publisher_node = Node(
        package='intro_rover_description',
        executable='state_publisher.py',
        name='state_publisher_node',
        output='screen'
    )

    bridge = Node(
    package='ros_gz_bridge',
    executable='parameter_bridge',
    arguments=[
        '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
        '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
        '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
        '/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
        '/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model',
    ],
    output='screen'
)

    return LaunchDescription([
        set_gz_ressource_path,
        gazebo_launch,
        robot_state_publisher_node,
        robot_spawn_node,
        bridge,
        load_joint_state_publisher_node
    ])

