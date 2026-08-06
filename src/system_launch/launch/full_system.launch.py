# system_launch/launch/full_system.launch.py
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():

    perception_launch = IncludeLaunchDescription(

        PythonLaunchDescriptionSource(

            os.path.join(get_package_share_directory('perception_layer'),'launch', 'perception_layer.launch.py')

        )

    )

   

    return LaunchDescription([
        perception_launch,
       
    ])