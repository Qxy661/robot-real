"""
实机目标检测器（capability 模块）

核心能力：把 M2 训练的 YOLO 模型部署到实机视觉链路。
支持三种输入源（同 ultralytics 接口）：
  1. 图片文件    --image path.jpg
  2. 视频文件    --video path.mp4
  3. MJPEG 流    --mjpeg http://ip:8080/?action=stream （LEAP 实机摄像头）

输出：
  - 检测 JSON（目标类别/置信度/框坐标/像素位置）
  - 标注可视化（写文件或窗口显示）

运行环境：conda dl（有 ultralytics）。实机阶段由 ROS2 桥接节点调用。

用法示例：
  python detector.py --image test.jpg --model best.pt
  python detector.py --video clip.mp4 --model best.pt --conf 0.4
"""
import argparse
import json
import os
import time

import cv2
import numpy as np


def load_model(model_path):
    """加载 YOLO 模型."""
    from ultralytics import YOLO
    model = YOLO(model_path)
    return model


def detect(model, frame, conf=0.25, target_classes=None):
    """单帧检测. 返回检测列表 [{cls_id, cls_name, conf, x1,y1,x2,y2, cx,cy}]."""
    result = model(frame, conf=conf, verbose=False)[0]
    detections = []
    names = model.names
    if result.boxes is not None:
        for box in result.boxes:
            cls_id = int(box.cls[0])
            if target_classes and cls_id not in target_classes:
                continue
            x1, y1, x2, y2 = [float(v) for v in box.xyxy[0]]
            detections.append({
                "cls_id": cls_id,
                "cls_name": names[cls_id],
                "conf": round(float(box.conf[0]), 3),
                "x1": round(x1, 1), "y1": round(y1, 1),
                "x2": round(x2, 1), "y2": round(y2, 1),
                "cx": round((x1 + x2) / 2, 1),
                "cy": round((y1 + y2) / 2, 1),
            })
    return detections


def annotate(frame, detections):
    """画检测框 + 标签 + 中心点."""
    vis = frame.copy()
    for d in detections:
        x1, y1, x2, y2 = int(d["x1"]), int(d["y1"]), int(d["x2"]), int(d["y2"])
        label = f"{d['cls_name']} {d['conf']:.2f}"
        color = (0, 255, 0)
        cv2.rectangle(vis, (x1, y1), (x2, y2), color, 2)
        cv2.putText(vis, label, (x1, max(0, y1 - 8)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        cv2.circle(vis, (int(d["cx"]), int(d["cy"])), 4, (0, 165, 255), -1)
    return vis


def process_image(model, path, conf, out):
    """处理单张图片."""
    frame = cv2.imread(path)
    if frame is None:
        print(f"无法读取: {path}")
        return
    dets = detect(model, frame, conf)
    print(f"检测到 {len(dets)} 个目标:")
    for d in dets:
        print(f"  {d['cls_name']:12s} conf={d['conf']:.2f} "
              f"中心=({d['cx']:.0f},{d['cy']:.0f})")
    vis = annotate(frame, dets)
    cv2.imwrite(out, vis)
    print(f"标注图已保存: {out}")
    with open(out.replace(".jpg", ".json").replace(".png", ".json"), "w") as f:
        json.dump(dets, f, ensure_ascii=False, indent=2)
    print(f"检测 JSON 已保存")


def process_video(model, path, conf, out, sample_every=15):
    """处理视频，每 N 帧检测一次并保存标注."""
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        print(f"无法打开视频: {path}")
        return
    writer = None
    frame_idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_idx % sample_every == 0:
            dets = detect(model, frame, conf)
            vis = annotate(frame, dets)
            if writer is None:
                h, w = vis.shape[:2]
                writer = cv2.VideoWriter(out, cv2.VideoWriter_fourcc(*"mp4v"),
                                         20.0, (w, h))
            writer.write(vis)
            print(f"帧 {frame_idx}: {len(dets)} 个目标")
        frame_idx += 1
    cap.release()
    if writer:
        writer.release()
    print(f"标注视频已保存: {out}")


def process_mjpeg(model, url, conf, max_frames=0):
    """处理 MJPEG 流（实机摄像头），实时显示标注."""
    cap = cv2.VideoCapture(url)
    if not cap.isOpened():
        print(f"无法连接 MJPEG 流: {url}")
        return
    frame_idx = 0
    fps_time = time.time()
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        dets = detect(model, frame, conf)
        vis = annotate(frame, dets)
        fps = 1.0 / max(1e-6, time.time() - fps_time)
        fps_time = time.time()
        cv2.putText(vis, f"FPS: {fps:.1f}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        cv2.imshow("LEAP Vision", vis)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        frame_idx += 1
        if max_frames and frame_idx >= max_frames:
            break
    cap.release()
    cv2.destroyAllWindows()


def main():
    parser = argparse.ArgumentParser(description="实机目标检测器")
    parser.add_argument("--model", required=True, help="YOLO 模型路径")
    parser.add_argument("--image", help="图片路径")
    parser.add_argument("--video", help="视频路径")
    parser.add_argument("--mjpeg", help="MJPEG 流 URL")
    parser.add_argument("--conf", type=float, default=0.25)
    parser.add_argument("--out", default="output.jpg", help="输出文件")
    args = parser.parse_args()

    model = load_model(args.model)
    print(f"模型已加载: {args.model}")

    if args.image:
        process_image(model, args.image, args.conf, args.out)
    elif args.video:
        process_video(model, args.video, args.conf, args.out)
    elif args.mjpeg:
        process_mjpeg(model, args.mjpeg, args.conf)
    else:
        print("请指定 --image / --video / --mjpeg 之一")


if __name__ == "__main__":
    main()
