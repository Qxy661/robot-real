#!/usr/bin/env python3
"""
里程计标定 · 直行（轮径）+ 原地转向（轮距）

差速/履带底盘的里程计有两个比例误差源，需要两次实验分开标定：
  1. 直行实验 (--test straight)：标定轮径（线性比例）
     - 直行指定时间，对比 /odom 报告位移 vs 卷尺实测
     - ratio = 实际/报告；轮径修正 = 当前轮径 × ratio
  2. 转向实验 (--test rotate)：标定轮距（角向比例）
     - 原地转指定角度，对比 /odom 报告转角 vs 量角器实测
     - ratio = 实际/报告；轮距修正 = 当前轮距 × ratio

标定系数含义：
  ratio > 1 → 实际比报告多（odom 偏小 → 轮径/轮距需调大）
  ratio < 1 → 实际比报告少（odom 偏大 → 轮径/轮距需调小）

用法：
    python3 odom_calib.py --test straight --speed 0.15 --duration 6
    python3 odom_calib.py --test rotate  --omega 0.5  --duration 6
"""
import argparse
import math
import time

import rclpy
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from rclpy.node import Node


def quat_to_yaw(q):
    """四元数 → yaw（弧度，范围 -pi..pi）."""
    return math.atan2(2.0 * (q.w * q.z + q.x * q.y),
                      1.0 - 2.0 * (q.y * q.y + q.z * q.z))


class OdomCalib(Node):
    def __init__(self):
        super().__init__("odom_calib")
        self.pub = self.create_publisher(Twist, "cmd_vel", 10)
        self.odom = None
        self.create_subscription(Odometry, "odom", self.odom_cb, 10)

    def odom_cb(self, m):
        self.odom = m.pose.pose

    def get_state(self):
        deadline = time.time() + 3
        while rclpy.ok() and time.time() < deadline:
            rclpy.spin_once(self, timeout_sec=0.2)
            if self.odom is not None:
                return (self.odom.position.x, self.odom.position.y,
                        quat_to_yaw(self.odom.orientation))
        return None

    def drive(self, speed, duration):
        """直行实验：按指定速度行驶指定时间，返回 odom 报告位移（m）."""
        start = self.get_state()
        if start is None:
            self.get_logger().error("收不到 /odom")
            return None
        twist = Twist()
        twist.linear.x = speed
        end_time = time.time() + duration
        while rclpy.ok() and time.time() < end_time:
            rclpy.spin_once(self, timeout_sec=0.05)
            self.pub.publish(twist)  # 持续发布
        self.pub.publish(Twist())
        end = self.get_state()
        if end is None:
            return None
        dx, dy = end[0] - start[0], end[1] - start[1]
        return math.hypot(dx, dy)

    def rotate(self, omega, duration):
        """转向实验：原地按指定角速度转指定时间，返回 odom 报告转角（rad）."""
        start = self.get_state()
        if start is None:
            self.get_logger().error("收不到 /odom")
            return None
        twist = Twist()
        twist.angular.z = omega
        end_time = time.time() + duration
        while rclpy.ok() and time.time() < end_time:
            rclpy.spin_once(self, timeout_sec=0.05)
            self.pub.publish(twist)
        self.pub.publish(Twist())
        end = self.get_state()
        if end is None:
            return None
        # 转向角度取有符号差，避免 -pi/pi 跳变
        return end[2] - start[2]

    def run_straight(self, speed, duration):
        print(f"\n直行实验: {speed} m/s × {duration}s")
        print("确保小车前方留出 ~2m 空间，3 秒后启动...")
        time.sleep(3)
        reported = self.drive(speed, duration)
        if reported is None:
            print("实验失败：无 /odom")
            return
        print(f"/odom 报告位移: {reported:.3f} m")
        actual = float(input("用卷尺量实际位移 (m): "))
        ratio = actual / reported
        self.print_ratio(ratio, "轮径修正系数", "调大" if ratio > 1 else "调小")

    def run_rotate(self, omega, duration):
        print(f"\n转向实验: {omega:.2f} rad/s × {duration}s "
              f"（期望转 {math.degrees(abs(omega * duration)):.0f}°）")
        print("确保原地留出转动空间，3 秒后启动...")
        time.sleep(3)
        reported = self.rotate(omega, duration)
        if reported is None:
            print("实验失败：无 /odom")
            return
        print(f"/odom 报告转角: {math.degrees(reported):.1f}°")
        actual_deg = float(input("用量角器量实际转角 (度): "))
        ratio = math.radians(actual_deg) / reported
        self.print_ratio(ratio, "轮距修正系数", "调大" if ratio > 1 else "调小")

    @staticmethod
    def print_ratio(ratio, label, direction):
        print(f"\n标定系数 ratio = 实际/报告 = {ratio:.4f}")
        if abs(ratio - 1) < 0.01:
            print("里程计已较准确（误差 <1%）")
        else:
            print(f"建议：{label} ×{ratio:.4f}（{'调大' if ratio > 1 else '调小'}）")


def main():
    parser = argparse.ArgumentParser(description="里程计标定（直行+转向）")
    parser.add_argument("--test", choices=["straight", "rotate"],
                        default="straight", help="直行标轮径 / 转向标轮距")
    parser.add_argument("--speed", type=float, default=0.15, help="直行速度 m/s")
    parser.add_argument("--omega", type=float, default=0.5, help="转向角速度 rad/s")
    parser.add_argument("--duration", type=float, default=6.0, help="行驶时长 s")
    args = parser.parse_args()

    rclpy.init()
    node = OdomCalib()
    if args.test == "straight":
        node.run_straight(args.speed, args.duration)
    else:
        node.run_rotate(args.omega, args.duration)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
