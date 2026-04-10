import os
from ament_index_python.packages import (
  get_package_share_directory,
  get_package_prefix
  )
from launch import LaunchDescription, conditions
from launch.substitutions import (
  Command,
  LaunchConfiguration,
  PathJoinSubstitution,
  EqualsSubstitution
  )
from launch.actions import (
  DeclareLaunchArgument,
  ExecuteProcess,
  SetEnvironmentVariable,
  IncludeLaunchDescription
  )
from launch_ros.actions import Node
from launch.conditions import LaunchConfigurationEquals, IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource

ros_distro = os.environ['ROS_DISTRO']
if ros_distro == "jazzy":
  from ros_gz_bridge.actions import RosGzBridge
## Nothing to do for humble...

import subprocess # To find gazebo version
import shutil # To find which gazebo executable is around...
import sys # For exit.

output_dest = "log"

pkg_name = "traethlin_gazebo"

def generate_launch_description():
  pkg_traethlin_description = get_package_share_directory('traethlin_description')
  pkg_install_path_TG = get_package_prefix(pkg_name) + "/share"
  pkg_install_path_TG_worlds = pkg_install_path_TG + "/" + pkg_name + "/worlds"
  pkg_install_path_TD = get_package_prefix('traethlin_description') + "/share"

  if 'GZ_SIM_RESOURCE_PATH' in os.environ:
      resource_path =  os.environ['GZ_SIM_RESOURCE_PATH'] + ':' + pkg_install_path_TG + ':' + pkg_install_path_TD + ':' + pkg_install_path_TG_worlds
  else:
      resource_path =  pkg_install_path_TG + ':' + pkg_install_path_TD + ':' + pkg_install_path_TG_worlds
#  print("------------------", resource_path);

  config = os.path.join(pkg_install_path_TG, pkg_name, 'config', 'traethlin.yaml')
  config_ign = os.path.join(pkg_install_path_TG, pkg_name, 'config', 'traethlin_ign.yaml')

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
    default_value='traethlin.sdf'
  )

  world = PathJoinSubstitution([pkg_name, 'worlds', world_file_name])

  camera_type_ = LaunchConfiguration('camera_type')
  camera_type_launch_arg = DeclareLaunchArgument(
    'camera_type',
    default_value='oak-d-s2',
    description="Can be 'oak-d-s2' or 'd455' (realsense)"
  )

  robot_x_ = LaunchConfiguration("robot_x")
  robot_x_launch_arg = DeclareLaunchArgument(
    'robot_x',
    default_value='0.0',
    description="X coordinate of the robot when launching"
  )

  robot_y_ = LaunchConfiguration("robot_y")
  robot_y_launch_arg = DeclareLaunchArgument(
    'robot_y',
    default_value='0.0',
    description="Y coordinate of the robot when launching"
  )

  gzCommand = ""
  gzPath = shutil.which("ign")
  if gzPath is None:
      gzPath = shutil.which("gz")
      if gzPath is None:
        sys.exit("No gazebo executable, bailing out.")
      else:
        gzCommand = "sim"
  else:
    gzCommand = "gazebo"
  print(f"found gazebo: {gzPath} {gzCommand}")

  gzVersion = subprocess.run(
    [gzPath, gzCommand, "--versions"],
    capture_output = True, # Python >= 3.7 only
    text = True # Python >= 3.7 only
  )
  gzVersion.stdout = gzVersion.stdout.strip('\n')
#  print(gzVersion.stdout)
  gzVersions = gzVersion.stdout.split(".")
#  print(gzVersions)
  gzVersionMajor = gzVersions[0]
#  gzVersionMinor = gzVersions[1]
#  print("Major version:", gzVersionMajor, "minor version", gzVersionMinor)

  traethlin_urdf = Command(['xacro', ' camera_type:=', camera_type_,
                            ' gazebo_major_version:=' , gzVersionMajor,
                            ' ', os.path.join(pkg_traethlin_description,
                                          'urdf',
                                          'traethlin.urdf.xacro')])

  remappings=[
    ('/camera/color/image_raw', '/oak/rgb/image_raw'),
    ('/camera/depth/image_rect_raw', '/oak/stereo/image_raw'),
  ]

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
    remappings=remappings
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
    remappings=remappings,
    respawn=True
  )

  gz_sim = IncludeLaunchDescription(
    PythonLaunchDescriptionSource(
      [
        os.path.join(
          get_package_share_directory("ros_gz_sim"),
          "launch",
          "gz_sim.launch.py",
        )
      ]
    ),
    launch_arguments={"gz_args": [" -r -v 4 ", world]}.items(),
  )

  # Spawn the robot in Gazebo
  spawn_entity = Node(
    package="ros_gz_sim",
    executable="create",
    arguments=[
      "-name",
      "traethlin",
      "-topic",
      "/robot_description",
      "-x", robot_x_, # 9.992638469324447
      "-y", robot_y_, # 15.239376132376492
      "-z", "1.5",
      "-P", "0.0",
      "-R", "0.0",
      "-Y", "0" # 90deg, 1.57rad
    ],
    output="screen",
  )

  # Gz - ROS Bridge
  if ros_distro == "jazzy":
    ros_gz_bridge = RosGzBridge(
        bridge_name='ros_gz_bridge',
        config_file=config,
    )
  elif ros_distro == "humble":
    ros_gz_bridge = Node(
      package='ros_gz_bridge',
      executable='parameter_bridge',
      parameters=[{'config_file': config}],
    )

  # We inject covariance values that are not zero in the GPS messages for the
  # EKF to be happy.
  inject_covariance = Node(
     package='traethlin_gazebo',
     executable='inject_navsatfix_covariance_node'
  )

  return LaunchDescription([
    namespace_launch_arg,
    use_sim_time_launch_arg,
    world_launch_arg,
    camera_type_launch_arg,
    robot_x_launch_arg,
    robot_y_launch_arg,

    SetEnvironmentVariable(name='GZ_SIM_RESOURCE_PATH', value=resource_path),

    robot_state_publisher,

    joint_state_publisher,

    # Gazebo
    gz_sim,
    spawn_entity,
    ros_gz_bridge,
    inject_covariance,

    Node(
      package = "tf2_ros",
      condition=IfCondition(EqualsSubstitution(camera_type_, 'oak-d-s2')),
      executable = "static_transform_publisher",
      parameters=[{
        'use_sim_time': use_sim_time_
      }],
      arguments = ["0", "0", "0", "0", "0", "0", "oak_rgb_camera_optical_frame", "camera_depth_optical_frame"]
    )

  ])
