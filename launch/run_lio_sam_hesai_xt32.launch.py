import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node
from launch.conditions import UnlessCondition


def generate_launch_description():

    share_dir = get_package_share_directory('liorf')
    parameter_file = LaunchConfiguration('params_file')
    rviz_config_file = os.path.join("/home/curdin/lio-sam_ws/src/liorf", 'rviz', 'mapping.rviz')

    params_declare = DeclareLaunchArgument(
        'params_file',
        default_value=os.path.join(
            share_dir, 'config', 'lio_sam_mid360.yaml'),
        description='FPath to the ROS2 parameters file to use.')
    no_viz = LaunchConfiguration('no_viz')
    no_viz_declare = DeclareLaunchArgument(
        'no_viz',
        default_value='false',
        description='If true, do not launch RViz')
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config_file],
        condition=UnlessCondition(no_viz),
        output='screen'
    )
    return LaunchDescription([
        params_declare,
        no_viz_declare,
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            arguments='0.0 0.0 0.0 0.0 0.0 0.0 map odom'.split(' '),
            parameters=[parameter_file],
            output='screen'
        ),
        Node(
            package='liorf',
            executable='liorf_imuPreintegration',
            name='liorf_imuPreintegration',
            parameters=[parameter_file],
            output='screen'
        ),
        Node(
            package='liorf',
            executable='liorf_imageProjection',
            name='liorf_imageProjection',
            parameters=[parameter_file],
            output='screen'
        ),
        Node(
            package='liorf',
            executable='liorf_mapOptmization',
            name='liorf_mapOptmization',
            parameters=[parameter_file],
            output='screen'
        ),
        rviz_node
        # Node(
        #     package='rviz2',
        #     executable='rviz2',
        #     name='rviz2',
        #     arguments=['-d', rviz_config_file],
        #     output='screen'
        # )
    ])