# Repository Description
This is the intro task repository to be forked by new potential software members who are interested in contributing to the software of the Robotics division of Space Concordia.\
The instructions of the software introduction task can be found in this README.md below.\
This repository contains a ROS2 workspace where packages can be added inside of the /src folder.\
Keep in mind that the URDF is very detailed and might need to be modified in order to reduce detail.\
Remember to go over documentation.

## 1. Creating a local repository  (DONE)
1.1. Make sure that your GitHub account is connected to your computer.\
1.2. Fork this repository into your GitHub account.\
1.3. Clone your fork of this repository onto your personal machine.

## 2. Fix the intro_rover_description ROS2 package
2.1. Apply the changes necessary to the files of the package in order to get it to work properly within ROS2.\

## 3. Visualize the robot in RViz
3.1. Create a launch file to visualize the rover in the RViz software.

## 4. Create a Ros2 infrastructure to control the rover in RViz
4.1. Create a node to manually control each joint of the rover.\
4.2. Create a node to make the rover dance. This should be a reprogrammed sequence or a function of the joint states over time.

## 5. Simulate the robot in Gazebo Harmonic
5.1. Create a launch file that spawns the rover in a Gazebo world. Please make sure to use Gazebo Harmonic as this version of Gazebo works better with ROS2 Jazzy.\
5.2. Control the rover with the control infrastructure built in part 4. and see it move in the Gazebo world.

## 6. Be ready to present your solution
6.1. Modify this README.md file in your forked workspace presenting your solutions.\
6.2. Run and present your workspace to the Software Manager.



Name: Sebastian Andres Soto Sandrea

## presentation of solution

to actually run the rviz simulation, you have to first build the package\

cd ~/src/intro_rover_description
colcon build --symlink-install


cd ~/src/intro_rover_description
source install/setup.bash 
ros2 launch intro_rover_description intro_rover.launch.py

cd ~/src/intro_rover_description
source install/setup.bash 
ros2 run rviz2 rviz2


## to not forget 

do chmod +x path/to/new/executable every time you add a new node script to the package! 

- Command used for the rviz command controller (if you want to run it in a separate terminal instead of with xterm)

ros2 run intro_rover_description keybind_controller.py --ros-args -p mode:=rviz -r joint_commands:=joint_states 

- Command used for the gazebo command controller

ros2 run intro_rover_description keybind_controller.py --ros-args -p mode:=gazebo -p use_sim_time:=true -p hold_time:=0.7

## explanation

- Debugging the launch 

The Cmakelists.txt was missing the amentcpython package to be able to run python base nodes inside the intro_rover_description package 
Also, to setup the colcon build, the required directories for meshes urdf launch and node files had to be installed. 

At the package.xml, I added the dependencies to use amentcpython to launch and added other dependencies like sensors_msg to get Joint_state, as well as 
the launch_ros to configure and launch the created nodes.

State interface is to read and command interface is to write data


- Dancing mode 

To implement the dancing of the robot, I used three nodes: a state publisher node, a linear movement node, and a joint_controller node. 

I decided to separate the logic into three different nodes, because the linear movement of the robot and the joint control do not use the same message type (Twist compared to JointStates). To keep the workflow more structured and distinguish the logic between the two, I made the decision to make three nodes for the dancing mode instead of three.  


**State Publisher Node** 

The state publisher subscribes to the joint_commands topic with JointState message type to be able to recieve joint angles and velocities from the other two nodes. 
The Twist message type with the cmd_vel topic is used to read the linear and angular velocity of the robot as the linear movement node is publishing position and velocity transforms to the robot's wheels. 

The joint and linear movement callback are used to log on the terminal when linear and joint movement message directions are recieved

I create a dictionary where I keep track of the joints and their current angular positions in rad, including the swerve drive joints and the linear wheels to control odometry 

The timer callback method is the method that actually publishes the joint and linear commands to the robot. 

For the odometry data, Transform Stamped is used and for all the joint data, Joint States is used. 

The swerve drive uses combined x and y translations to move the robot in the odometry link's xz frame and quaternions are used to control the joint angles for the arm. Quaternion angles are preferred over euler angles for better interpolation and smoother rotation changes.

**Joint Controller Node**


At the joint controller, every 0.1 seconds, there is an increment multiplier for the joint positions and these positions get published as a message
through JointStates, and that is how the state publisher node can subscribe and listen to those messages. 


**Linear Movement Node**

Likewise, the linear movement node publishes messages through the Twist message type 


- Controller

For the robot to run in URDF, the URDF file had to be modified to include the gazebo headers and parameters 
these include the ros2 control gazebo sim and the odom and base link declarations

I also had to add a controllers.yaml file for the ros2 controller to be configured for gazebo. Inside of it, there is the jointStateBroadcaster declaration (a controller inside ros2_control that gathers velocity and position data), as well as the wheel position controller and the arm swerve position controller.


I also had to add the ros2_control header alongside a declaration of the joints to be able to control them through ros2 control.

Also, I had to install and use the ro2_control package to be able to publish control messages through my keyboard for the robotic arm and wheels 



**Keybind controller node**

This the node that allows you to control the robot through keybinds. 

The arms keys indicate the key indeces with their associated joint direction. The drive keys indicate the directions associated with the drive keys (x, y translation or z rotation)

Contrary to the state publisher, the odom and cmd_vel topics are used because to control the robot within the odom frame, we need a better estimate for the position, orientation and velocity of the robot


I set a joint limit of - pi / 2, pi / 2 for the pitches of the wrist, shoulder and elbow to not clip into other parts of the robot. 
These joint limits are then clamped when we update the joint positions with the high and low joint limits. This gets done in the update method, 
which updates the swerve drive, integrates the odometry and publishes the velocity and position commands 

For the update swerve drive, I use the positive radian convention for standardization of the robot's orientation odometry

For the integration of odometry, I use angle pose estimation with the current robot position and velocity vectors to update the yaw orientation

Two different publishing methods are used depending on if the controller is being used in gazebo or in rviz 

If it is used in gazebo, the joint positions are published through ros control's /arm_swerve_position_controller/commands topic
and the wheel velocities are published through the /wheel_velocity_controller/commands topic 

For rviz, Twist, Transformed and Odometry message types are used for linear velocity, tranforms, and pose orientation and velocity, similar to the state publisher, but the difference is that here, the assigned position changes come from the self.positions list that was changed by the keybind presses with respect to the joint step.

Also, the ys, select, termios, and tty libraries were used for all the keybind logic and updates. 


**Launch Files**

- intro_rover.launch.py

this is the launch file used for rviz, for both the controller mode and the dancing mode. You have to swap comment the state publisher and the keybind controller nodes to switch between these modes (in the future, I could add a user prompt to do this swap instead) 

This is where I declare all the nodes, including the robot state publisher node, the tf2 ros node (used for coordinate frame tracking, so the base and odometry frame), as well as the rviz2 node, which takes the config.rviz file as a parameter to be able to save a current rviz2 config. For example, by default, the robot model is not visible in the simulation, so you have to add it manually finding the urdf file, but once you save that config in the .rviz file, you don't have to do that again. 

for the rviz version of the robot controller, I used xterm to launch an auxiliary terminal where you can press the keybinds to control the robot. This is done by the xterm parameter added to the keybind controller node. 

- gz_sim.launch.py

The gz sim launch uses the ros_gz_sim package to launch gazebo. 

you first need to add ressource gazebo path, the environment variable used to load the world and add other gazebo simulation ressources.

There are four nodes that are declared and then launched through the launch description:
    The robot state publisher, that is used to publish transforms to the robot urdf, just as the rviz launch file. 
    The bridge node is used to link ros2 topics required for odometry, joint state and pose and gazebo such as tf, and odom.
    The robot spawner node allows the robot to be able to spawn inside the empty sdf world in gazebo. 
    The controller manager node which declares the ros2 control topics and all the three declared controllers which appear in the controllers.yaml file.




















