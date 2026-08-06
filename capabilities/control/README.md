# 实机控制层 · 死推算与控制论 🎛️

> 作品集金字塔的最底层：**能控制（死推算/控制论）**。先做，打基础。
> 目标：让底盘"走得准、停得稳、方向不偏"，为规划层（手写 DWA/A*）和系统层（三任务）提供可靠执行底座。

## 能力（按依赖递进）

| 脚本 | 解决什么问题 | 量化产出 |
|---|---|---|
| **odom_calib.py** | 里程计有比例误差（轮径/轮距不匹配真实底盘） | 误差从 X% → <0.5% 对比 |
| **pid_drive.py** | 开环"发固定速度"停不准、走不直 | 超调 / 稳态误差 / 整定曲线 CSV |
| **heading_fusion.py** | 里程计打滑漂移 + IMU 陀螺偏置漂移 | 融合前后航向误差对比 CSV |

## 接口（对齐 LEAP ESP32 micro-ROS）

| 话题 | 类型 | 角色 |
|---|---|---|
| `/cmd_vel` | geometry_msgs/Twist | 发布（本层所有脚本） |
| `/odom` | nav_msgs/Odometry | 订阅（位置/航向反馈） |
| `/imu` | sensor_msgs/Imu | 订阅（heading_fusion 用陀螺） |

## 用法

```bash
# 1. 里程计标定（先做！误差不标，后面全白搭）
python3 odom_calib.py --test straight          # 直行 → 标轮径
python3 odom_calib.py --test rotate            # 原地转 → 标轮距

# 2. PID 精确行驶（走 2 米精确停，保持直线）
python3 pid_drive.py --distance 2.0 --speed 0.3
python3 pid_drive.py --distance 1.5 --kp 0.8 --ki 0.05 --kd 0.1

# 3. IMU+里程计航向融合（先静止 3s 估偏置，再转动记录 30s）
python3 heading_fusion.py --alpha 0.98 --duration 30
```

## 作品集素材（每步都要留）

- **odom_calib**：标定前后两次直行对比（报告值 vs 实测值表）
- **pid_drive**：`pid_drive_data.csv` → matplotlib 画整定曲线（超调/稳态误差标注）
- **heading_fusion**：`heading_fusion_data.csv` → 画 odom/imu/fused 三线对比 + 静止段标准差表

## 踩坑记录（真机回填）

- （待实机）调参顺序：先 P 后 D 再 I；航向环超调优先降 `--yaw-kp`
- （待实机）履带底盘打滑对里程计影响大，PID 目标距离建议 ≤3m
- （待实机）IMU 偏置随温度漂移，每次上电都重新估（脚本已内置静止估计）

## 与深化路线衔接

- **阶段 B（手写 DWA 上真机）**：DWA 的轨迹跟踪依赖 `pid_drive` 的航向保持；DWA 仿真的航向误差用 `heading_fusion` 对标
- **阶段 C（检测导航闭环）**：Nav2 到位精度不满足时可下放到 `pid_drive` 做末段精确到位
