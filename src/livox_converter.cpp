#include <memory>
#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/point_cloud2.hpp>
#include <livox_ros_driver2/msg/custom_msg.hpp>
#include <pcl_conversions/pcl_conversions.h>
#include <pcl/point_cloud.h>
#include <pcl/point_types.h>

// Define the PointXYZIRT structure that LIORF/LIO-SAM expects
struct PointXYZIRT {
    PCL_ADD_POINT4D;
    float intensity;
    uint16_t ring;
    float time;
    EIGEN_MAKE_ALIGNED_OPERATOR_NEW
} EIGEN_ALIGN16;

POINT_CLOUD_REGISTER_POINT_STRUCT(PointXYZIRT,
    (float, x, x) (float, y, y) (float, z, z) (float, intensity, intensity)
    (uint16_t, ring, ring) (float, time, time)
)

class LivoxConverter : public rclcpp::Node {
public:
    LivoxConverter() : Node("livox_converter") {
        // Subscribe to Livox CustomMsg
        sub_livox = this->create_subscription<livox_ros_driver2::msg::CustomMsg>(
            "/livox/lidar", 10, std::bind(&LivoxConverter::callback, this, std::placeholders::_1));

        // Publish standard PointCloud2
        pub_pcl = this->create_publisher<sensor_msgs::msg::PointCloud2>("/livox/points", 10);
    }

private:
    void callback(const livox_ros_driver2::msg::CustomMsg::SharedPtr msg) {
        pcl::PointCloud<PointXYZIRT>::Ptr cloud(new pcl::PointCloud<PointXYZIRT>());
        
        cloud->header.frame_id = msg->header.frame_id;
        cloud->header.stamp = msg->timebase / 1000; // nanoseconds to microseconds for PCL
        cloud->reserve(msg->point_num);

        for (uint32_t i = 0; i < msg->point_num; ++i) {
            PointXYZIRT p;
            p.x = msg->points[i].x;
            p.y = msg->points[i].y;
            p.z = msg->points[i].z;
            p.intensity = msg->points[i].reflectivity;
            p.ring = msg->points[i].line;
            p.time = static_cast<float>(msg->points[i].offset_time) / 1e9f; // offset in seconds
            cloud->push_back(p);
        }

        sensor_msgs::msg::PointCloud2 output_msg;
        pcl::toROSMsg(*cloud, output_msg);
        output_msg.header = msg->header; // Keep original ROS 2 header time
        pub_pcl->publish(output_msg);
    }

    rclcpp::Subscription<livox_ros_driver2::msg::CustomMsg>::SharedPtr sub_livox;
    rclcpp::Publisher<sensor_msgs::msg::PointCloud2>::SharedPtr pub_pcl;
};

int main(int argc, char** argv) {
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<LivoxConverter>());
    rclcpp::shutdown();
    return 0;
}