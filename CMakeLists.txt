cmake_minimum_required(VERSION 3.5)
project(traethlin_gazebo)

find_package(ament_cmake_auto REQUIRED)
ament_auto_find_build_dependencies()

ament_auto_add_executable(
  inject_navsatfix_covariance_node
  "src/injectNavSatFixCovariance.cpp")  


install(DIRECTORY
  rviz
  launch
  worlds
  config
  DESTINATION share/${PROJECT_NAME}
)

ament_auto_package()
