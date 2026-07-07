# klavye ile araç kontrol edilecek 
"""
AckermannControlCommand
├── stamp        → builtin_interfaces/Time
├── lateral      → AckermannLateralCommand
│     ├── steering_tire_angle          ← direksiyon degree (radyan)
│     └── steering_tire_rotation_rate  ← dönüş speed
└── longitudinal → LongitudinalCommand
      ├── speed        ← hedef speed (m/s)
      ├── acceleration ← ivme (m/s²)
      └── jerk         ← ivme değişim speed

"""

#------------ ros2 lib
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge
from rclpy.qos import QoSProfile, ReliabilityPolicy
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy

#------------ autoware lib
from autoware_auto_control_msgs.msg import AckermannControlCommand
from autoware_auto_vehicle_msgs.msg import GearCommand


import sys
import tty
import termios


class ControlNode(Node):
    
    def __init__(self):

        super().__init__("Control_Node")

        qos = QoSProfile(depth=10,reliability=ReliabilityPolicy.RELIABLE,durability=DurabilityPolicy.TRANSIENT_LOCAL)


        self.publisherControl = self.create_publisher(AckermannControlCommand,'/control/command/control_cmd',qos)

        self.gear_pub = self.create_publisher(GearCommand,'/control/command/gear_cmd',qos)

        
        self.gear_timer = self.create_timer(0.1, self.gear_callback)

        self.timer = self.create_timer(0.05,self.timer_callback)

        self.speed = 0.0

        self.steering = 0.0

        self.get_logger().info("control node's been started...")

        self.get_logger().info('W: ileri | S: yavaşla | A: sol | D: sağ | Q: dur')

    def get_key(self):
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            key = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
        return key
    
    def gear_callback(self):
        gear_msg = GearCommand()
        gear_msg.stamp = self.get_clock().now().to_msg()
        if self.speed >= 0:
            gear_msg.command = GearCommand.DRIVE
        else:
            gear_msg.command = GearCommand.REVERSE
        self.gear_pub.publish(gear_msg)

    def timer_callback(self):
        key = self.get_key()

        if key == 'w':
            self.speed = min(self.speed + 0.05, 1.0)
        elif key == 's':
            self.speed = max(self.speed - 0.5, -5.0)
        elif key == 'd':
            self.steering = max(self.steering - 0.05, -0.3)
        elif key == 'a':
            self.steering = min(self.steering + 0.05, 0.3)
        elif key == 'q':
            self.speed = 0.0
            self.steering = 0.0
        elif key == '\x03':  # Ctrl+C
            raise KeyboardInterrupt

        msg = AckermannControlCommand()
        msg.stamp = self.get_clock().now().to_msg()
        msg.longitudinal.speed = self.speed
        msg.longitudinal.acceleration = 1.0
        msg.lateral.steering_tire_angle = self.steering
        self.publisherControl.publish(msg)


def main(args=None):

    rclpy.init(args=args)

    control_node = ControlNode()

    rclpy.spin(node=control_node)

    rclpy.shutdown()



if __name__ == "__main__":
    main()