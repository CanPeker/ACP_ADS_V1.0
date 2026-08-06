# ACP_ADS — Vision-Based ADAS Perception Stack

> A hobby-built, camera-first Advanced Driver Assistance System.
> **V1.0** delivers real-time object detection and lane detection running on ROS 2, fed by a simulated sensor source.

![version](https://img.shields.io/badge/version-1.0-blue)
![ros](https://img.shields.io/badge/ROS2-Humble-22314E)
![python](https://img.shields.io/badge/python-3.10-3776AB)

---

## What is this

ACP_ADS is a personal project that builds a **camera-based perception pipeline** for driver assistance — the kind of processing that sits behind features like lane-departure alerts and forward-collision warnings.

V1.0 focuses on the **perception layer only**: detecting objects and lane lines from camera frames, then publishing structured outputs that downstream systems can consume.

```
Camera frames  →  Object Detection (YOLOv8)
               →  Lane Detection (UFLD + Kalman Filter)
```

No warnings, no vehicle control — just clean, reliable perception outputs. The warning layer comes in V1.5.

---

## Architecture

```
              ┌───────────────┐
              │     AWSIM     │   virtual camera source
              └───────┬───────┘
                      │
                      │  /sensing/camera/traffic_light/image_raw
                      │
           ┌──────────┴──────────┐
           ▼                     ▼
    ┌─────────────┐      ┌─────────────┐
    │  yolo_node  │      │  lane_node  │
    │  (YOLOv8)   │      │(UFLD + KF)  │
    └──────┬──────┘      └──┬──────┬───┘
           │                │      │
           ▼                ▼      ▼
  /Perception/          /Perception/   /Perception/
  Object_Detection/     Lane/          Lane/
  yolo_detected_images  detected_frames filtered_pos
```

Both nodes subscribe to the same camera topic independently and publish their own outputs. This keeps them decoupled — either node can run standalone.

> **Note on AWSIM:** It is used purely as a virtual sensor source (camera frames) during development. The perception nodes are simulator-agnostic and can be pointed at any camera topic.

---

## Packages

```
ACP_ADS_V1.0/
└── src/
    ├── perception_layer/        # perception nodes + models
    │   ├── perception_layer/
    │   │   ├── yolo_node.py
    │   │   ├── laneDetectorNode.py
    │   │   ├── ultrafastLaneDetector.py
    │   │   ├── model.py
    │   │   └── backbone.py
    │   ├── dnn/
    │   │   └── yolov8n.pt
    │   ├── config/
    │   │   └── perception.yaml
    │   ├── launch/
    │   │   └── perception.launch.py
    │   └── package.xml
    │
    ├── acp_ads_interfaces/      # custom message definitions
    │   └── msg/
    │       └── LaneRawData.msg
    │
    └── system_launch/           # top-level launch
        └── launch/
            └── full_system.launch.py
```

---

## Nodes

### `yolo_node`

Real-time object detection using YOLOv8.

| | |
|---|---|
| **Subscribes** | `/sensing/camera/traffic_light/image_raw` (sensor_msgs/Image) |
| **Publishes** | `/Perception/Object_Detection/yolo_detected_images` (sensor_msgs/Image) |
| **Model** | YOLOv8n (COCO — person, bicycle, car, motorcycle, bus, truck) |
| **QoS** | BEST_EFFORT, depth 10 |

### `lane_node`

Lane line detection using Ultra-Fast Lane Detection with Kalman filtering on lane positions.

| | |
|---|---|
| **Subscribes** | `/sensing/camera/traffic_light/image_raw` (sensor_msgs/Image) |
| **Publishes** | `/Perception/Lane/detected_frames` (sensor_msgs/Image) |
| | `/Perception/Lane/filtered_pos` (acp_ads_interfaces/LaneRawData) |
| **Model** | UFLD (TuSimple, ResNet-18 backbone) |
| **Filtering** | Per-lane Kalman filter on lower-quarter x-coordinates |
| **QoS** | BEST_EFFORT, depth 10 |

---

## Custom Messages

### `LaneRawData.msg`

```
std_msgs/Header header
float32[] positions
```

Contains Kalman-filtered x-positions for up to 4 detected lanes.

---

## Tech Stack

| Component | Technology |
|---|---|
| OS | Ubuntu 22.04 |
| Middleware | ROS 2 Humble |
| Sensor Source | AWSIM v1.2.0 (TIER IV) |
| Object Detection | YOLOv8n (Ultralytics) |
| Lane Detection | Ultra-Fast Lane Detection (TuSimple) |
| Filtering | Kalman Filter (filterpy) |
| Language | Python 3.10 |

---

## Getting Started

### Prerequisites

- Ubuntu 22.04
- ROS 2 Humble
- AWSIM v1.2.0
- Python 3.10 with pip

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/CanPeker/ACP_ADS_V1.0.git
cd ACP_ADS_V1.0

# 2. Install Python dependencies
pip install ultralytics filterpy opencv-python torch torchvision scipy

# 3. Source ROS 2 and build
source /opt/ros/humble/setup.bash
colcon build
source install/setup.bash
```

### Running

```bash
# Terminal 1: Start AWSIM
# (follow AWSIM launch instructions)

# Terminal 2: Launch perception pipeline
source install/setup.bash
ros2 launch system_launch full_system.launch.py

# Or run nodes individually:
ros2 run perception_layer yolo_node
ros2 run perception_layer lane_node
```

### Verify

```bash
# Check active topics
ros2 topic list

# View detection output
ros2 topic echo /Perception/Object_Detection/yolo_detected_images --no-arr
ros2 topic echo /Perception/Lane/filtered_pos
```

---

## Configuration

Node parameters are loaded from `config/perception.yaml`:

```yaml
yolo_node:
  ros__parameters:
    model_path: ""               # defaults to package share/dnn/yolov8n.pt
    confidence_threshold: 0.5
    input_topic: "/sensing/camera/traffic_light/image_raw"

lane_node:
  ros__parameters:
    model_path: ""               # defaults to package share tusimple_18.pth
    use_gpu: true
    input_topic: "/sensing/camera/traffic_light/image_raw"
```

---

## Demo

> _Demo GIF / video coming soon._

<!--
![demo](docs/demo.gif)
-->

---

## Roadmap

### V1.5 — Alert Layer *(under development)*

V1.0 provides perception outputs. V1.5 adds an **`alert_layer`** package that consumes these outputs and generates driver warnings:

- **Lane Departure Warning (LDW):** Compares vehicle position against Kalman-filtered lane boundaries from `lane_node`. Triggers when the vehicle drifts toward a lane edge.
- **Forward Collision Warning (FCW):** Uses object detections from `yolo_node` with distance estimation to warn about imminent collision risks.

```
perception_layer (V1.0)          alert_layer (V1.5)
┌─────────────┐                ┌──────────────┐
│  yolo_node  │ ──detections──►│   fcw_node   │──► collision warning
└─────────────┘                └──────────────┘
┌─────────────┐                ┌──────────────┐
│  lane_node  │ ──lane pos────►│   ldw_node   │──► lane departure warning
└─────────────┘                └──────────────┘
```

### Future

- Multi-object tracking (ByteTrack)
- HMI dashboard for unified visualization
- C++ rewrite for production-grade performance (V2.0)
- LiDAR integration and sensor fusion

---

## Design Principles

- **Perception first.** Build reliable detection before adding decision layers.
- **Simulator is just a sensor.** AWSIM feeds frames; the stack stays simulator-agnostic.
- **Single-responsibility nodes.** Each node has one job and a clean topic contract.
- **Decoupled layers.** Perception publishes, alert layer subscribes — no tight coupling.

---

## Author

**Atılay Can Peker**

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

*This is a personal learning project and is not intended for use in real vehicles. It provides no safety guarantees.*
