# 02 · micro-ROS Client-Agent 原理

> 理解 micro-ROS 的核心架构：Client 和 Agent 如何配合。

## 一、Client（薄客户端）

**运行在 ESP32**，只做两件事：
1. **序列化数据**：把数据打包（不处理复杂逻辑）
2. **发指令**：创建节点/发布消息/订阅

**为什么"薄"**：复杂逻辑（发现/匹配/QoS）都交给 Agent，Client 只传数据。

```
Client 职责：
  - 创建节点/话题
  - 发布/订阅消息
  - 调用服务
  （都是"传数据"，不参与 DDS 复杂机制）
```

## 二、Agent（桥）

**运行在 PC/容器**，做复杂的事：
1. **发现/匹配**：找到其他 ROS2 节点
2. **QoS 管理**：消息质量服务
3. **桥接 DDS**：把 Client 数据接入 ROS2 网络

```
Agent 职责：
  - 接入 ROS2 DDS 域
  - 代表 Client 参与通信
  - 管理连接/心跳
```

## 三、通信流程

```
1. Client 启动 → 连接 Agent（UART/WiFi UDP）
2. Client 创建节点 → Agent 注册到 ROS2
3. Client 发布数据 → Agent 转发到 ROS2 话题
4. ROS2 发布指令 → Agent 转发给 Client
5. Client 执行（电机/传感器）
```

## 四、传输方式

| 方式 | 特点 | 适用 |
|---|---|---|
| **UART/Serial** | 确定性、实时、零配置 | 底层控制 |
| **WiFi UDP** | 灵活、多节点、<15ms | 无线（LEAP）|

## 五、LEAP 的实际通信

```
PC（micro-ROS Agent）
  ↓ WiFi/UDP
ESP32（Client）
  /cmd_vel → motion_msg → 电机
  /scan ← lidar_msg ← 激光雷达
```

## 六、为什么分层重要

1. **资源受限**：Client 只传数据（省内存）
2. **解耦**：换中间件不用改应用
3. **多机**：一个 Agent 可管多 Client

## 探究练习

1. 为什么 Client 要"薄"（不处理 DDS 逻辑）？
2. Agent 崩溃会发生什么？
3. UART 和 WiFi 各自适合什么场景？

---
*下一章：03-DDS-XRCE 协议*
