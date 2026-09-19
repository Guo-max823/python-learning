# -*- coding: utf-8 -*-
with open("D:/python AI/hanzhong_air/hanzhong_aqi_2025.csv", "rb") as f:
    raw = f.read()
# 找第2行（第一条数据）
lines = raw.split(b"\r\n")[:3]
for i, ln in enumerate(lines):
    print(i, ln[:80])
# 测试各级别解码
for enc in ("utf-8", "gbk", "gb2312"):
    try:
        print(enc, "->", lines[1].decode(enc)[:60])
    except Exception as e:
        print(enc, "fail", e)
