# -*- coding: utf-8 -*-
import pandas as pd
from datetime import date

df_all = pd.read_csv("D:/python AI/hanzhong_air/hanzhong_aqi_2025_analyzed.csv", encoding="utf-8-sig")
df_all["日期"] = pd.to_datetime(df_all["日期"])
assert len(df_all) == 365

def count(d0, d1):
    d0 = pd.Timestamp(d0); d1 = pd.Timestamp(d1)
    if d0 > d1:
        d0, d1 = d1, d0
    return len(df_all[(df_all["日期"] >= d0) & (df_all["日期"] <= d1)])

cases = [
    ("all",   (date(2025,1,1), date(2025,12,31)), 365),
    ("q1",    (date(2025,1,1), date(2025,3,31)),  90),
    ("h1",    (date(2025,1,1), date(2025,6,30)),  181),
    ("d30",   (date(2025,12,2), date(2025,12,31)), 30),
    ("jun-aug",(date(2025,6,1), date(2025,8,31)),  92),
    ("mar-apr",(date(2025,3,15), date(2025,4,15)), 32),
    ("reversed",(date(2025,8,31), date(2025,6,1)), 92),
]
ok_all = True
for name, (a, b), exp in cases:
    got = count(a, b)
    ok = got == exp
    ok_all &= ok
    print(("OK " if ok else "FAIL"), name, "got", got, "exp", exp)
print("ALL_PASS" if ok_all else "SOME_FAILED")
