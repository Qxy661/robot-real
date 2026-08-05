# 实机视觉能力 · YOLO 目标检测 📷

> 把 M2 训练的 YOLO 模型部署到实机视觉链路。实机任务「目标巡检」的核心能力。

## 能力

- **三种输入源**：图片 / 视频 / MJPEG 流（LEAP 实机摄像头是 HTTP/MJPEG）
- **检测输出**：JSON（类别/置信度/框坐标/像素中心）+ 标注可视化
- **可复用模型**：钢珠（mAP 0.93）、VisDrone 低空小目标（mAP 0.38）

## 用法

```bash
# 环境：conda activate dl（有 ultralytics）

# 图片检测
python detector.py --image test.jpg --model best.pt

# 视频检测（每15帧标注一次）
python detector.py --video clip.mp4 --model best.pt --conf 0.4

# MJPEG 实时流（实机摄像头）
python detector.py --mjpeg http://192.168.1.100:8080/?action=stream \
    --model best.pt
```

## 输出示例

```
检测到 5 个目标:
  steel_ball   conf=0.86 中心=(147,219)
  steel_ball   conf=0.81 中心=(61,48)
```

检测 JSON：`output.json`（含 cls_name / conf / x1y1x2y2 / cxcy）

## 实机对接（阶段 1-3）

```
实机摄像头(MJPEG) → detector.py → 检测JSON → ROS2桥接 → /vision/detections
                                              → 目标中心/导航决策
```

- **阶段 1**：接 MJPEG 流验证检测（真机到手）
- **阶段 3**：检测结果接导航，实现「导航→检测确认→报告」巡检闭环
