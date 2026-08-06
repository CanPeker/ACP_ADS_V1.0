import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from ultralytics import YOLO
from rclpy.qos import QoSProfile, ReliabilityPolicy

class YOLONode(Node):
    def __init__(self):
        super().__init__("YOLO_Node")
        self.model = YOLO("/home/canpeker/Desktop/ACP_ADS_V1.0/src/perception_layer/dnn/yolov8n.pt") # change path 
        self.bridge = CvBridge()
        
        qos = QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT)
        
        self.subscriber = self.create_subscription(
            Image,
            '/sensing/camera/traffic_light/image_raw',
            self.image_callback,
            qos)
        
        self.publisher = self.create_publisher(Image, '/Perception/Object_Detection/yolo_detected_images', 10)
        self.get_logger().info("Yolo Node's been started...")

    def image_callback(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        results = self.model(frame, classes=[0,1,2,3,5,7], conf=0.5, verbose=False)
        annotated = results[0].plot()
        out_msg = self.bridge.cv2_to_imgmsg(annotated, encoding='bgr8')
        out_msg.header = msg.header
        self.publisher.publish(msg=out_msg)

def main(args=None):
    rclpy.init(args=args)
    yolo_node = YOLONode()
    rclpy.spin(node=yolo_node)
    rclpy.shutdown()