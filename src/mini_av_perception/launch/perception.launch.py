from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='mini_av_perception',
            executable='cameraNode',
            name='camera_node',
            output='screen'
        ),
        Node(
            package='mini_av_perception',
            executable='yoloNode',
            name='yolo_node',
            output='screen'
        ),
    ])