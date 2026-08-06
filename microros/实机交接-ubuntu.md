# micro-ROS 实机交接文档（Ubuntu 执行）

> **给 Ubuntu 环境的 Claude 的交接说明。** 在 Ubuntu 真机环境（有 micro-ROS + ROS2 Humble）完成 LEAP 小车实机落地。
> 本文档从 Windows 侧交接，目标：实机到手后按此执行。

## 📌 交接背景

- **实机**：LEAP ROS2 小车（已购，待收货）
- **上位机**：Ubuntu 22.04 + ROS2 Humble（已有 micro-ROS）
- **Windows 侧已准备**：`capabilities/vision/detector.py`（YOLO 检测器，已用钢珠模型验证）
- **研究已完成**：`docs/01-07`（实机架构/启动/导航/视觉/三任务）

## 🎯 阶段 1：micro-ROS 基础通信（实机到手第一步）

### 目标
ESP32（leap_low）通过 micro-ROS 与上位机通信，跑通 `/odom` `/imu` `/scan` 话题。

### 具体步骤
```bash
# 1. 启动 micro-ROS Agent（udp4:8888，连接 ESP32）
source /opt/ros/humble/setup.bash
ros2 run micro_ros_agent micro_ros_agent udp4 --port 8888

# 2. 编译并启动 xuegeros_ws（LEAP 源码，含运动/雷达/建图/导航）
cd ~/xuegeros_ws
colcon build --symlink-install
source install/setup.bash

# 3. 验证通信（应看到话题）
ros2 topic list | grep -E "odom|imu|scan"
ros2 topic echo /odom --once   # 应有数据
```

### 验证标准
- [ ] `ros2 topic list` 出现 /odom /imu /scan
- [ ] `/scan` 有激光数据（雷达 → 虚拟串口 /dev/lidar）
- [ ] `/cmd_vel` 能控制电机（`ros2 topic pub /cmd_vel ...` 小车应移动）

### 常见问题
| 问题 | 解决 |
|---|---|
| Agent 无连接 | 确认 ESP32 通电 + 手机热点网络通（UDP 8888）|
| 雷达无数据 | socat：`socat udp:8889 /dev/lidar` 后启动 YDLIDAR 驱动 |
| 话题无/odom | 确认 xuegecar_bringup 启动 + micro-ROS 通信正常 |

## 🎯 阶段 2a：仿真先行验证（真机前必做）

> **在 TurtleBot3 仿真里先跑通导航闭环**，再上真机。环境已在 WSL/Ubuntu 验证可用（Gazebo 11 + turtlebot3_simulations + Nav2 均安装，Gazebo 世界启动成功）。

```bash
# 1. 启动仿真世界（验证 Gazebo + 小车）
export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py

# 2. 建图（终端2）
ros2 launch turtlebot3_cartographer cartographer.launch.py use_sim_time:=True

# 3. 遥控走一圈（终端3）
ros2 run turtlebot3_teleop turtlebot3_teleop_key

# 4. 保存地图
mkdir -p ~/map
ros2 run nav2_map_server map_saver_cli -f ~/map/room

# 5. Nav2 导航（终端4）
ros2 launch turtlebot3_navigation2 navigation2.launch.py map:=~/map/room.yaml
# RViz 设 2D Goal Pose → 小车自主导航
```

**仿真验证标准**：地图轮廓正确 + 小车到达目标点。通过后再走真机路径（阶段2b）。

## 🎯 阶段 2b：实机建图导航（真机到手后）

> 用 LEAP 实机（xuegeros_ws 源码），流程与仿真同构。

```bash
# 1. Cartographer 建图
ros2 launch xuegecar_cartographer cartographer.launch.py

# 2. 遥控走一圈（或用 auto_explore.py 自动）
ros2 run xuegeros_demo teleop  # 或启动 GUI 遥控

# 3. 保存地图
ros2 run nav2_map_server map_saver_cli -f ~/map/room

# 4. Nav2 导航
ros2 launch xuegecar_navigation2 navigation2.launch.py map:=~/map/room.yaml
```

### 验证标准
- [ ] 地图正确（RViz 显示房间轮廓）
- [ ] 设置目标点后小车自主导航到达

## 🎯 阶段 3：目标巡检（串联三能力）

用 Windows 侧已准备的 `detector.py` + ROS2 桥接，实现"导航→检测确认→报告"：

```bash
# 摄像头 MJPEG 流 → YOLO 检测（conda dl 环境）
python capabilities/vision/detector.py \
    --mjpeg http://<ESP32摄像头IP>:8080/?action=stream \
    --model /path/to/best.pt

# 检测结果 → 导航决策（巡检任务逻辑）
```

### 三任务递进
1. **室内目标巡检**：建图→指令→导航→YOLO确认→报告
2. **自主避障巡逻**：自主巡逻→动态避障→异常检测
3. **语音指令控制**：语音→VLA理解→导航→检测

## 📁 已准备的能力（Windows 侧）

| 能力 | 位置 | 状态 |
|---|---|---|
| YOLO 检测器 | `capabilities/vision/detector.py` | ✅ 已用钢珠模型验证 |
| micro-ROS 知识 | `microros/docs/01-04` | ✅ 研究完成 |
| 实机架构 | `docs/01-07` | ✅ 研究完成 |

## ✅ 完成后回传

- 实机通信截图（/odom /scan 数据）
- 建图结果（room.pgm）
- 导航/检测效果图
- 遇到的问题与解决（更新本文档）
