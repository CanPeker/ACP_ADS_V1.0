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

    """
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
    """

    def timer_callback(self):
        key = self.get_key()

        # Vites geçişi
        if key == '1':
            self.gear = "D"
            self.speed = 0.0
            self.get_logger().info('Vites: DRIVE')
        elif key == '2':
            self.gear = "N"
            self.speed = 0.0
            self.get_logger().info('Vites: NEUTRAL')
        elif key == '3':
            self.gear = "R"
            self.speed = 0.0
            self.get_logger().info('Vites: REVERSE')

        # Hareket kontrolü
        elif key == 'w':
            if self.gear == "D":
                self.speed = min(self.speed + 0.5, 1.36)
            elif self.gear == "R":
                self.speed = min(self.speed + 0.3, 1.0)
            # Neutral'da W çalışmaz

        elif key == 's':
            # Fren — her viteste çalışır
            self.brake = min(self.brake + 2.0, 10.0)
            self.speed = max(self.speed - 1.5, 0.0)

        elif key == 'b':
            # Acil fren
            self.brake = 10.0
            self.speed = 0.0

        elif key == 'a':
            self.steering = min(self.steering + 0.05, 0.15)

        elif key == 'd':
            self.steering = max(self.steering - 0.05, -0.15)

        elif key == 'q':
            self.speed = 0.0
            self.steering = 0.0
            self.brake = 0.0
            self.gear = "N"

        # Fren zamanla azalsın (W basılınca)
        if key == 'w':
            self.brake = max(self.brake - 1.0, 0.0)

        # Mesaj oluştur
        msg = AckermannControlCommand()
        msg.stamp = self.get_clock().now().to_msg()
        msg.lateral.steering_tire_angle = self.steering

        if self.gear == "N":
            msg.longitudinal.speed = 0.0
            msg.longitudinal.acceleration = 0.0
        elif self.gear == "D":
            msg.longitudinal.speed = self.speed
            msg.longitudinal.acceleration = -self.brake if self.brake > 0 else 1.0
        elif self.gear == "R":
            msg.longitudinal.speed = self.speed
            msg.longitudinal.acceleration = -self.brake if self.brake > 0 else 0.5

        self.publisher.publish(msg)

        # Gear publish
        gear_msg = GearCommand()
        gear_msg.stamp = self.get_clock().now().to_msg()
        if self.gear == "D":
            gear_msg.command = GearCommand.DRIVE
        elif self.gear == "N":
            gear_msg.command = GearCommand.NEUTRAL
        elif self.gear == "R":
            gear_msg.command = GearCommand.REVERSE
        self.gear_pub.publish(gear_msg)

        self.get_logger().info(
            f'Vites: {self.gear} | Hız: {self.speed*3.6:.0f} km/h | '
            f'Fren: {self.brake:.1f} | Direksiyon: {self.steering:.2f}')

def main(args=None):

    rclpy.init(args=args)

    control_node = ControlNode()

    rclpy.spin(node=control_node)

    rclpy.shutdown()



if __name__ == "__main__":
    main()