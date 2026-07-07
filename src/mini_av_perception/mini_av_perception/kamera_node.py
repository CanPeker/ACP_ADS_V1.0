import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2

class camNode(Node):
    
    def __init__(self):

        super().__init__("camera_node")

        self.publisher = self.create_publisher(Image,'/camera/image_raw',10)

        self.bridge = CvBridge()

        self.cap = cv2.VideoCapture('/home/canpeker/Desktop/dnn/test_clip.mp4')

        self.timer = self.create_timer(0.033,self.timer_callback)

        self.get_logger().info("cam node's been started...")


    def timer_callback(self):
        
        ret,frame = self.cap.read()

        if not ret:
            self.get_logger().info("video bitti frame = 0")
            self.cap.set(cv2.CAP_PROP_POS_FRAMES,0)
            return 
        
        msg = self.bridge.cv2_to_imgmsg(frame,encoding='bgr8')
        self.publisher.publish(msg=msg)


def main(args=None):

    rclpy.init(args=args)

    cam_node = camNode()

    rclpy.spin(node=cam_node)

    rclpy.shutdown()
