
"""

awsim---publish --> /sensing/camera/traffic_light/image_raw ---> image_callback()

---> /Perception/Lane/filtered_pos ---> publish
---> /Perception/Lane/detected_frames ---> publish

  
from customInterfaces.msg import LaneRawData
    std_msgs/Header header
    bool detected
    float32[] positions
    
"""
#------------ ros2 lib
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge
from rclpy.qos import QoSProfile, ReliabilityPolicy
from customInterfaces.msg import LaneRawData #custom msg 

#------------- ufld libs
import cv2
from driveAst.ultrafastLaneDetector import UltrafastLaneDetector, ModelType
from filterpy.kalman import KalmanFilter
import numpy as np
import json


class LaneNode(Node):

    def __init__(self):

        super().__init__("LaneNode")
           
        qos = QoSProfile(depth=10,reliability=ReliabilityPolicy.BEST_EFFORT)

        self.rawImage_sub = self.create_subscription(Image,'/sensing/camera/traffic_light/image_raw',self.image_callback,qos)

        self.lane_Img_Publish = self.create_publisher(Image,'/Perception/Lane/detected_frames',10)

        self.kfPos_Publisher = self.create_publisher(LaneRawData, '/Perception/Lane/filtered_pos', 10)

        self.bridge = CvBridge()

        # initiliaze ultra fast lane detection 
        self.model_path = "/home/canpeker/Desktop/avPT1_ws/src/driveAst/driveAst/tusimple_18.pth" # local path ver unutma
        self.model_type = ModelType.TUSIMPLE
        self.use_gpu = True
        self.lane_detector = UltrafastLaneDetector(self.model_path, self.model_type, self.use_gpu)

        # initiliaze kalman filters 
        self.kalman_filters = [self.create_kalman() for _ in range(4)] 

        self.get_logger().info('Lane Node has been started...')

    def create_kalman(self):
        kf = KalmanFilter(dim_x=2, dim_z=1)
        kf.F = np.array([[1., 1.], [0., 1.]])
        kf.H = np.array([[1., 0.]])
        kf.R = np.array([[10.]])
        kf.Q = np.array([[1., 0.], [0., 1.]])
        kf.x = np.array([[0.], [0.]])
        kf.P = np.array([[100., 0.], [0., 10.]])
        return kf

    def filtering(self,points,lanes):
        filtered_positions = []
    
        for i in range(4):
            if lanes[i] and len(points[i]) > 0:
                # Alt Çeyrek noktanın x koordinatını al
                lower = int(len(points[i]) * 0.75)
                x = float(points[i][lower][0])
                
                # Kalman predict + update
                self.kalman_filters[i].predict()
                self.kalman_filters[i].update([[x]])
            else:
                # Ölçüm yok — sadece predict
                self.kalman_filters[i].predict()
            
            # Filtrelenmiş x koordinatı
            filtered_positions.append(
                float(self.kalman_filters[i].x[0][0]))
        
        return filtered_positions  
    
    
    def laneDetection(self,rawImg):
        output_img,points,lanes = self.lane_detector.detect_lanes(rawImg)
        return output_img,points,lanes


    def image_callback(self,msg):
        
        rawFrame = self.bridge.imgmsg_to_cv2(msg,desired_encoding='bgr8')
        detectImg,points,lanes = self.laneDetection(rawImg=rawFrame)
        kfPos = self.filtering(points,lanes)

        lanedata = LaneRawData()
        lanedata.header = msg.header
        lanedata.detected = lanes.tolist()
        lanedata.positions = kfPos
        self.kfPos_Publisher.publish(lanedata)

        finalImage = self.bridge.cv2_to_imgmsg(detectImg,encoding='bgr8')
        finalImage.header = msg.header
        self.lane_Img_Publish.publish(finalImage)


def main(args=None):

    rclpy.init(args=args)

    lane_node = LaneNode()

    rclpy.spin(node=lane_node)

    rclpy.shutdown()



if __name__ == '__main__':
    main()