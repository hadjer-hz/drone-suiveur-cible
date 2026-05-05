import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'drone_tracker'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'),
            glob('launch/*.py')),
        (os.path.join('share', package_name, 'worlds'),
            glob('worlds/*.sdf')),
        (os.path.join('share', package_name, 'models/drone'),
            glob('models/drone/*.sdf') + glob('models/drone/*.config')),
        (os.path.join('share', package_name, 'models/target'),
            glob('models/target/*.sdf') + glob('models/target/*.config')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='hadjer',
    maintainer_email='hadjerzigadi596@gmail.com',
    description='Drone suiveur de cible',
    license='MIT',
    entry_points={
        'console_scripts': [
            'tracker_node = drone_tracker.tracker_node:main',
        ],
    },
)
