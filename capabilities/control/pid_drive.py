#!/usr/bin/env python3
"""
PID 精确行驶 · 走 N 米精确停 + 保持直线

双闭环 PID，输出到 /cmd_vel：
  - 位置环：目标距离 vs 已行驶距离 → 线速度（vx）
      traveled 把 /odom 位移投影到起始航向上，避免斜着走也算满距离
  - 航向环：起始 yaw 为参考，航向偏差 → 角速度（wz），保证走直线不偏

量化产出（作品集素材）：
  - 到位精度：超调量 / 稳态误差 / 到位时间
  - 整定曲线：CSV 记录 (t, distance, target, yaw_err, vx, wz)

用法：
    python3 pid_drive.py --distance 2.0 --speed 0.3
    python3 pid_drive.py --distance 1.5 --kp 0.8 --ki 0.1 --kd 0.05
"""
import argparse
import csv
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


def wrap_pi(angle):
    """角度归一化到 [-pi, pi)."""
    return (angle + math.pi) % (2 * math.pi) - math.pi


class PID:
    """离散 PID，带输出限幅与积分抗饱和."""
    def __init__(self, kp, ki, kd, out_min, out_max):
        self.kp, self.ki, self.kd = kp, ki, kd
        self.out_min, self.out_max = out_min, out_max
        self.integral = 0.0
        self.prev_error = 0.0

    def reset(self):
        self.integral = 0.0
        self.prev_error = 0.0

    def update(self, error, dt):
        self.integral += error * dt
        # 积分抗饱和：输出限幅内才累计
        self.integral = max(self.out_min, min(self.out_max, self.integral))
        derivative = (error - self.prev_error) / dt if dt > 1e-6 else 0.0
        self.prev_error = error
        out = self.kp * error + self.ki * self.integral + self.kd * derivative
        return max(self.out_min, min(self.out_max, out))


class PIDDrive(Node):
    def __init__(self, args):
        super().__init__("pid_drive")
        self.args = args
        self.pub = self.create_publisher(Twist, "cmd_vel", 10)
        self.odom = None
        self.create_subscription(Odometry, "odom", self.odom_cb, 10)
        # 控制周期（20 Hz）
        self.rate = self.create_rate(20)

    def odom_cb(self, m):
        self.odom = m

    def get_state(self):
        deadline = time.time() + 3
        while rclpy.ok() and time.time() < deadline:
            rclpy.spin_once(self, timeout_sec=0.2)
            if self.odom is not None:
                return self.odom
        return None

    def run(self):
        a = self.args
        state = self.get_state()
        if state is None:
            self.get_logger().error("收不到 /odom")
            return

        # 起始参考
        p0 = state.pose.pose.position
        yaw0 = quat_to_yaw(state.pose.pose.orientation)

        pos_pid = PID(a.kp, a.ki, a.kd, -a.speed, a.speed)
        yaw_pid = PID(a.yaw_kp, 0.0, a.yaw_kd, -a.yaw_max, a.yaw_max)

        print(f"行驶目标: {a.distance:.2f} m @ ≤{a.speed:.2f} m/s")
        print(f"3 秒后启动，确保前方留出 {a.distance + 1:.1f} m 空间...")
        time.sleep(3)

        # 记录数据
        rows = []
        start_time = time.time()
        reached = False
        min_traveled = 0.0   # 用于计算超调（越过目标后再回退的最大距离）
        settle_time = None

        while rclpy.ok():
            t = time.time() - start_time
            state = self.get_state()
            if state is None:
                break
            pos = state.pose.pose.position
            yaw = quat_to_yaw(state.pose.pose.orientation)

            # 位移投影到起始航向 → 有效行进距离
            traveled = ((pos.x - p0.x) * math.cos(yaw0) +
                        (pos.y - p0.y) * math.sin(yaw0))

            err = a.distance - traveled
            dt = 1.0 / 20.0
            vx = pos_pid.update(err, dt)
            # 航向保持：误差 = 起始航向 - 当前航向
            yaw_err = wrap_pi(yaw0 - yaw)
            wz = yaw_pid.update(yaw_err, dt)

            twist = Twist()
            twist.linear.x = vx
            twist.angular.z = wz
            self.pub.publish(twist)

            rows.append((round(t, 3), round(traveled, 3),
                         round(err, 3), round(yaw_err, 3),
                         round(vx, 3), round(wz, 3)))

            if err < min_traveled:
                min_traveled = err          # 最负 = 最大超调
            if abs(err) < a.tolerance and settle_time is None:
                settle_time = t
            if settle_time is not None and t - settle_time > a.hold_time:
                reached = True
                break
            if t > a.timeout:
                break

        self.pub.publish(Twist())   # 停车
        self.report(rows, traveled, min_traveled, settle_time, reached)

    def report(self, rows, final_distance, min_traveled, settle_time, reached):
        a = self.args
        steady_err = a.distance - final_distance
        overshoot = -min_traveled if min_traveled < 0 else 0.0
        print(f"\n=== 行驶结果 ===")
        print(f"目标 {a.distance:.2f} m / 实走 {final_distance:.3f} m")
        print(f"稳态误差: {steady_err:+.4f} m（{abs(steady_err)/a.distance*100:.2f}%）")
        print(f"超调量: {overshoot:.3f} m")
        print(f"到位时间: {settle_time:.2f}s" if settle_time else "未到位（超时）")
        print(f"到达判定: {'✅ 达标' if reached and abs(steady_err) <= a.tolerance else '❌ 未达标'}")

        out = a.out or "pid_drive_data.csv"
        with open(out, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["t", "distance", "target_err", "yaw_err", "vx", "wz"])
            w.writerows(rows)
        print(f"整定曲线已保存: {out}")


def main():
    parser = argparse.ArgumentParser(description="PID 精确行驶（走 N 米精确停）")
    parser.add_argument("--distance", type=float, required=True, help="目标距离 m")
    parser.add_argument("--speed", type=float, default=0.3, help="最大线速度 m/s")
    parser.add_argument("--kp", type=float, default=0.8, help="位置环 P")
    parser.add_argument("--ki", type=float, default=0.05, help="位置环 I")
    parser.add_argument("--kd", type=float, default=0.0, help="位置环 D")
    parser.add_argument("--yaw-kp", type=float, default=0.6, help="航向环 P")
    parser.add_argument("--yaw-kd", type=float, default=0.1, help="航向环 D")
    parser.add_argument("--yaw-max", type=float, default=0.6, help="最大角速度 rad/s")
    parser.add_argument("--tolerance", type=float, default=0.03,
                        help="到位误差 m（±3cm）")
    parser.add_argument("--hold-time", type=float, default=0.5,
                        help="误差达标后保持时间 s")
    parser.add_argument("--timeout", type=float, default=30.0,
                        help="超时 s，防卡死")
    parser.add_argument("--out", default="", help="CSV 输出路径")
    args = parser.parse_args()

    rclpy.init()
    node = PIDDrive(args)
    node.run()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
