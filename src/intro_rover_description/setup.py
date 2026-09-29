from setuptools import setup, find_packages
import os
from glob import glob

package_name = 'intro_rover_description'

setup(
     name=package_name,
        version='0.0.0',
        packages=find_packages(exclude=['test']),
        data_files=[
            ('share/ament_index/resource_index/packages',
                ['resource/' + package_name]),
            ('share/' + package_name, ['package.xml']),
            (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
            (os.path.join('share', package_name, 'urdf'), glob('urdf/*.urdf')),
            (os.path.join('share', package_name, 'meshes'), glob('meshes/*')),
            (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
        ],
        install_requires=['setuptools'],
        zip_safe=True,
        maintainer='buffshark444',
        maintainer_email = 'sebassotosandrea@gmail.com',
        description='TODO: Package description',
        license='TODO: License declaration',
        entry_points= {
            'console_scripts': [
                'state_publisher_node = intro_rover_description.launch.state_publisher:main',
            ],
        },
)
   