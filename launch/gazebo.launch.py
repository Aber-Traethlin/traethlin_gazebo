import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription, conditions
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch.actions import DeclareLaunchArgument, ExecuteProcess, SetEnvironmentVariable
from launch_ros.actions import Node
from launch.conditions import LaunchConfigurationEquals

output_dest = "log"

def generate_launch_description():
  pkg_traethlin_description = get_package_share_directory('traethlin_description')

  pkg_install_path = get_package_share_directory('traethlin_gazebo')
  if 'GAZEBO_MODEL_PATH' in os.environ:
      model_path =  os.environ['GAZEBO_MODEL_PATH'] + ':' + pkg_install_path
  else:
      model_path =  pkg_install_path
#  print("------------------------------", model_path)
  if 'GAZEBO_RESOURCE_PATH' in os.environ:
      resource_path =  os.environ['GAZEBO_RESOURCE_PATH'] + ':' + pkg_install_path
  else:
      resource_path =  pkg_install_path
#  print("------------------", resource_path);

  use_sim_time_ = LaunchConfiguration('use_sim_time')
  use_sim_time_launch_arg = DeclareLaunchArgument(
    'use_sim_time',
    default_value='true'
  )

  namespace_ = LaunchConfiguration('namespace')

  namespace_launch_arg = DeclareLaunchArgument(
    'namespace',
    default_value=''
  )

  world_file_name = LaunchConfiguration('world')
  world_launch_arg = DeclareLaunchArgument(
    'world',
    default_value='traethlin.world'
  )

  world = PathJoinSubstitution(['worlds', world_file_name])

  camera_type_ = LaunchConfiguration('camera_type')
  camera_type_launch_arg = DeclareLaunchArgument(
    'camera_type',
    default_value='oak-d-s2',
    description="Can be 'oak-d-s2' or 'd455' (realsense)"
  )


  traethlin_urdf = Command(['xacro', ' camera_type:=', camera_type_, ' ',
                            os.path.join(pkg_traethlin_description,
                                          'urdf',
                                          'traethlin.urdf.xacro')])

  robot_state_publisher = Node(
    package='robot_state_publisher',
    executable='robot_state_publisher',
    name='robot_state_publisher',
    namespace=namespace_,
    parameters=[{
      'robot_description': traethlin_urdf,
      'use_sim_time': use_sim_time_
      }],
    output={"both": output_dest},
    arguments=['--ros-args', '--log-level', 'WARN'],
    respawn=True,
#    remappings=[
#        ('/oak/robot_description', '/robot_description')
#      ]
    )


  joint_state_publisher = Node(
    package='joint_state_publisher',
    name='joint_state_publisher',
    executable='joint_state_publisher',
    namespace=namespace_,
    output={"both": output_dest},
    parameters=[{
      'use_sim_time': use_sim_time_
      }],
    arguments=['--ros-args', '--log-level', 'WARN'],
    respawn=True
    )

  return LaunchDescription([
    namespace_launch_arg,
    use_sim_time_launch_arg,
    world_launch_arg,
    camera_type_launch_arg,

    SetEnvironmentVariable(name='GAZEBO_MODEL_PATH', value=model_path),
    SetEnvironmentVariable(name='GAZEBO_RESOURCE_PATH', value=resource_path),


    ExecuteProcess(
            cmd=['gazebo', '--verbose', world,
                 '-s', 'libgazebo_ros_init.so',
                 '-s', 'libgazebo_ros_factory.so'],
            output='screen'),

    robot_state_publisher,

    joint_state_publisher,

    Node(
      package='gazebo_ros',
      executable='spawn_entity.py',
      name='urdf_spawner',
      output='screen',
      parameters=[{
         'use_sim_time': use_sim_time_
      }],
      arguments=["-robot_namespace", namespace_,
                 "-topic", [namespace_, "/robot_description"],
                 "-entity", "traethlin"]
    ),

    Node(
      package = "tf2_ros",
      condition=LaunchConfigurationEquals('camera_type', 'oak-d-s2'),
      executable = "static_transform_publisher",
      parameters=[{
        'use_sim_time': use_sim_time_
      }],
      arguments = ["0", "0", "0", "0", "0", "0", "camera_rgb_camera_optical_frame", "camera_depth_optical_frame"]
    )

  ])
