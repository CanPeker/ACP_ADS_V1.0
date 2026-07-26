# ACP_ADS — Vision-Based Level-2 ADAS

> A hobby-built, camera-first Advanced Driver Assistance System.
> **V1.0** delivers a working perception + lane-departure-warning chain running on ROS 2, fed by a simulated sensor source.

![status](https://img.shields.io/badge/version-1.0-blue)
![ros](https://img.shields.io/badge/ROS2-Humble-22314E)
![python](https://img.shields.io/badge/python-3.10-3776AB)
![level](https://img.shields.io/badge/ADAS-Level%202%20(warning)-orange)

---

## What is this

ACP_ADS is a personal project to build the **warning-level (Level 2) driver assistance stack** you'd find behind features like lane-departure and forward-collision alerts — but from scratch, with lightweight custom ROS 2 nodes instead of a full autonomy framework.

The design goal is deliberate: **the system only warns, it never actuates.** No steering, throttle, or brake control. This keeps the scope honest for a hobby build and mirrors how real aftermarket Level-2 warning systems behave.

**V1.0 scope** is the first vertical slice — camera in, warning out:

```
Camera frames  →  Perception  →  Lane Departure Warning
```

---

## Architecture

The system is organized into layers, each node holding a single responsibility with defined topic inputs/outputs.

| Layer | Node | Responsibility |
|---|---|---|
| **L1 · Sensing** | *(AWSIM)* | Provides camera frames + vehicle status (virtual sensor source) |
| **L2 · Perception** | `yolo_node` | YOLOv8 object detection on incoming frames |
| | `lane_node` | UFLD lane-line detection |
| **L3 · Warning** | `ldw_node` | Lane Departure Warning from lane geometry |

> **Note on AWSIM:** It is used purely as a *virtual sensor input source* (camera frames + vehicle status) during development — **not** as an Autoware full-stack host. This keeps the perception/warning layers independent of the simulator, so the same nodes can later be pointed at a real camera without rewriting the stack.

### Data flow (V1.0)

```
        ┌──────────────┐
        │    AWSIM      │   virtual camera + vehicle status
        └──────┬───────┘
               │ image topic
       ┌───────┴────────┐
       ▼                ▼
 ┌───────────┐   ┌────────────┐
 │ yolo_node │   │ lane_node  │
 │ (YOLOv8)  │   │  (UFLD)    │
 └───────────┘   └─────┬──────┘
                       │ lane geometry
                       ▼
                 ┌───────────┐
                 │ ldw_node  │  → lane departure warning
                 └───────────┘
```

---

## Tech stack

- **OS:** Ubuntu 22.04
- **Middleware:** ROS 2 Humble
- **Simulator / sensor source:** AWSIM v1.2.0 (TIER IV)
- **Perception:** YOLOv8 (object detection), UFLD (Ultra-Fast Lane Detection)
- **Language:** Python 3.10

---

## Nodes

### `yolo_node`
Runs YOLOv8 inference on incoming camera frames and publishes detected objects (class, bounding box, confidence).

### `lane_node`
Runs UFLD lane detection and publishes lane-line geometry for downstream consumers.

### `ldw_node`
Consumes lane geometry and raises a **Lane Departure Warning** when the vehicle drifts across a lane boundary.

---

## Getting started

> Requires Ubuntu 22.04 with ROS 2 Humble and AWSIM v1.2.0 installed.

```bash
# 1. Source ROS 2
source /opt/ros/humble/setup.bash

# 2. Build the workspace
colcon build
source install/setup.bash

# 3. Launch AWSIM (virtual sensor source), then in a new terminal:
ros2 topic list        # confirm camera + vehicle status topics are visible

# 4. Run the nodes
ros2 run <pkg> yolo_node
ros2 run <pkg> lane_node
ros2 run <pkg> ldw_node
```

> Replace `<pkg>` with your package name. Launch-file support is planned (see Roadmap).

---

## Demo

> _Demo GIF / video coming soon._

<!--
![demo](docs/demo.gif)
-->

---

## Roadmap

V1.0 is the first working vertical slice. Planned direction:

- **Perception stability** — Kalman filtering on lane output, custom ROS 2 message definitions
- **Collision warning** — ByteTrack object tracking + Forward Collision Warning (TTC-based)
- **Dashboard** — HMI layer visualizing all perception + warning outputs on one screen
- **Expansion** — pedestrian warning, speed warning, LiDAR + sensor fusion

---

## Design principles

- **Warn, don't actuate.** Level-2 warning scope only.
- **Simulator is just a sensor.** AWSIM feeds frames; the stack stays simulator-agnostic.
- **Single-responsibility nodes.** Each node has one job and a clean topic contract.
- **Lightweight over full-stack.** Custom nodes instead of Autoware, matched to the Level-2 goal.

---

## Author

**Atılay Can Peker** — hobby ADAS build on a 2009 Mitsubishi Colt 1.3.

---

*This is a personal learning project and is not intended for use in real vehicles. It provides no safety guarantees.*
