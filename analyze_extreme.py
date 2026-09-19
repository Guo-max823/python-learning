# -*- coding: utf-8 -*-
import pandas as pd
df = pd.read_csv("D:/python AI/hanzhong_air/hanzhong_aqi_2025.csv", encoding="utf-8-sig")
df["日期"] = pd.to_datetime(df["日期"])

print("=== 极端值核查 ===")
print("AQI 最高的5天:")
print(df.nlargest(5, "AQI")[["日期","AQI","质量等级","PM2.5","PM10"]].to_string(index=False))
print("\nPM10 最高的5天:")
print(df.nlargest(5, "PM10")[["日期","AQI","质量等级","PM2.5","PM10"]].to_string(index=False))
print("\nPM2.5 最高的5天:")
print(df.nlargest(5, "PM2.5")[["日期","AQI","质量等级","PM2.5","PM10"]].to_string(index=False))

print("\n=== 1月等级分布（对照源站: 优1 良7 轻度14 中度2 重度7）===")
jan = df[df["日期"].dt.month == 1]
print(jan["质量等级"].value_counts().to_string())

print("\n=== 1月AQI/PM2.5 极值（对照源站: AQI 36-257, PM2.5 20-207）===")
print(f"AQI min={jan['AQI'].min()} max={jan['AQI'].max()}")
print(f"PM2.5 min={jan['PM2.5'].min()} max={jan['PM2.5'].max()}")

# 空气污染首要污染物判定（按IAQI估算,简单近似: 取各污染物IAQI最大者）
def iaqi_pm25(v):
    if v<=35: return v*50/35
    if v<=75: return 50+(v-35)*50/40
    if v<=115: return 100+(v-75)*50/40
    if v<=150: return 150+(v-115)*50/35
    if v<=250: return 200+(v-150)*100/100
    if v<=350: return 300+(v-250)*100/100
    return 400+(v-350)*100/150
def iaqi_pm10(v):
    if v<=50: return v
    if v<=150: return 50+(v-50)*50/100
    if v<=250: return 100+(v-150)*50/100
    if v<=350: return 150+(v-250)*50/100
    if v<=420: return 200+(v-350)*100/70
    if v<=500: return 300+(v-420)*100/80
    return 400+(v-500)*100/100
def iaqi_o3(v):
    if v<=100: return v
    if v<=160: return 50+(v-100)*50/60
    if v<=215: return 100+(v-160)*50/55
    if v<=265: return 150+(v-215)*50/50
    if v<=800: return 200+(v-265)*100/535
    return 300
def iaqi_no2(v):
    if v<=40: return v*50/40
    if v<=80: return 50+(v-40)*50/40
    if v<=180: return 100+(v-80)*50/100
    if v<=280: return 150+(v-180)*50/100
    if v<=565: return 200+(v-280)*100/285
    return 300
def iaqi_so2(v):
    if v<=50: return v
    if v<=150: return 50+(v-50)*50/100
    if v<=475: return 100+(v-150)*50/325
    if v<=800: return 150+(v-475)*50/325
    if v<=1600: return 200+(v-800)*100/800
    return 300
def iaqi_co(v):
    if v<=2: return v*50/2
    if v<=4: return 50+(v-2)*50/2
    if v<=14: return 100+(v-4)*50/10
    if v<=24: return 150+(v-14)*50/10
    if v<=36: return 200+(v-24)*100/12
    return 300

df["IAQI_PM25"] = df["PM2.5"].apply(iaqi_pm25)
df["IAQI_PM10"] = df["PM10"].apply(iaqi_pm10)
df["IAQI_O3"] = df["O3"].apply(iaqi_o3)
df["IAQI_NO2"] = df["NO2"].apply(iaqi_no2)
df["IAQI_SO2"] = df["SO2"].apply(iaqi_so2)
df["IAQI_CO"] = df["CO"].apply(iaqi_co)
cols = ["IAQI_PM25","IAQI_PM10","IAQI_O3","IAQI_NO2","IAQI_SO2","IAQI_CO"]
df["首要污染物"] = df[cols].idxmax(axis=1).map({
    "IAQI_PM25":"PM2.5","IAQI_PM10":"PM10","IAQI_O3":"O3","IAQI_NO2":"NO2","IAQI_SO2":"SO2","IAQI_CO":"CO"})
# 若所有IAQI都<=50 视为"无"
df.loc[df[cols].max(axis=1) <= 50, "首要污染物"] = "无（优）"
print("\n=== 首要污染物分布（全年按AQI>50的天）===")
print(df[df["AQI"]>50]["首要污染物"].value_counts().to_string())
df.to_csv("D:/python AI/hanzhong_air/hanzhong_aqi_2025_analyzed.csv", index=False, encoding="utf-8-sig")
print("\nsaved analyzed csv")
