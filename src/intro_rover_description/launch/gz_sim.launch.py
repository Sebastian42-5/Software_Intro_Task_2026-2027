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
from launch.actions import AppendEnvironmentVariable, RegisterEventHandler
from launch.event_handlers import OnProcessExit
from ament_index_python.packages import get_package_share_directory
from launch.actions import RegisterEventHandler, TimerAction
from launch.event_handlers import OnProcessExit

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

    delayed_spawn = TimerAction(period=5.0, actions=[robot_spawn_node])

    spawners = [
    Node(package='controller_manager', executable='spawner',
         arguments=[name, '--controller-manager', '/controller_manager'])
    for name in ['joint_state_broadcaster',
                 'arm_swerve_position_controller',
                 'wheel_velocity_controller']
]

    spawn_controllers = RegisterEventHandler(
        OnProcessExit(target_action=robot_spawn_node, on_exit=spawners)
    )

    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/model/intro_rover/odometry@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            '/model/intro_rover/pose@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
        ],
        remappings=[
            ('/model/intro_rover/odometry', '/odom'),
            ('/model/intro_rover/pose', '/tf'),
        ],
        output='screen'
    )

    return LaunchDescription([
        set_gz_ressource_path,
        gazebo_launch,
        robot_state_publisher_node,
        robot_spawn_node,
        spawn_controllers,
        bridge,
    ])

