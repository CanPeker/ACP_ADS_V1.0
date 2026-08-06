from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='perception_layer',
            executable='objectDetectionNode',
            name='yolo_node_custom',
            output='screen'
        ),
        Node(
                    package='perception_layer',
                    executable='laneDetectionNode',
                    name='ufld_node',
                    output='screen'
                ),
        


    ])