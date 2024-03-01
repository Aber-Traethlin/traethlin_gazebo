cmake_minimum_required(VERSION 3.5)
project(traethlin_gazebo)

find_package(ament_cmake)

find_package(traethlin_description REQUIRED)
find_package(gazebo_ros_ackermann_drive_4wd REQUIRED)

install(DIRECTORY
  rviz
  launch
  worlds
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
