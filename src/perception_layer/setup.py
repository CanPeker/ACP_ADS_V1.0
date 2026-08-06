from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'perception_layer'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
         (os.path.join('share', package_name, 'launch'),
                    glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='canpeker',
    maintainer_email='cpeker16@hotmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'objectDetectionNode=perception_layer.yolo_node:main',
            'laneDetectionNode=perception_layer.laneDetectorNode:main'
        ],
    },
)
