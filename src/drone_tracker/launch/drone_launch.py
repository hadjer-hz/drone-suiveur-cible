import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess, TimerAction
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    pkg_dir = get_package_share_directory('drone_tracker')
    world_file = os.path.join(pkg_dir, 'worlds', 'drone_world.sdf')
    models_dir = os.path.join(pkg_dir, 'models')

    gz_env = {**os.environ, 'GZ_SIM_RESOURCE_PATH': models_dir}

    return LaunchDescription([

        # Lancer Gazebo server
        ExecuteProcess(
            cmd=['gz', 'sim', '-r', world_file],
            env=gz_env,
            output='screen'
        ),

        # Lancer Gazebo GUI séparément
        TimerAction(
            period=2.0,
            actions=[
                ExecuteProcess(
                    cmd=['gz', 'sim', '-g'],
                    env=gz_env,
                    output='screen'
                )
            ]
        ),

        # Attendre puis lancer le nœud tracker
        TimerAction(
            period=5.0,
            actions=[
                Node(
                    package='drone_tracker',
                    executable='tracker_node',
                    name='drone_tracker',
                    output='screen'
                )
            ]
        )
    ])
