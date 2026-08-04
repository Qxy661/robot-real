# micro-ROS · 嵌入式 ROS2 轻量化部署 🤖

> 让单片机（ESP32）跑 ROS2 的轻量方案。
> **轻量化部署 + 减重 + PC 统一调控**——多机协同的核心技术。
> 基于 LEAP ROS2 小车（已购实机）。

## 🎯 核心价值

```
轻量化部署：ESP32(12KB) vs 完整ROS2(200KB)
多机协同：一台 PC 调控多台机器人（一控多）
PC 统一调控：PC 大脑 + 嵌入式执行分工
```

## 🏆 学习价值（调研确认）

| 维度 | 价值 |
|---|---|
| **就业** | 2025 真实岗位要求 microROS 通讯整合能力 |
| **趋势** | 机器人热门，嵌入式 ROS 需求扩大 |
| **复合技能** | ROS2 + DDS + FreeRTOS + MCU 驱动 |
| **差异化** | 嵌入式+机器人交叉，区分度高 |

## 📂 项目结构

```
microros/
├── README.md          # 本文件
├── docs/              # 知识概念
│   ├── 01-micro-ROS架构
│   ├── 02-Client-Agent原理
│   ├── 03-DDS-XRCE协议
│   └── 04-多机协同
├── firmware/          # ESP32 micro-ROS 固件分析（LEAP）
├── agent/             # micro-ROS Agent 配置
├── examples/          # 实机示例（话题/传感器）
├── multi_robot/       # 多机协同（Agent 池）
└── results/           # 实机演示
```

## 🚀 实机操作路径

```
1. Client-Agent 架构理解（docs/）
2. 跑通 LEAP micro-ROS（Agent↔Client 通信）
3. 修改固件（加话题/传感器）
4. 扩展多机（多 ESP32 + Agent 池）
5. 科研方向（实时性/资源优化/多机协同）
```

## 🔗 与主线融合

```
M6 控制 → 实机 micro-ROS（ESP32 执行）
多机协同 → Agent 池（一控多）
轻量化 → 理解"PC大脑+嵌入式执行"
```

## License

MIT
