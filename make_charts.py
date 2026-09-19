# -*- coding: utf-8 -*-
"""
汉中市 2025 年空气质量分析 —— 静态图表生成
输出到 charts/ 目录
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm, Normalize

plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["figure.dpi"] = 150

BASE = os.path.dirname(os.path.abspath(__file__))
CHART_DIR = os.path.join(BASE, "charts")
os.makedirs(CHART_DIR, exist_ok=True)

df = pd.read_csv(os.path.join(BASE, "hanzhong_aqi_2025_analyzed.csv"), encoding="utf-8-sig")
df["日期"] = pd.to_datetime(df["日期"])
df["月份"] = df["日期"].dt.month
df["季节"] = df["月份"].map({12:"冬",1:"冬",2:"冬",3:"春",4:"春",5:"春",6:"夏",7:"夏",8:"夏",9:"秋",10:"秋",11:"秋"})

LEVEL_COLOR = {"优":"#67C23A","良":"#409EFF","轻度污染":"#E6A23C","中度污染":"#F56C6C","重度污染":"#9C27B0","严重污染":"#7A1F1F"}
LEVEL_ORDER = ["优","良","轻度污染","中度污染","重度污染","严重污染"]
POLLUTANTS = ["PM2.5","PM10","NO2","SO2","CO","O3"]
POLLUTANT_CN = {"PM2.5":"PM2.5 (ug/m3)","PM10":"PM10 (ug/m3)","NO2":"NO2 (ug/m3)","SO2":"SO2 (ug/m3)","CO":"CO (mg/m3)","O3":"O3 (ug/m3)"}

# ---------- 图1 全年 AQI 时间序列 ----------
fig, ax = plt.subplots(figsize=(13, 4.6))
ax.plot(df["日期"], df["AQI"], lw=0.9, color="#2f6fed", alpha=0.85)
for y, name, c in [(50,"优限",None),(100,"良限",None),(150,"轻度限",None),(200,"中度限",None),(300,"重度限",None)]:
    ax.axhline(y, color="#c8c8c8", lw=0.7, ls="--")
ax.fill_between(df["日期"], 0, 50, color="#67C23A", alpha=0.08)
ax.fill_between(df["日期"], 50, 100, color="#409EFF", alpha=0.06)
ax.set_title("汉中市 2025 年逐日 AQI 变化趋势", fontsize=14, pad=12)
ax.set_ylabel("AQI 指数")
ax.set_xlabel("日期")
ax.set_ylim(0, 330)
ax.grid(axis="y", alpha=0.25)
fig.tight_layout()
fig.savefig(os.path.join(CHART_DIR, "01_aqi_trend.png"))
plt.close(fig)

# ---------- 图2 月度污染物均值（柱线组合）----------
monthly = df.groupby("月份")[["PM2.5","PM10","O3"]].mean()
fig, ax = plt.subplots(figsize=(11, 4.8))
x = np.arange(12)
w = 0.26
ax.bar(x-w, monthly["PM2.5"], w, label="PM2.5", color="#2f6fed")
ax.bar(x,   monthly["PM10"],  w, label="PM10",  color="#67C23A")
ax.bar(x+w, monthly["O3"],    w, label="O3",    color="#E6A23C")
ax.set_xticks(x); ax.set_xticklabels([f"{i}月" for i in range(1,13)])
ax.set_ylabel("浓度 (ug/m3)")
ax.set_title("汉中市 2025 年月度主要污染物平均浓度", fontsize=14, pad=12)
ax.legend(frameon=False)
ax.grid(axis="y", alpha=0.25)
fig.tight_layout()
fig.savefig(os.path.join(CHART_DIR, "02_monthly_pollutants.png"))
plt.close(fig)

# ---------- 图3 质量等级占比环图 ----------
vc = df["质量等级"].value_counts()
vc = vc.reindex(LEVEL_ORDER).fillna(0).astype(int)
fig, ax = plt.subplots(figsize=(7.4, 5.6))
wedges, texts, autotexts = ax.pie(
    vc.values, labels=[f"{k}\n{v}天" for k,v in vc.items()],
    colors=[LEVEL_COLOR[k] for k in vc.index], autopct="%1.1f%%",
    startangle=90, counterclock=False, wedgeprops=dict(width=0.42, edgecolor="white"),
    textprops=dict(fontsize=11))
for at in autotexts:
    at.set_color("white"); at.set_fontsize(10)
ax.set_title("汉中市 2025 年空气质量等级分布（优良率 89.0%）", fontsize=14, pad=12)
fig.tight_layout()
fig.savefig(os.path.join(CHART_DIR, "03_level_donut.png"))
plt.close(fig)

# ---------- 图4 六项污染物月度热力图（逐污染物 min-max 归一化）----------
piv = df.groupby("月份")[POLLUTANTS].mean()
norm_piv = piv.apply(lambda s: (s - s.min()) / (s.max() - s.min()), axis=0)
fig, ax = plt.subplots(figsize=(10.5, 5.4))
im = ax.imshow(norm_piv.T, cmap="YlOrRd", aspect="auto")
ax.set_xticks(range(12)); ax.set_xticklabels([f"{i}月" for i in range(1,13)])
ax.set_yticks(range(6)); ax.set_yticklabels(POLLUTANTS)
for i in range(6):
    for j in range(12):
        v = norm_piv.iloc[j, i]
        ax.text(j, i, f"{piv.iloc[j,i]:.1f}", ha="center", va="center",
                fontsize=9, color="white" if v > 0.55 else "#333333")
ax.set_title("汉中市 2025 年六项污染物月度均值热力图（深色=浓度高）", fontsize=14, pad=12)
fig.colorbar(im, ax=ax, shrink=0.85, label="归一化浓度")
fig.tight_layout()
fig.savefig(os.path.join(CHART_DIR, "04_monthly_heatmap.png"))
plt.close(fig)

# ---------- 图5 PM2.5 与 PM10 相关性散点 ----------
fig, ax = plt.subplots(figsize=(7.2, 6))
ax.scatter(df["PM2.5"], df["PM10"], s=14, alpha=0.55, color="#2f6fed", edgecolors="none")
k = np.polyfit(df["PM2.5"], df["PM10"], 1)
xs = np.linspace(df["PM2.5"].min(), df["PM2.5"].max(), 50)
ax.plot(xs, np.polyval(k, xs), color="#E74C3C", lw=2, ls="--", label=f"拟合 y={k[0]:.2f}x{k[1]:+.1f}")
r = df["PM2.5"].corr(df["PM10"])
ax.text(0.03, 0.95, f"Pearson r = {r:.3f}", transform=ax.transAxes,
        fontsize=12, bbox=dict(boxstyle="round,pad=0.4", fc="#fff3cd", ec="#e6a23c"))
ax.set_xlabel("PM2.5 (ug/m3)"); ax.set_ylabel("PM10 (ug/m3)")
ax.set_title("PM2.5 与 PM10 浓度相关分析", fontsize=14, pad=12)
ax.legend(frameon=False)
ax.grid(alpha=0.25)
fig.tight_layout()
fig.savefig(os.path.join(CHART_DIR, "05_corr_pm25_pm10.png"))
plt.close(fig)

# ---------- 图6 四季污染物雷达图（min-max 归一化）----------
season_piv = df.groupby("季节")[POLLUTANTS].mean().reindex(["春","夏","秋","冬"])
smin = season_piv.min(); smax = season_piv.max()
sn = (season_piv - smin) / (smax - smin)
angles = np.linspace(0, 2*np.pi, 6, endpoint=False).tolist()
angles += angles[:1]
fig, ax = plt.subplots(figsize=(7.4, 6.4), subplot_kw=dict(polar=True))
for season, c in zip(["春","夏","秋","冬"], ["#67C23A","#F56C6C","#E6A23C","#2f6fed"]):
    vals = sn.loc[season].tolist(); vals += vals[:1]
    ax.plot(angles, vals, lw=1.8, label=f"{season}（AQI均值 {df[df['季节']==season]['AQI'].mean():.0f}）", color=c)
    ax.fill(angles, vals, color=c, alpha=0.10)
ax.set_xticks(angles[:-1]); ax.set_xticklabels(POLLUTANTS, fontsize=11)
ax.set_ylim(0, 1.05)
ax.set_title("四季六项污染物浓度形态对比（归一化）", fontsize=14, pad=22)
ax.legend(loc="lower right", bbox_to_anchor=(1.28, -0.05), frameon=False, fontsize=10)
fig.tight_layout()
fig.savefig(os.path.join(CHART_DIR, "06_season_radar.png"))
plt.close(fig)

# ---------- 图7 首要污染物占比 ----------
prim = df[df["AQI"] > 50]["首要污染物"].value_counts()
order = prim.index.tolist()
fig, ax = plt.subplots(figsize=(8.6, 5))
bars = ax.bar(order, prim.values, color=["#2f6fed","#E6A23C","#67C23A"])
for b, v in zip(bars, prim.values):
    ax.text(b.get_x()+b.get_width()/2, v+1, f"{v}天", ha="center", fontsize=11)
ax.set_title("汉中市 2025 年非优良日首要污染物分布（共 %d 天）" % int((df["AQI"]>50).sum()), fontsize=14, pad=12)
ax.set_ylabel("天数")
ax.grid(axis="y", alpha=0.25)
fig.tight_layout()
fig.savefig(os.path.join(CHART_DIR, "07_primary_pollutant.png"))
plt.close(fig)

# ---------- 图8 AQI 月度箱线图 ----------
fig, ax = plt.subplots(figsize=(11, 4.8))
data = [df[df["月份"]==m]["AQI"].values for m in range(1,13)]
bp = ax.boxplot(data, tick_labels=[f"{i}月" for i in range(1,13)], patch_artist=True,
                medianprops=dict(color="#E74C3C", lw=1.8))
for patch in bp["boxes"]:
    patch.set_facecolor("#bcd0f7"); patch.set_alpha(0.75)
ax.plot(range(1,13), df.groupby("月份")["AQI"].mean().values, "o-", color="#E67E22", label="月均 AQI")
ax.axhline(50, color="#67C23A", ls="--", lw=0.8); ax.axhline(100, color="#409EFF", ls="--", lw=0.8)
ax.set_title("汉中市 2025 年 AQI 月度分布箱线图", fontsize=14, pad=12)
ax.set_ylabel("AQI"); ax.set_xlabel("月份")
ax.legend(frameon=False)
ax.grid(axis="y", alpha=0.25)
fig.tight_layout()
fig.savefig(os.path.join(CHART_DIR, "08_aqi_boxplot.png"))
plt.close(fig)

print("charts generated:", sorted(os.listdir(CHART_DIR)))
