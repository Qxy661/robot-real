# 01 · micro-ROS 架构

> micro-ROS：让单片机（ESP32）跑 ROS2 的轻量方案。
> 轻量化部署 + 减重 + PC 统一调控。

## 一、问题：ROS2 不能跑在单片机

完整 ROS2 需要 Linux + 大内存 + 算力，不能跑在 ESP32/STM32。

但机器人底层全是单片机（电机/传感器）。
**需求**：让单片机成为 ROS2 节点。

## 二、方案：Client-Agent 架构

```
PC/上位机（重量级 ROS2）
    ↓ micro-ROS Agent（桥）
    ↓ DDS-XRCE 协议
ESP32（micro-ROS Client）
```

| 角色 | 运行 | 职责 |
|---|---|---|
| **Client** | ESP32 | 薄客户端：序列化数据 + 发指令 |
| **Agent** | PC/容器 | 桥接：接入 ROS2 DDS 网络 |

## 三、关键技术

### DDS-XRCE 协议
- 把 ROS2 的 DDS 发现模型 → 客户端-服务器模型
- 适配资源受限单片机（心跳保活）

### RMW 抽象层
- 可切换中间件（Micro XRCE ~12KB vs Cyclone ~25KB）
- 无需改应用代码

## 四、资源对比

| 项 | 完整 ROS2 | micro-ROS |
|---|---|---|
| 内存 | >200KB | **~12KB** |
| 平台 | Linux | 单片机裸机 |
| 成本 | 电脑/树莓派 | **ESP32（¥10）** |
| 话题 | 无限 | 8-12 个 |

## 五、三层架构

```
应用层（RCL/RCLC）：话题/服务/节点
Client 库：micro-ROS Client
通信层（DDS-XRCE）：Micro XRCE-DDS
```

## 六、LEAP 的实践（固件确认）

```cpp
WifiCommMode g_wifi_comm_mode = kMicroRos;  // 默认 micro-ROS
g_microros_agent_ip = "192.168.31.214";     // Agent
g_microros_agent_port = 8888;
// FreeRTOS 队列：任务间通信
```

## 七、为什么重要

1. **轻量化**：低成本 MCU 也能接入 ROS2 生态
2. **多机**：多 ESP32 + Agent 池 → 一控多
3. **分工**：PC 大脑 + 嵌入式执行

## 探究练习

1. 为什么完整 ROS2 不能跑在 ESP32？
2. Agent 和 Client 分别承担什么？
3. DDS-XRCE 协议解决了什么问题？

---
*下一章：02-Client-Agent 原理*
