import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, PoseStamped

class DroneFollower(Node):
    def __init__(self):
        super().__init__('drone_follower')

        self.cmd_pub = self.create_publisher(Twist, '/drone/cmd_vel', 10)

        self.create_subscription(PoseStamped, '/world/default/model/drone/pose', self.drone_pose_callback, 10)
        self.create_subscription(PoseStamped, '/world/default/model/target/pose', self.target_pose_callback, 10)

        self.drone_pose = None
        self.target_pose = None

    def drone_pose_callback(self, msg):
        self.drone_pose = msg.pose.position
        self.update_cmd()

    def target_pose_callback(self, msg):
        self.target_pose = msg.pose.position
        self.update_cmd()

    def update_cmd(self):
        if self.drone_pose is None or self.target_pose is None:
            return

        error_x = self.target_pose.x - self.drone_pose.x
        error_y = self.target_pose.y - self.drone_pose.y

        cmd = Twist()
        cmd.linear.x = 0.5 * error_x
        cmd.linear.y = 0.5 * error_y
        cmd.linear.z = 0.0

        self.cmd_pub.publish(cmd)

def main(args=None):
    rclpy.init(args=args)
    node = DroneFollower()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
