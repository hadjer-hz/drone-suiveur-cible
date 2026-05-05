import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, PoseStamped
from nav_msgs.msg import Odometry
import math

class DroneTracker(Node):
    def __init__(self):
        super().__init__('drone_tracker')

        # Publisher pour commander le drone
        self.cmd_pub = self.create_publisher(Twist, '/drone/cmd_vel', 10)

        # Subscriber pour la position du drone
        self.odom_sub = self.create_subscription(
            Odometry, '/drone/odometry', self.odom_callback, 10)

        # Position du drone
        self.drone_x = 0.0
        self.drone_y = 0.0
        self.drone_z = 0.0

        # Position de la cible (fixe pour l'instant)
        self.target_x = 5.0
        self.target_y = 0.0
        self.target_z = 0.5

        # Seuil d'arrêt (distance minimale)
        self.threshold = 0.5

        # Timer de contrôle
        self.timer = self.create_timer(0.1, self.control_loop)

        self.get_logger().info('Drone Tracker démarré !')

    def odom_callback(self, msg):
        self.drone_x = msg.pose.pose.position.x
        self.drone_y = msg.pose.pose.position.y
        self.drone_z = msg.pose.pose.position.z

    def control_loop(self):
        # Calcul de la distance
        dx = self.target_x - self.drone_x
        dy = self.target_y - self.drone_y
        dz = self.target_z - self.drone_z
        distance = math.sqrt(dx**2 + dy**2 + dz**2)

        cmd = Twist()

        if distance > self.threshold:
            # Vitesse proportionnelle à la distance (avec limite)
            speed = min(0.5, distance * 0.3)

            # Direction vers la cible (normalisée)
            cmd.linear.x = (dx / distance) * speed
            cmd.linear.y = (dy / distance) * speed
            cmd.linear.z = (dz / distance) * speed

            self.get_logger().info(
                f'Distance: {distance:.2f}m | '
                f'dx={dx:.2f} dy={dy:.2f} dz={dz:.2f}')
        else:
            # Cible atteinte, on s'arrête
            cmd.linear.x = 0.0
            cmd.linear.y = 0.0
            cmd.linear.z = 0.0
            self.get_logger().info('Cible atteinte ! ✅')

        self.cmd_pub.publish(cmd)

def main(args=None):
    rclpy.init(args=args)
    node = DroneTracker()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
