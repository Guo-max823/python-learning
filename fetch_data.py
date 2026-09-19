# -*- coding: utf-8 -*-
"""
抓取汉中市 2025 年逐日空气质量数据（来源：天气后报 tianqihoubao.com）— 修正版
严格按 GBK 解码并校验中文，输出: hanzhong_aqi_2025.csv
"""
import re
import time
import csv
import requests
from bs4 import BeautifulSoup

BASE = "https://www.tianqihoubao.com/aqi/hanzhong-{ym}.html"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Referer": "https://www.tianqihoubao.com/aqi/",
}
EXPECT_LEVELS = ["优", "良", "轻度污染", "中度污染", "重度污染", "严重污染"]


def decode_page(raw: bytes) -> str:
    """依次尝试 gbk / utf-8，返回成功且能识别质量等级文本的解码结果"""
    for enc in ("gbk", "utf-8"):
        try:
            txt = raw.decode(enc)
            if any(lv in txt for lv in EXPECT_LEVELS):
                return txt, enc
        except (UnicodeDecodeError, LookupError):
            continue
    # 兜底
    return raw.decode("gbk", errors="replace"), "gbk-replace"


def fetch_month(year, month):
    ym = f"{year}{month:02d}"
    url = BASE.format(ym=ym)
    for attempt in range(3):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=20)
            if resp.status_code != 200:
                print(f"  [{ym}] HTTP {resp.status_code}, retry {attempt+1}")
                time.sleep(2)
                continue
            txt, enc = decode_page(resp.content)
            soup = BeautifulSoup(txt, "html.parser")
            table = soup.find("table")
            if not table:
                print(f"  [{ym}] no table, retry {attempt+1}")
                time.sleep(2)
                continue
            rows = []
            for tr in table.find_all("tr")[1:]:
                tds = [td.get_text(strip=True) for td in tr.find_all("td")]
                if len(tds) < 9:
                    continue
                date, aqi, level = tds[0], tds[1], tds[2]
                pm25, pm10, no2, so2, co, o3 = tds[4], tds[5], tds[6], tds[7], tds[8], tds[9]
                m = re.match(r"(\d{4})-(\d{2})-(\d{2})", date)
                if not m:
                    continue
                rows.append({
                    "日期": date,
                    "AQI": int(aqi),
                    "质量等级": level,
                    "PM2.5": float(pm25),
                    "PM10": float(pm10),
                    "NO2": float(no2),
                    "SO2": float(so2),
                    "CO": float(co),
                    "O3": float(o3),
                })
            bad = [r["日期"] for r in rows if r["质量等级"] not in EXPECT_LEVELS]
            print(f"  [{ym}] rows={len(rows)} enc={enc} bad_levels={bad[:3]}")
            return rows
        except Exception as e:
            print(f"  [{ym}] error: {e}, retry {attempt+1}")
            time.sleep(2)
    return []


def main():
    all_rows = []
    for month in range(1, 13):
        print(f"fetching 2025-{month:02d} ...")
        all_rows.extend(fetch_month(2025, month))
        time.sleep(1.0)

    seen, unique = set(), []
    for r in all_rows:
        if r["日期"] not in seen:
            seen.add(r["日期"])
            unique.append(r)
    unique.sort(key=lambda r: r["日期"])

    out = "D:/python AI/hanzhong_air/hanzhong_aqi_2025.csv"
    with open(out, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["日期", "AQI", "质量等级", "PM2.5", "PM10", "NO2", "SO2", "CO", "O3"])
        writer.writeheader()
        writer.writerows(unique)
    print(f"TOTAL: {len(unique)} days -> {out}")


if __name__ == "__main__":
    main()
