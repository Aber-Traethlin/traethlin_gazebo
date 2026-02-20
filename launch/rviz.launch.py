import launch
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
  current_pkg = FindPackageShare('traethlin_gazebo')

  use_sim_time_ = LaunchConfiguration('use_sim_time')
  use_sim_time_launch_arg = DeclareLaunchArgument(
    'use_sim_time',
    default_value='true'
  )

  return launch.LaunchDescription(
    [
      use_sim_time_launch_arg,

      DeclareLaunchArgument(
        'rviz_config',
        default_value=PathJoinSubstitution([current_pkg, 'rviz',
                                            'traethlin.rviz']),
        description='Full path to the rviz config file to use',
      ),

      Node(
        package='rviz2',
        executable='rviz2',
        name='rviz',
        output={'both': 'log'},
        parameters=[{
          'use_sim_time': use_sim_time_
        }],
        arguments=['-d', LaunchConfiguration('rviz_config')]
      ),
    ]
  )
