# -*- coding: utf-8 -*-
import requests, re
r = requests.get("https://www.tianqihoubao.com/aqi/hanzhong-202501.html",
                 headers={"User-Agent": "Mozilla/5.0"}, timeout=20)
print("apparent_encoding:", r.apparent_encoding)
print("r.encoding:", r.encoding)
m = re.search(rb'charset=["\']?([\w-]+)', r.content[:2000])
print("meta charset:", m.group(1).decode() if m else None)
# 直接尝试 utf-8 解码一段含中文的部分
try:
    txt = r.content.decode("utf-8")
    print("utf8 decode OK, 包含'中度污染':", "中度污染" in txt)
except Exception as e:
    print("utf8 decode failed:", e)
