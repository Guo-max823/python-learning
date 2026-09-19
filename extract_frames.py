# -*- coding: utf-8 -*-
"""从录屏中抽帧，每秒1帧，输出到 _video_frames/"""
import os
import cv2

src = r"C:\Users\17223\Videos\Captures\汉中城市空气质量数据分析 - Google Chrome 2026-09-19 11-43-32.mp4"
out_dir = r"D:\python AI\hanzhong_air\_video_frames"
os.makedirs(out_dir, exist_ok=True)

cap = cv2.VideoCapture(src)
if not cap.isOpened():
    print("OPEN_FAIL")
    raise SystemExit(1)
fps = cap.get(cv2.CAP_PROP_FPS) or 25
total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
print(f"fps={fps:.2f} total={total} duration={total/fps:.1f}s")

interval = max(1, int(round(fps)))
idx = 0
n = 0
while True:
    ok, frame = cap.read()
    if not ok:
        break
    if idx % interval == 0:
        p = os.path.join(out_dir, f"f{idx:04d}.png")
        cv2.imwrite(p, frame)
        n += 1
    idx += 1
cap.release()
print("frames saved:", n)
