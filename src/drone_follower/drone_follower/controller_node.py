#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point, Twist

class ControllerNode(Node):
    def __init__(self):
        super().__init__('controller_node')
        self.kp_yaw      = 0.3
        self.kp_altitude = 0.2
        self.kp_forward  = 0.2
        self.target_area = 0.05
        self.dead_zone   = 0.03
        self.sub = self.create_subscription(Point, '/target_point', self.target_cb, 10)
        self.pub = self.create_publisher(Twist, '/drone/cmd_vel', 10)
        self.last_seen = self.get_clock().now()
        self.create_timer(0.05, self.safety_loop)
        self.get_logger().info('Controleur demarre')

    def dead(self, v):
        return v if abs(v) > self.dead_zone else 0.0

    def clamp(self, v, lo, hi):
        return max(lo, min(hi, v))

    def target_cb(self, pt):
        self.last_seen = self.get_clock().now()
        cmd = Twist()
        cmd.angular.z = self.clamp(-self.kp_yaw      * self.dead(pt.x), -0.5, 0.5)
        cmd.linear.z  = self.clamp(-self.kp_altitude * self.dead(pt.y), -0.3, 0.3)
        cmd.linear.x  = self.clamp( self.kp_forward  * (self.target_area - pt.z), -0.3, 0.3)
        self.pub.publish(cmd)
        self.get_logger().info(
            f'CMD vx={cmd.linear.x:.2f} vz={cmd.linear.z:.2f} wz={cmd.angular.z:.2f}',
            throttle_duration_sec=0.5)

    def safety_loop(self):
        elapsed = (self.get_clock().now() - self.last_seen).nanoseconds / 1e9
        if elapsed > 0.5:
            self.pub.publish(Twist())

def main(args=None):
    rclpy.init(args=args)
    rclpy.spin(ControllerNode())
    rclpy.shutdown()

if __name__ == '__main__':
    main()
