import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import math
import time

class ArmController(Node):
    def __init__(self):
        super().__init__('arm_controller')

        self.pub = self.create_publisher(JointState, '/joint_states', 10)

        # Longueurs des segments
        self.L1 = 0.15
        self.L2 = 0.20
        self.L3 = 0.18
        self.L4 = 0.10

        # Positions pick and place
        self.home        = [0.0, 0.0, 0.0, 0.0]
        self.pick_pos    = (0.20, 0.0, 0.10)
        self.place_pos   = (-0.20, 0.0, 0.10)

        self.current_joints = [0.0, 0.0, 0.0, 0.0]

        self.get_logger().info('Arm Controller démarré !')
        self.timer = self.create_timer(0.05, self.run)
        self.state = 'home'
        self.step  = 0
        self.sequence = self.build_sequence()

    def inverse_kinematics(self, x, y, z):
        # Joint 1 - rotation autour de Z
        j1 = math.atan2(y, x)

        # Distance horizontale
        r = math.sqrt(x**2 + y**2)
        h = z - self.L1

        # Distance totale jusqu'à la cible
        D = math.sqrt(r**2 + h**2)
        D = min(D, self.L2 + self.L3 - 0.01)

        # Joint 3 - coude
        cos3 = (D**2 - self.L2**2 - self.L3**2) / (2 * self.L2 * self.L3)
        cos3 = max(-1.0, min(1.0, cos3))
        j3 = -math.acos(cos3)

        # Joint 2 - épaule
        alpha = math.atan2(h, r)
        beta  = math.atan2(self.L3 * math.sin(-j3),
                           self.L2 + self.L3 * math.cos(-j3))
        j2 = alpha - beta

        # Joint 4 - poignet (garde l'effecteur horizontal)
        j4 = -(j2 + j3)

        return [j1, j2, j3, j4]

    def build_sequence(self):
        seq = []
        # home -> pick
        seq.append(('move', self.inverse_kinematics(*self.pick_pos), 60))
        # saisir
        seq.append(('wait', None, 20))
        # lever
        seq.append(('move', self.inverse_kinematics(0.20, 0.0, 0.25), 60))
        # aller au place
        seq.append(('move', self.inverse_kinematics(*self.place_pos), 80))
        # poser
        seq.append(('wait', None, 20))
        # retour home
        seq.append(('move', self.home, 60))
        return seq

    def interpolate(self, start, end, t, total):
        return [s + (e - s) * t / total for s, e in zip(start, end)]

    def publish_joints(self, angles):
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name     = ['joint1', 'joint2', 'joint3', 'joint4']
        msg.position = angles
        self.pub.publish(msg)

    def run(self):
        if self.step >= len(self.sequence):
            self.publish_joints(self.home)
            return

        action, target, duration = self.sequence[self.step]

        if action == 'wait':
            self.state_counter = getattr(self, 'state_counter', 0) + 1
            if self.state_counter >= duration:
                self.state_counter = 0
                self.step += 1
                self.get_logger().info(f'Etape {self.step} terminee')
            self.publish_joints(self.current_joints)

        elif action == 'move':
            self.move_counter = getattr(self, 'move_counter', 0) + 1
            self.current_joints = self.interpolate(
                self.current_joints, target,
                self.move_counter, duration)
            self.publish_joints(self.current_joints)
            if self.move_counter >= duration:
                self.move_counter = 0
                self.current_joints = target
                self.step += 1
                self.get_logger().info(f'Etape {self.step} terminee')

def main(args=None):
    rclpy.init(args=args)
    node = ArmController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
