# 实机小车 · LEAP ROS2 真机项目 🤖

> 基于 LEAP ROS2 开源小车（已购实机）的真机落地项目。
> 把 M2 检测、M5 导航、M6 控制、micro-ROS 底层在**真实机器人**上体现。
> 价值：从"仿真"到"真机"的完整闭环（作品集最强信号）。

## 🎯 三个 IDEA（按序实施）

| IDEA | 内容 | 串联能力 | 状态 |
|---|---|---|---|
| **1. 语音指挥小车** | 语音→ASR→VLA理解→执行→TTS反馈 | M2/M3/M5/底层 | 🔄 规划 |
| **2. 多能力矩阵** | 实机YOLO/导航/micro-ROS/PID + 对比 | M2/M5/M6 | ⏳ |
| **3. 多机协同** | Agent池，PC一控多 | micro-ROS进阶 | ⏳ |

## 🏆 实机能力（已研究确认）

```
感知：激光雷达(SLAM) + 摄像头(MJPEG→PC YOLO) + IMU
执行：电机 + 编码器 + PID
通信：micro-ROS(ESP32↔PC) + WiFi MJPEG(图像)
上层：PC 跑 ROS2（导航/视觉/规划/决策）
```

## 📂 项目结构

```
robot-real/
├── README.md              # 本文件（门面）
├── voice_command/         # IDEA 1：语音指挥小车
│   ├── asr/               # 语音识别
│   ├── vla/               # VLA 指令理解
│   ├── execute/           # 任务执行
│   └── tts/               # 语音反馈
├── capabilities/          # IDEA 2：多能力矩阵
│   ├── vision/            # 实机 YOLO
│   ├── navigation/        # 实机导航
│   └── control/           # PID 控制
├── multi_robot/           # IDEA 3：多机协同
├── microros/              # micro-ROS 知识体系（完成）
└── docs/                  # 实机部署教程
```

## 🚀 实机操作路径

```
1. 熟悉 LEAP（固件/协议/飞书文档）
2. 跑通 micro-ROS（Agent↔Client）
3. 实机 YOLO 检测（摄像头流）
4. 实机 SLAM 导航（激光雷达）
5. IDEA 1：语音指挥小车（端到端）
6. IDEA 2：多能力矩阵
7. IDEA 3：多机协同
```

## 🔗 与主线融合

```
M2 检测 → 实机 YOLO
M3 VLA → 语音指令理解
M5 导航 → 实机 Nav2
M6 控制 → micro-ROS 执行
```

## License

MIT
