import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node


def generate_launch_description():

    share_dir = get_package_share_directory('liorf')
    parameter_file = LaunchConfiguration('params_file')
    rviz_config_file = os.path.join("/home/curdin/lio-sam_ws/src/liorf", 'rviz', 'mapping.rviz')

    params_declare = DeclareLaunchArgument(
        'params_file',
        default_value=os.path.join(
            # share_dir, 'config', 'lio_sam_fairy_livox_imu.yaml'),
            share_dir, 'config', 'lio_sam_fairy.yaml'),
        description='FPath to the ROS2 parameters file to use.')

    use_sim_time = LaunchConfiguration('use_sim_time')
    use_sim_time_declare = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        description='Use simulation clock if true.')

    return LaunchDescription([
        params_declare,
        use_sim_time_declare,
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            arguments='0.0 0.0 0.0 0.0 0.0 0.0 map odom'.split(' '),
            parameters=[parameter_file, {'use_sim_time': use_sim_time}],
            output='screen',
        ),
        Node(
            package='liorf',
            executable='liorf_imuPreintegration',
            name='liorf_imuPreintegration',
            parameters=[parameter_file, {'use_sim_time': use_sim_time}],
            output='screen'
        ),
        Node(
            package='liorf',
            executable='liorf_imageProjection',
            name='liorf_imageProjection',
            parameters=[parameter_file, {'use_sim_time': use_sim_time}],
            output='screen'
        ),
        Node(
            package='liorf',
            executable='liorf_mapOptmization',
            name='liorf_mapOptmization',
            parameters=[parameter_file, {'use_sim_time': use_sim_time}],
            output='screen'
        ),
        # Node(
        #     package='liorf',
        #     executable='livox_converter',
        #     name='livox_converter',
        #     output='screen'
        # ),
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', rviz_config_file],
            parameters=[{'use_sim_time': use_sim_time}],
            output='screen'
        )
    ])