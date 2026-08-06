# 实机落地 · LEAP 履带巡检机器人 🤖

> **从仿真到真机**——把 M2 检测、M5 导航、M6 控制、micro-ROS 底层集成到一台真实履带小车，跑通「感知 → 规划 → 控制 → 执行」完整闭环。

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![ROS2](https://img.shields.io/badge/ROS2-Humble-green.svg)](https://docs.ros.org/en/humble/)
[![micro-ROS](https://img.shields.io/badge/micro--ROS-ESP32S3-orange.svg)](https://micro.ros.org/)
[![Python](https://img.shields.io/badge/Python-3.10-blue.svg)](https://www.python.org/)

---

## 🏗️ 整体项目架构

**能力金字塔 + 三任务主线**，覆盖机器人从底层控制到高层决策的完整链路：

```
        【主线叙事】 能做事（巡检）→ 会自主（巡逻）→ 懂人话（语音）
                                   ▲
┌─────────────────────────────────────────────────────────────┐
│  ④ 系统层：三任务递进 + 自定义中控台        ← 作品集门面      │
├─────────────────────────────────────────────────────────────┤
│  ③ 规划层：手写 DWA/A* 真机 + frontier 探索  ← 差异化王牌      │
├─────────────────────────────────────────────────────────────┤
│  ② 感知层：超声波专项 + 激光 SLAM + YOLO     ← 感知可靠性      │
├─────────────────────────────────────────────────────────────┤
│  ① 控制层：里程计标定 + PID + 航向融合       ← 底层功底        │
└─────────────────────────────────────────────────────────────┘
         ▲ 深化差异化：检测导航闭环 → 手写算法真机 → K230 边缘 AI
```

**四层递进逻辑**：底层功底（控制）→ 感知可靠（感知）→ 会写算法且能部署（规划）→ 全栈整合（系统），每层都有**量化产出**支撑——这是作品集"有质量"的关键。

## 🏆 已完成成果

| 层 | 成果 | 结果 |
|---|---|---|
| 底层 | **micro-ROS 通信** | ESP32-S3 控制板 ↔ PC 跑通（/odom /imu /scan /cmd_vel）|
| 底层 | **控制层脚本 ×3** | 里程计标定 / PID 精确行驶 / IMU+里程计航向融合 |
| 感知 | **YOLO 检测器** | 图片/视频/MJPEG 三输入，钢珠 mAP 0.93 |
| 感知 | **实机建图** | Cartographer 真机建图，229×233 房间地图 |
| 系统 | **四层能力框架** | 能力金字塔 + 三任务设计 + 整体作战地图 |

## 🎯 核心方法论

```
算法理解 → micro-ROS 落地 → 真机验证 → 量化标定 → 三任务整合 → 作品集
  (知识)      (嵌入式)       (落地)     (误差数据)     (闭环)      (展示)
```

- **从仿真到真机** — 把 ROS2 全栈压进 ESP32 控制板 + 上位机协同，真机验证算法落地能力
- **能力分层递进** — 控制→感知→规划→系统，每层都是下一层的地基
- **量化胜于描述** — 误差曲线、对比表、覆盖率，每个结论都有数字撑腰

## 📂 项目结构

```
robot-real/
├── capabilities/          # 能力模块（任务基础）
│   ├── control/           # 控制层：里程计标定/PID精确行驶/IMU航向融合
│   └── vision/            # YOLO 检测器（图片/视频/MJPEG）
├── docs/                  # 实机部署文档（09 篇）
├── microros/              # micro-ROS 知识体系 + 实机交接
├── mission/               # 三任务（巡检→巡逻→语音）
└── multi_robot/           # 多机协同（扩展）
```

## ✅ 已完成详解

### 1. 四层能力金字塔（作品集框架）

实机能力组织为**四个递进层次**，每层带量化产出（误差曲线/对比表/覆盖率曲线），详见 [08-作品集框架·实机能力](docs/08-作品集框架-实机能力.md)。

### 2. micro-ROS 底层（嵌入式 · 差异化）

```
ESP32 控制板 (leap_low_v1)
  ├─ WiFi STA → micro-ROS (UDP 8888) → /odom /imu /cmd_vel
  └─ 激光雷达 → UDP 8889 → PC socat /dev/lidar → /scan
```

控制板 = **Seeed XIAO ESP32-S3**，UART 命令配置 WiFi，知识体系见 [microros/docs/](microros/docs/01-micro-ROS架构.md)。

### 3. 控制层 · 死推算与控制论

> 底层功底：车走不准、停不住、方向歪，上层规划全白搭。三个脚本见 [capabilities/control/README.md](capabilities/control/README.md)：

| 脚本 | 解决什么 | 量化产出 |
|---|---|---|
| **odom_calib.py** | 直行标轮径 + 原地转标轮距 | 误差 → <0.5% 对比 |
| **pid_drive.py** | 位置环+航向环双闭环走 N 米停 | 超调/稳态误差/整定曲线 |
| **heading_fusion.py** | IMU 陀螺高频 + 里程计低频互补 | 融合前后航向误差对比 |

### 4. 感知层 · 视觉 + 激光

- **YOLO 检测器**：`capabilities/vision/detector.py`，三种输入源，输出检测 JSON + 可视化
- **激光 SLAM**：Cartographer 实机建图，为导航提供地图基础

### 5. 三任务设计（作品集门面）

```
能做事（IDEA 1 巡检）→ 会自主（IDEA 2 巡逻）→ 懂人话（IDEA 3 语音）
```

每个任务串联前面全部能力，从"能做事"到"懂人话"递进，详见 [07-三任务设计](docs/07-三任务设计.md)。

## 🗺️ 计划路线

```
基础落地（micro-ROS + 建图导航）→ 控制层量化数据 → 三任务（1→2→3）
   → 深化 C 检测导航闭环 → 深化 B 手写 DWA 真机 → 深化 D K230 边缘 AI
```

**按层逐个击破**，每步一个可验收里程碑，完整执行顺序见 [09-实机项目总览](docs/09-实机项目总览.md)。

## 🚀 快速开始

```bash
# 1. 一键启动（雷达 + micro-ROS + 运动控制）
cd ~/xuegeros_ws && source install/setup.bash
ros2 launch xuegeros_demo bringup_all.launch.py

# 2. 确认通信
ros2 topic echo /odom --once   # 应有位置数据

# 3. 控制层脚本（真机）
cd ~/robot-real/capabilities/control
python3 odom_calib.py --test straight        # 里程计直行标定
python3 pid_drive.py --distance 1.0          # PID 精确走 1 米
python3 heading_fusion.py --duration 30      # IMU+里程计航向融合
```

## 📚 文档导航

| 文档 | 内容 |
|---|---|
| [01-实机架构与启动](docs/01-实机架构与启动.md) | LEAP 上位机栈 + 启动流程 |
| [02-运动与导航配置](docs/02-运动与导航配置.md) | 底盘/雷达/导航配置 |
| [03-Web中控与配置](docs/03-Web中控与配置.md) | ros2_web 中控台 |
| [04-视觉方案-K230](docs/04-视觉方案-K230.md) | 边缘 AI 检测规划 |
| [05-双系统实操计划](docs/05-双系统实操计划.md) | Ubuntu + 手机热点 |
| [06-实施路线规划](docs/06-实施路线规划.md) | 五阶段执行路线 |
| [07-三任务设计](docs/07-三任务设计.md) | 巡检/巡逻/语音递进 |
| [08-作品集框架·实机能力](docs/08-作品集框架-实机能力.md) | 四层能力金字塔 |
| [09-实机项目总览](docs/09-实机项目总览.md) | 整体工作分解作战地图 |
| [控制层能力](capabilities/control/README.md) | 标定/PID/融合脚本 |
| [视觉能力](capabilities/vision/README.md) | YOLO 检测器 |
| [micro-ROS 交接](microros/实机交接-ubuntu.md) | 实机落地执行步骤 |

## License

MIT
