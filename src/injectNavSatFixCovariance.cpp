/*!
 * \brief A node to inject covariance values in NavSatFix messages produced
 * by gazebo.  This is for the localisation EKF to be happy.
 * 
 * \todo The topic names should be parameters.  The injected values should be
 * parameters.
 */

#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/nav_sat_fix.hpp>

//Namespace specified for simplfication when using placeholders library
using std::placeholders::_1;

class injectNavSatFixCovariance : public rclcpp::Node
{
public:
  injectNavSatFixCovariance()
  : Node("inject_NavSatFix_covariance")
  {
    navsatfixSub_ = this->create_subscription<sensor_msgs::msg::NavSatFix>(
      "/gps/fix_raw",
      10,
      std::bind(&injectNavSatFixCovariance::navsatfixCallback, this, _1)
    );
    navsatfixPub_ = this->create_publisher<sensor_msgs::msg::NavSatFix>(
      "/gps/fix", 10
    );
  }

private:

  const uint8_t priorityLow = 251;  // A large but not maximum number.
  const uint8_t priorityCritical = 255;  // The max number

  void navsatfixCallback(const sensor_msgs::msg::NavSatFix& msg)
  {
    sensor_msgs::msg::NavSatFix newMsg = msg;
    newMsg.position_covariance[0] = 0.5;
    newMsg.position_covariance[4] = 0.5;
    newMsg.position_covariance[8] = 0.5;
    newMsg.position_covariance_type = 1; // COVARIANCE_TYPE_APPROXIMATED
    navsatfixPub_->publish(newMsg);
  }

  rclcpp::Subscription<sensor_msgs::msg::NavSatFix>::SharedPtr navsatfixSub_;
  rclcpp::Publisher<sensor_msgs::msg::NavSatFix>::SharedPtr navsatfixPub_;
};




//Main method defining entry point for program
int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);

  auto node = std::make_shared<injectNavSatFixCovariance>();
  rclcpp::executors::MultiThreadedExecutor exec;
  exec.add_node(node);
  exec.spin();

  //When the node is terminated, shut down ROS 2 for this node
  rclcpp::shutdown();
  return 0;
}
