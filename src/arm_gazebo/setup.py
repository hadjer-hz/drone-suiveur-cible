import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'arm_gazebo'

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
        (os.path.join('share', package_name, 'models/arm'),
            glob('models/arm/*.sdf') + glob('models/arm/*.config')),
        (os.path.join('share', package_name, 'models/object'),
            glob('models/object/*.sdf') + glob('models/object/*.config')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='hadjer',
    maintainer_email='hadjerzigadi596@gmail.com',
    description='Bras manipulateur 4DOF pick and place',
    license='MIT',
    entry_points={
        'console_scripts': [
            'arm_node = arm_gazebo.arm_node:main',
        ],
    },
)
