import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64
import math

class ArmController(Node):
    def __init__(self):
        super().__init__('arm_controller')

        self.pub1 = self.create_publisher(Float64, '/arm/joint1', 10)
        self.pub2 = self.create_publisher(Float64, '/arm/joint2', 10)
        self.pub3 = self.create_publisher(Float64, '/arm/joint3', 10)
        self.pub4 = self.create_publisher(Float64, '/arm/joint4', 10)

        self.L1 = 0.15
        self.L2 = 0.20
        self.L3 = 0.18
        self.L4 = 0.10

        # Position de la box dans le SDF : x=0.25, y=0, z=0.025
        self.pick_pos  = (0.25, 0.0, 0.05)
        self.place_pos = (0.0, 0.25, 0.10)
        self.home      = [0.0, 0.0, 0.0, 0.0]

        self.current  = [0.0, 0.0, 0.0, 0.0]
        self.step     = 0
        self.counter  = 0
        self.sequence = self.build_sequence()

        self.timer = self.create_timer(0.05, self.run)
        self.get_logger().info('Arm Controller démarré !')

    def ik(self, x, y, z):
        j1 = math.atan2(y, x)
        r  = math.sqrt(x**2 + y**2)
        h  = z - self.L1

        D  = math.sqrt(r**2 + h**2)
        D  = min(D, self.L2 + self.L3 - 0.01)

        cos3 = (D**2 - self.L2**2 - self.L3**2) / (2 * self.L2 * self.L3)
        cos3 = max(-1.0, min(1.0, cos3))
        j3   = -math.acos(cos3)

        alpha = math.atan2(h, r)
        beta  = math.atan2(self.L3 * math.sin(-j3),
                           self.L2 + self.L3 * math.cos(-j3))
        j2 = alpha - beta
        j4 = -(j2 + j3)

        self.get_logger().info(f'IK -> j1={j1:.2f} j2={j2:.2f} j3={j3:.2f} j4={j4:.2f}')
        return [j1, j2, j3, j4]

    def build_sequence(self):
        seq = []
        seq.append(('move', self.ik(0.25, 0.0, 0.30), 60))  # approche haute
        seq.append(('move', self.ik(*self.pick_pos),   60))  # descendre sur pick
        seq.append(('wait', None,                       30))  # saisir
        seq.append(('move', self.ik(0.25, 0.0, 0.30), 60))  # lever
        seq.append(('move', self.ik(*self.place_pos),  80))  # aller au place
        seq.append(('wait', None,                       30))  # poser
        seq.append(('move', self.home,                  60))  # retour home
        return seq

    def interpolate(self, start, end, t, total):
        return [s + (e - s) * t / total for s, e in zip(start, end)]

    def publish(self, angles):
        for pub, val in zip(
            [self.pub1, self.pub2, self.pub3, self.pub4], angles):
            msg = Float64()
            msg.data = float(val)
            pub.publish(msg)

    def run(self):
        if self.step >= len(self.sequence):
            self.publish(self.home)
            return

        action, target, duration = self.sequence[self.step]
        self.counter += 1

        if action == 'wait':
            self.publish(self.current)
            if self.counter >= duration:
                self.counter = 0
                self.step += 1
                self.get_logger().info(f'Etape {self.step} terminee')

        elif action == 'move':
            joints = self.interpolate(self.current, target,
                                      self.counter, duration)
            self.publish(joints)
            if self.counter >= duration:
                self.current = target
                self.counter = 0
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
