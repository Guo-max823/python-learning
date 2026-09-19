# -*- coding: utf-8 -*-
"""数据核验 + 描述性统计"""
import pandas as pd

df = pd.read_csv("D:/python AI/hanzhong_air/hanzhong_aqi_2025.csv", encoding="utf-8-sig")
df["日期"] = pd.to_datetime(df["日期"])
print("=== 数据形状 ===")
print(df.shape)
print("\n=== 缺失值 ===")
print(df.isna().sum().sum())
print("\n=== 前5行 ===")
print(df.head().to_string())
print("\n=== 描述统计 ===")
print(df[["AQI", "PM2.5", "PM10", "NO2", "SO2", "CO", "O3"]].describe().round(2).to_string())

print("\n=== 质量等级分布 ===")
print(df["质量等级"].value_counts().to_string())
good_days = df["质量等级"].isin(["优", "良"]).sum()
print(f"优良天数: {good_days}, 优良率: {good_days/len(df)*100:.1f}%")
print(f"PM2.5 年均: {df['PM2.5'].mean():.2f}  μg/m3")
print(f"PM10 年均: {df['PM10'].mean():.2f}  μg/m3")
print(f"O3 年均: {df['O3'].mean():.2f}  μg/m3")
print(f"SO2 年均: {df['SO2'].mean():.2f}  μg/m3")
print(f"NO2 年均: {df['NO2'].mean():.2f}  μg/m3")
print(f"CO 年均: {df['CO'].mean():.3f}  mg/m3")

print("\n=== 月度 PM2.5 均值 ===")
print(df.groupby(df["日期"].dt.month)["PM2.5"].mean().round(2).to_string())
print("\n=== 月度 AQI 均值 ===")
print(df.groupby(df["日期"].dt.month)["AQI"].mean().round(2).to_string())
print("\n=== 月度优良率 ===")
m = df.groupby(df["日期"].dt.month)["质量等级"].apply(lambda s: (s.isin(["优","良"])).mean()*100).round(1)
print(m.to_string())

# AQI 等级与首要污染物统计（粗略：AQI>50 时按浓度超标倍数判断）
print("\n=== 季节划分（气象学）===")
season_map = {12:"冬",1:"冬",2:"冬",3:"春",4:"春",5:"春",6:"夏",7:"夏",8:"夏",9:"秋",10:"秋",11:"秋"}
df["季节"] = df["日期"].dt.month.map(season_map)
print(df.groupby("季节")[["AQI","PM2.5","PM10","O3"]].mean().round(2).to_string())
