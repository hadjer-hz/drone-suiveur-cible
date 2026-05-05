import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess, TimerAction
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    pkg   = get_package_share_directory('drone_follower')
    world = os.path.join(pkg, 'worlds', 'drone_world.sdf')
    return LaunchDescription([
        ExecuteProcess(
            cmd=['gz', 'sim', '-r', world],
            output='screen'
        ),
        TimerAction(period=3.0, actions=[
            Node(
                package='ros_gz_bridge',
                executable='parameter_bridge',
                name='gz_bridge',
                arguments=[
                    '/drone/camera@sensor_msgs/msg/Image@gz.msgs.Image',
                    '/drone/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
                ],
                output='screen'
            ),
            Node(package='drone_follower', executable='vision_node',    output='screen'),
            Node(package='drone_follower', executable='controller_node', output='screen'),
        ])
    ])
