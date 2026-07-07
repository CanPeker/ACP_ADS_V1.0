
"""

sub --> awsim img raw 

lane detect process 

pub --> detect lane 


"""
#------------ ros2 lib
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge
from rclpy.qos import QoSProfile, ReliabilityPolicy

#------------- ufld libs
import cv2
from driveAst.ultrafastLaneDetector import UltrafastLaneDetector, ModelType

class LaneNode(Node):

    def __init__(self):

        super().__init__("LaneNode")
           
        qos = QoSProfile(depth=10,reliability=ReliabilityPolicy.BEST_EFFORT)

        self.image_sub = self.create_subscription(Image,'/sensing/camera/traffic_light/image_raw',self.image_callback,qos)

        self.lanePublish = self.create_publisher(Image,'/lane/detected_lanes',10)

        self.bridge = CvBridge()

        # initiliaze ultra fast lane detection 

        self.model_path = "/home/canpeker/Desktop/avPT1_ws/src/driveAst/driveAst/tusimple_18.pth" # local path ver unutma
        self.model_type = ModelType.TUSIMPLE
        self.use_gpu = True
        self.lane_detector = UltrafastLaneDetector(self.model_path, self.model_type, self.use_gpu)

    
    def laneDetection(self,rawImg):
        output_img = self.lane_detector.detect_lanes(rawImg)
        array = [0,0]
        return output_img,array


    def image_callback(self,msg):
        
        rawFrame = self.bridge.imgmsg_to_cv2(msg,desired_encoding='bgr8')

        detectImg,_ = self.laneDetection(rawImg=rawFrame)

        detectImg = self.bridge.cv2_to_imgmsg(detectImg,encoding='bgr8')
        detectImg.header = msg.header
        self.lanePublish.publish(detectImg)


def main(args=None):

    rclpy.init(args=args)

    lane_node = LaneNode()

    rclpy.spin(node=lane_node)

    rclpy.shutdown()



if __name__ == '__main__':
    main()