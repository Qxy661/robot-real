# 实机小车 · LEAP ROS2 真机项目 🤖

> 基于 LEAP ROS2 开源小车（已购实机）的真机落地项目。
> **从仿真到真机**——把 M2 检测、M5 导航、M6 控制、micro-ROS 底层在真实机器人上体现。
> 价值：完整闭环（感知→规划→执行→决策）在真机跑通。

## 🎯 三任务递进（作品集核心）

```
能做事（IDEA 1 巡检）→ 会自主（IDEA 2 巡逻）→ 懂人话（IDEA 3 语音）
```

| 任务 | 内容 | 串联能力 | 状态 |
|---|---|---|---|
| **1. 室内目标巡检** | 建图→指令→导航→YOLO确认→报告 | 建图/导航/检测/决策 | 🔄 规划 |
| **2. 自主避障巡逻** | 自主巡逻→动态避障→异常检测→报告 | 导航/避障/检测/控制 | ⏳ |
| **3. 语音指令控制** | 语音→VLA理解→导航→检测 | VLA/导航/检测/交互 | ⏳ |

## 📂 项目结构

```
robot-real/
├── README.md              # 门面（三任务 + 能力）
├── mission/               # 三任务（递进）
│   ├── 01_target_inspection/   # 室内目标巡检
│   ├── 02_patrol_avoidance/    # 自主避障巡逻
│   └── 03_voice_command/       # 语音指令控制
├── capabilities/          # 能力模块（任务基础）
│   ├── slam/              # 建图定位
│   ├── navigation/        # 导航避障
│   ├── vision/            # YOLO 检测
│   ├── control/           # micro-ROS 控制
│   └── interaction/       # 语音交互（ASR/TTS/VLA）
├── gui/                   # GUI 仪表盘（实时视频/标注/传感器）
├── microros/              # micro-ROS 知识体系
├── multi_robot/           # 多机协同（扩展）
└── docs/                  # 实机部署教程
```

## 🏆 实机能力（已研究确认）

```
感知：激光雷达(SLAM) + 摄像头(MJPEG→PC YOLO) + IMU
执行：电机 + 编码器 + PID
通信：micro-ROS(ESP32↔PC) + WiFi MJPEG(图像)
上层：PC 跑 ROS2（导航/视觉/规划/决策/语音）
```

## 🚀 实机操作路径

```
1. 熟悉 LEAP（固件/协议）
2. 跑通 micro-ROS（Agent↔Client）
3. 实机 YOLO 检测（摄像头流）
4. 实机 SLAM 导航（激光雷达）
5. IDEA 1 巡检 → IDEA 2 巡逻 → IDEA 3 语音
6. GUI 仪表盘（整合展示）
```

## 🔗 与主线融合

```
M2 检测 → 实机 YOLO（找目标）
M3 VLA → 语音指令理解（听指挥）
M5 导航 → 实机 Nav2（行动）
M6 控制 → micro-ROS（执行）
```

## 🙏 开源贡献致谢（参考文献）

本项目基于以下开源项目构建，在此衷心致谢原作者的贡献：

### 1. LEAP_ROS 开源机器人
- **作者**：出云科技（czu963889306-dev）
- **仓库**：[czu963889306-dev/-ros2-](https://github.com/czu963889306-dev/-ros2-)
- **贡献**：ESP32 micro-ROS 控制板固件、ROS2 上位机栈（导航/SLAM/摄像头）、硬件设计（原理图/BOM/3D外壳）
- **用途**：本项目实机小车的基础平台

### 2. ROS2 Web 中控台（ros2_web）
- **作者**：czu963889306-dev
- **仓库**：[czu963889306-dev/ros2_web](https://github.com/czu963889306-dev/ros2_web)
- **贡献**：Vue Web 机器人中控台（地图显示/摇杆控制/建图管理/Foxglove 桥接）
- **用途**：本项目的 Web 控制界面

### 3. 相关开源生态
- **micro-ROS**：嵌入式 ROS2 轻量化方案（[micro.ros.org](https://micro.ros.org)）
- **ROS2 Humble** + **Nav2** + **Cartographer**：机器人的标准框架

> 本项目的三任务（巡检/巡逻/语音）与 YOLO/VLA 扩展，是基于上述开源平台的**二次开发与创新**，所有成果回馈开源社区。

## License

MIT

