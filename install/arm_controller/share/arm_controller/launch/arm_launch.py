import os
from launch import LaunchDescription
from launch.actions import TimerAction
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    pkg_dir = get_package_share_directory('arm_controller')
    urdf_file = os.path.join(pkg_dir, 'urdf', 'arm.urdf')
    rviz_file = os.path.join(pkg_dir, 'rviz', 'arm.rviz')

    with open(urdf_file, 'r') as f:
        robot_description = f.read()

    return LaunchDescription([

        # Publier robot_description comme topic ET paramètre
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            parameters=[{
                'robot_description': robot_description,
                'publish_frequency': 50.0
            }],
            remappings=[('/robot_description', '/robot_description')],
            output='screen'
        ),

        # Noeud de controle
        Node(
            package='arm_controller',
            executable='arm_node',
            name='arm_controller',
            output='screen'
        ),

        # RViz2 après 3 secondes
        TimerAction(
            period=3.0,
            actions=[
                Node(
                    package='rviz2',
                    executable='rviz2',
                    name='rviz2',
                    arguments=['-d', rviz_file],
                    output='screen'
                )
            ]
        ),
    ])
