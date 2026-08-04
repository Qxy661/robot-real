# 03 · DDS-XRCE 协议

> micro-ROS 的通信协议：把 DDS 适配到资源受限单片机。

## 一、背景：DDS 太重

标准 ROS2 用 DDS（Data Distribution Service）：
- 对等发现（peer-to-peer）
- 完整 QoS
- 内存/算力要求高

**问题**：单片机跑不动完整 DDS。

## 二、DDS-XRCE 方案

**XRCE = XRCE（X-Robotics Communication Extension）**

核心思想：**把"对等发现"改为"客户端-服务器"**。

```
标准 DDS：每个节点对等发现（复杂）
DDS-XRCE：Client 连 Agent（简单），Agent 处理发现
```

## 三、协议特点

1. **客户端-服务器模型**
   - Client：传数据（薄）
   - Agent：处理发现/匹配

2. **心跳保活**
   - Client 和 Agent 定期心跳
   - 防止资源泄漏

3. **资源占用小**
   - Micro XRCE-DDS：~12KB RAM
   - 适配 ESP32 等 MCU

## 四、消息流程

```
Client → Agent：
  创建节点/话题 请求
  发布数据 请求
  订阅数据 请求

Agent → Client：
  确认/响应
  转发 ROS2 数据
```

## 五、为什么重要

1. **适配 MCU**：12KB 能跑（vs 完整 DDS 200KB）
2. **可靠**：心跳保活防泄漏
3. **标准**：ROS2 官方支持的嵌入式方案

## 六、RMW 抽象

```
RMW（ROS Middleware Wrapper）：
  可切换 Micro XRCE-DDS（~12KB）或 Cyclone-DDS（~25KB）
  不用改应用代码
```

## 探究练习

1. 为什么标准 DDS 发现机制不适合 MCU？
2. 心跳保活解决了什么问题？
3. RMW 抽象的价值是什么？

---
*下一章：04-多机协同*
