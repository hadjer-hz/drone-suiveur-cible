# Drone Suiveur de Cible

Simulation d'un drone autonome qui suit une cible rouge avec ROS2 Jazzy et Gazebo Harmonic.

## Technologies

- ROS2 Jazzy
- Gazebo Harmonic
- Python 3
- Ubuntu 24.04

## Installation

git clone git@github.com:hadjer-hz/drone-suiveur-cible.git
cd drone-suiveur-cible
colcon build --packages-select drone_tracker
source install/setup.bash

## Lancer la simulation

ros2 launch drone_tracker drone_launch.py

## Auteur

Hadjer Zigadi
