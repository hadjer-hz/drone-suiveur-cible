#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Point
from cv_bridge import CvBridge
import cv2
import numpy as np

class VisionNode(Node):
    def __init__(self):
        super().__init__('vision_node')
        self.bridge = CvBridge()
        self.sub = self.create_subscription(Image, '/drone/camera', self.image_cb, 10)
        self.pub = self.create_publisher(Point, '/target_point', 10)
        self.get_logger().info('Vision node demarre')

    def image_cb(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='rgb8')
        if frame is None or frame.size == 0:
            return
        hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)

        lo1, hi1 = np.array([0,   120, 70]), np.array([10,  255, 255])
        lo2, hi2 = np.array([170, 120, 70]), np.array([180, 255, 255])
        mask = cv2.inRange(hsv, lo1, hi1) | cv2.inRange(hsv, lo2, hi2)
        k    = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN,  k)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, k)

        M = cv2.moments(mask)
        if M['m00'] > 300:
            h, w = frame.shape[:2]
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])
            pt = Point()
            pt.x = (cx - w / 2.0) / (w / 2.0)
            pt.y = (cy - h / 2.0) / (h / 2.0)
            pt.z = M['m00'] / float(w * h)
            self.pub.publish(pt)
            self.get_logger().info(
                f'Cible : ex={pt.x:.2f} ey={pt.y:.2f} aire={pt.z:.3f}',
                throttle_duration_sec=0.5)
        else:
            self.get_logger().warn('Cible perdue', throttle_duration_sec=1.0)

def main(args=None):
    rclpy.init(args=args)
    rclpy.spin(VisionNode())
    rclpy.shutdown()

if __name__ == '__main__':
    main()
