from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'system_launch'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),

            # ----------- eklenen kısım
        
          (os.path.join('share', package_name, 'launch'),
            glob('launch/*.launch.py')),

        # ----------- eklenen kısım
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
        ],
    },
)
