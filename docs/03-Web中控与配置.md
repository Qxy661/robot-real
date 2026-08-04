# 实机 Web 中控与配置（ros2_web）

> 基于 ros2_web 源码研究（2026-08-04）。上位机的 Web 控制界面。

## 一、Web 中控台（Ros_Vue）

**基于 Vue 的机器人中控台**（Web 界面控制 ROS2 小车）。

**核心功能**：
```
实时 SLAM 栅格地图显示
机器人摇杆远程控制
电池电压 + 里程计监测
可视化建图控制（开始/停止）
地图保存（网页输入地图名）
Foxglove WebSocket 连接
```

**架构**：Ros_Vue_arm（ARM 版） / Ros_Vue_x86（x86 版）

## 二、通信（Foxglove WebSocket）

```
Web界面 ←ws://主机:8765→ foxglove_bridge → ROS2 话题
```

**foxglove_bridge 参数**（高带宽）：
```
include_hidden: true
send_buffer_limit: 100000000
num_threads: 4
max_qos_depth: 10
```

## 三、任务配置（ros_config.json）

| 任务 | 说明 |
|---|---|
| **foxglove** | 数据桥接（WebSocket）|
| **mapCartographer** | Cartographer 建图 |
| **nav2** | Nav2 导航（AMCL + 规划）|
| **保存地图** | map_saver |

## 四、启动流程（start_console.sh）

```bash
# 1. 加载 Node.js 环境（NVM）
# 2. 启动后端（server.js）
# 3. 启动前端（Vue dev/prod）
# 4. ros_config.json 配置的任务可一键启动
```

## 五、完整实机操作流程（整合）

```
1. 硬件检查（电池/接线/轮子/雷达）
2. 导入虚拟机（Ubuntu 22.04 / ROS2 Humble）
3. 确认出厂固件（ESP32 micro-ROS）
4. Web 后台配置 WiFi/通信参数
5. 启动中控台（start_console.sh）
6. micro-ROS 通信测试（/odom /imu /scan）
7. 激光建图（Cartographer/Gmapping）
8. 保存地图
9. Nav2 导航（加载地图 → 设初始位姿 → 目标点）
```

## 六、四层架构（手册确认）

```
硬件层：电机/编码器/IMU/雷达/控制板
固件层：ESP32 micro-ROS 固件
ROS2 通信层：Micro-ROS Agent
应用层：RViz2/SLAM/Nav2/Web中控
```

## 七、硬件规格（手册确认）

| 项 | 规格 |
|---|---|
| 主控 | ESP32-S3（双核，WiFi+蓝牙）|
| 电机 | TT 减速电机（9V/150RPM/1:90，带编码器）|
| 激光雷达 | Camsense D2（三角测距，串口115200）|
| IMU | 六轴（板载）|
| 上位机 | 虚拟机（Ubuntu 22.04 / ROS2 Humble）|

## 八、我们要加的（三任务）

```
Web 中控已有：建图/导航/地图保存/摇杆
我们要加：
  YOLO 检测（订阅 /camera/image_raw）
  语音/VLA（IDEA 3）
  三任务逻辑（IDEA 1/2）
  → 可集成到 Web 中控或独立节点
```

---
*实机 Web 中控研究。配合飞书手册使用。*
