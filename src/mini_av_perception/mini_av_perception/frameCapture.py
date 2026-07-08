import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from rclpy.qos import QoSProfile, ReliabilityPolicy
import cv2
import os
from datetime import datetime

class DataCollectorNode(Node):
    def __init__(self):
        super().__init__('data_collector_node')

        qos = QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT)

        self.bridge = CvBridge()

        # Kayıt klasörü — tarih/saat ile otomatik isimlendir
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.save_dir = f'/home/canpeker/Desktop/lane_dataset/session_{timestamp}'
        os.makedirs(self.save_dir, exist_ok=True)

        # Video writer — henüz None, ilk frame gelince başlatacağız
        self.video_writer = None
        self.frame_count = 0

        self.sub = self.create_subscription(Image,'/sensing/camera/traffic_light/image_raw',self.callback,qos)

        self.get_logger().info(f'Data Collector başlatıldı...')
        self.get_logger().info(f'Kayıt klasörü: {self.save_dir}')

    def callback(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

        # İlk frame'de video writer başlat
        if self.video_writer is None:
            h, w = frame.shape[:2]
            video_path = os.path.join(self.save_dir, 'recording.mp4')
            self.video_writer = cv2.VideoWriter(
                video_path,
                cv2.VideoWriter_fourcc(*'mp4v'),
                10,   # FPS — AWSIM ~7 FPS yayınlıyor
                (w, h)
            )
            self.get_logger().info(f'Video başlatıldı: {video_path} ({w}x{h})')

        # Frame'i videoya yaz
        self.video_writer.write(frame)
        self.frame_count += 1

        # Her 30 frame'de bir log
        if self.frame_count % 30 == 0:
            self.get_logger().info(f'{self.frame_count} frame kaydedildi...')

    def destroy_node(self):
        # Node kapanırken video dosyasını kapat
        if self.video_writer:
            self.video_writer.release()
            self.get_logger().info(f'Video kaydedildi. Toplam: {self.frame_count} frame')
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node = DataCollectorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()