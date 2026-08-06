#!/usr/bin/env python3
"""
IMU + 里程计 航向融合 · 互补滤波

问题：
  - 里程计 yaw（编码器积分）：履带打滑 / 地面不均时漂移，但短时稳定、无累积突变
  - IMU 陀螺 yaw（角速度积分）：动态响应快、不受打滑影响，但有偏置漂移

互补滤波：高频信陀螺（快），低频信里程计（稳）
    yaw_fused += (gyro_z - bias) * dt
    yaw_fused  = α * yaw_fused + (1 - α) * yaw_odom
  启动时静止 3 秒估计陀螺偏置 bias（角速度均值），之后实时补偿

输出（作品集素材：融合前后航向误差对比）：
  - CSV: (t, yaw_odom, yaw_imu, yaw_fused, gyro_z, bias)
  - 结束打印静止窗口内各源标准差：融合后应明显小于任一单一源

用法：
    python3 heading_fusion.py --alpha 0.98 --duration 30
    先静止 3 秒（估偏置），再任意转动/直行，全程记录对比
"""
import argparse
import csv
import math
import statistics
import time

import rclpy
from nav_msgs.msg import Odometry
from rclpy.node import Node
from sensor_msgs.msg import Imu


def quat_to_yaw(q):
    """四元数 → yaw（弧度，范围 -pi..pi）."""
    return math.atan2(2.0 * (q.w * q.z + q.x * q.y),
                      1.0 - 2.0 * (q.y * q.y + q.z * q.z))


def wrap_pi(angle):
    """角度归一化到 [-pi, pi)."""
    return (angle + math.pi) % (2 * math.pi) - math.pi


class HeadingFusion(Node):
    def __init__(self, args):
        super().__init__("heading_fusion")
        self.args = args
        self.odom = None
        self.imu = None
        self.create_subscription(Odometry, "odom", self.odom_cb, 10)
        self.create_subscription(Imu, "imu", self.imu_cb, 10)
        self.rate = self.create_rate(50)   # 50 Hz 融合

    def odom_cb(self, m):
        self.odom = m

    def imu_cb(self, m):
        self.imu = m

    def run(self):
        a = self.args
        # 等话题
        deadline = time.time() + 3
        while rclpy.ok() and time.time() < deadline:
            rclpy.spin_once(self, timeout_sec=0.2)
            if self.odom is not None and self.imu is not None:
                break
        if self.odom is None or self.imu is None:
            self.get_logger().error("收不到 /odom 或 /imu")
            return

        # 阶段 1：静止估陀螺偏置
        print(f"保持静止 {a.bias_time}s 估计陀螺偏置...")
        gyro_samples = []
        t0 = time.time()
        while rclpy.ok() and time.time() - t0 < a.bias_time:
            rclpy.spin_once(self, timeout_sec=0.05)
            if self.imu is not None:
                gyro_samples.append(self.imu.angular_velocity.z)
        bias = statistics.mean(gyro_samples)
        print(f"陀螺偏置 bias = {bias:.5f} rad/s")

        # 阶段 2：互补滤波记录
        yaw_fused = None
        rows = []
        t0 = time.time()
        prev_t = t0
        while rclpy.ok() and time.time() - t0 < a.duration:
            rclpy.spin_once(self, timeout_sec=0.02)
            t = time.time()
            dt = t - prev_t
            prev_t = t

            yaw_odom = quat_to_yaw(self.odom.pose.pose.orientation)
            gyro_z = self.imu.angular_velocity.z

            # 里程计源：odom 角度直接读
            # IMU 源：陀螺积分（独立于里程计，验证融合效果）
            if yaw_fused is None:
                yaw_imu = yaw_odom  # 初始对齐，方便对比
            else:
                yaw_imu = wrap_pi(yaw_imu + (gyro_z - bias) * dt)

            # 互补滤波：陀螺积分 + 里程计校正
            if yaw_fused is None:
                yaw_fused = yaw_odom
            else:
                yaw_fused = wrap_pi(yaw_fused + (gyro_z - bias) * dt)
                yaw_fused = (a.alpha * yaw_fused +
                             (1.0 - a.alpha) * yaw_odom)
                yaw_fused = wrap_pi(yaw_fused)

            elapsed = t - t0
            rows.append((round(elapsed, 3),
                         round(math.degrees(yaw_odom), 2),
                         round(math.degrees(yaw_imu), 2),
                         round(math.degrees(yaw_fused), 2),
                         round(gyro_z, 5), round(bias, 5)))
            if elapsed % 5 < 0.02:
                print(f"t={elapsed:5.1f}s  odom={math.degrees(yaw_odom):7.2f}° "
                      f"imu={math.degrees(yaw_imu):7.2f}° "
                      f"fused={math.degrees(yaw_fused):7.2f}°")

        self.save(rows, a)

    def save(self, rows, a):
        out = a.out or "heading_fusion_data.csv"
        with open(out, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["t", "yaw_odom_deg", "yaw_imu_deg",
                        "yaw_fused_deg", "gyro_z", "bias"])
            w.writerows(rows)
        print(f"\n数据已保存: {out}")

        # 质量指标：后 10s 静止段（如有）各源标准差
        tail = rows[-int(10 / max(rows[1][0] - rows[0][0], 1e-3)):]
        if len(tail) >= 10:
            odom_std = statistics.pstdev([r[1] for r in tail])
            imu_std = statistics.pstdev([r[2] for r in tail])
            fused_std = statistics.pstdev([r[3] for r in tail])
            print(f"\n=== 静止段标准差（°）===")
            print(f"里程计: {odom_std:.3f}")
            print(f"陀螺积分: {imu_std:.3f}")
            print(f"互补融合: {fused_std:.3f}")
            if fused_std < min(odom_std, imu_std):
                print("融合有效：标准差小于任一单一源 ✅")
            else:
                print("提示：融合未显著改善，可调小 α 增加里程计权重")


def main():
    parser = argparse.ArgumentParser(description="IMU+里程计航向互补融合")
    parser.add_argument("--alpha", type=float, default=0.98,
                        help="互补系数（越接近1越信陀螺，越小越信里程计）")
    parser.add_argument("--bias-time", type=float, default=3.0,
                        help="启动静止估偏置时长 s")
    parser.add_argument("--duration", type=float, default=30.0,
                        help="融合记录时长 s")
    parser.add_argument("--out", default="", help="CSV 输出路径")
    args = parser.parse_args()

    if not (0.0 <= args.alpha <= 1.0):
        print("alpha 须在 [0,1]")
        return

    rclpy.init()
    node = HeadingFusion(args)
    node.run()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
