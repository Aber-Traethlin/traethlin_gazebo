cmake_minimum_required(VERSION 3.5)
project(traethlin_gazebo)

find_package(ament_cmake)

find_package(depthai_descriptions)
find_package(realsense2_description)
find_package(traethlin_description REQUIRED)

install(DIRECTORY
  rviz
  launch
  worlds
  config
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
