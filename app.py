# -*- coding: utf-8 -*-
"""
汉中市 2025 年城市空气质量数据分析 —— Streamlit 交互式驾驶舱
运行：lc_env 下执行  streamlit run app.py
数据来源：天气后报（tianqihoubao.com）汉中市 2025 年逐日监测记录
"""
import os
import io
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ---------- 页面配置 ----------
st.set_page_config(
    page_title="汉中城市空气质量数据分析",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE, "hanzhong_aqi_2025_analyzed.csv")

LEVEL_ORDER = ["优", "良", "轻度污染", "中度污染", "重度污染", "严重污染"]
LEVEL_COLOR = {"优": "#67C23A", "良": "#409EFF", "轻度污染": "#E6A23C",
               "中度污染": "#F56C6C", "重度污染": "#9C27B0", "严重污染": "#7A1F1F"}
POLLUTANTS = ["PM2.5", "PM10", "NO2", "SO2", "CO", "O3"]
POLLUTANT_UNIT = {"PM2.5": "ug/m3", "PM10": "ug/m3", "NO2": "ug/m3",
                  "SO2": "ug/m3", "CO": "mg/m3", "O3": "ug/m3"}
SEASON_ORDER = ["春", "夏", "秋", "冬"]

TEMPLATE = "plotly_white"
COLOR_MAIN = "#2f6fed"


# ---------- 数据加载 ----------
@st.cache_data(ttl=3600)
def load_data():
    df = pd.read_csv(DATA_PATH, encoding="utf-8-sig")
    df["日期"] = pd.to_datetime(df["日期"])
    df["月份"] = df["日期"].dt.month
    df["季节"] = df["月份"].map({12: "冬", 1: "冬", 2: "冬", 3: "春", 4: "春", 5: "春",
                                6: "夏", 7: "夏", 8: "夏", 9: "秋", 10: "秋", 11: "秋"})
    df["星期"] = df["日期"].dt.day_name(locale="zh_CN")
    df["年-月"] = df["日期"].dt.strftime("%Y-%m")
    return df


df_all = load_data()

# ---------- 侧边栏筛选 ----------
st.sidebar.title("筛选控制")
st.sidebar.caption("数据范围：2025-01-01 ~ 2025-12-31，共 365 天")

# 日期范围：快捷预设 + 两个独立日期选择器
# （st.date_input 的区间模式在部分 Streamlit 版本上无法正常选取结束日期，故拆分实现）
from datetime import date as _date

MIN_D = df_all["日期"].min().date()
MAX_D = df_all["日期"].max().date()
PRESETS = {
    "全年": (MIN_D, MAX_D),
    "上半年": (_date(2025, 1, 1), _date(2025, 6, 30)),
    "下半年": (_date(2025, 7, 1), _date(2025, 12, 31)),
    "第一季度": (_date(2025, 1, 1), _date(2025, 3, 31)),
    "第二季度": (_date(2025, 4, 1), _date(2025, 6, 30)),
    "第三季度": (_date(2025, 7, 1), _date(2025, 9, 30)),
    "第四季度": (_date(2025, 10, 1), _date(2025, 12, 31)),
    "近30天": (_date(2025, 12, 2), MAX_D),
    "自定义": None,
}
if "d_start" not in st.session_state:
    st.session_state.d_start = MIN_D
if "d_end" not in st.session_state:
    st.session_state.d_end = MAX_D
if "preset_epoch" not in st.session_state:
    st.session_state.preset_epoch = 0

# 快捷范围被点击时（on_change 回调只在控件值真正变化时触发一次），把日期写回预设区间。
# 同时递增 preset_epoch：给日期控件换新 key 强制重挂载。
# 原因：Streamlit 1.64 的 date_input（React Aria DateField）在"程序化写值后"会残留旧的
# 内部状态，下一次用户手选日期时会把另一个字段重置回初始值；重挂载可彻底规避。
def _apply_preset():
    _p = st.session_state.get("preset")
    if PRESETS.get(_p) is not None:
        st.session_state.d_start, st.session_state.d_end = PRESETS[_p]
        st.session_state.preset_epoch += 1


preset = st.sidebar.segmented_control(
    "快捷范围", list(PRESETS.keys()), default="全年", key="preset",
    on_change=_apply_preset)

c1, c2 = st.sidebar.columns(2)
_ep = st.session_state.preset_epoch
d_start = c1.date_input("开始日期", value=st.session_state.d_start,
                        min_value=MIN_D, max_value=MAX_D, key=f"ds_{_ep}")
d_end = c2.date_input("结束日期", value=st.session_state.d_end,
                      min_value=MIN_D, max_value=MAX_D, key=f"de_{_ep}")
if d_start > d_end:
    d_start, d_end = d_end, d_start
d0, d1 = pd.Timestamp(d_start), pd.Timestamp(d_end)

seasons = st.sidebar.multiselect("季节", SEASON_ORDER, default=SEASON_ORDER)
months = st.sidebar.multiselect("月份", list(range(1, 13)), default=list(range(1, 13)))

df = df_all[(df_all["日期"] >= d0) & (df_all["日期"] <= d1)]
df = df[df["季节"].isin(seasons) & df["月份"].isin(months)].copy()

st.sidebar.markdown("---")
st.sidebar.caption(
    "数据来源：天气后报（tianqihoubao.com）汉中市逐日监测值（24 小时均值），"
    "仅供参考；AQI 等级依据《环境空气质量指数（AQI）技术规定》（HJ 633—2012）。"
)

# ---------- 顶部标题 ----------
st.title("汉中城市空气质量检测数据分析")
st.caption("汉中市 2025 年逐日监测 · 筛选后样本 {} 天（占全年 {:.1f}%）".format(
    len(df), len(df) / len(df_all) * 100))

if df.empty:
    st.warning("当前筛选条件下没有数据，请调整侧边栏筛选。")
    st.stop()


# ---------- 通用指标计算 ----------
def kpi_values(d):
    good = d["质量等级"].isin(["优", "良"]).sum()
    return {
        "样本天数": len(d),
        "年均AQI": d["AQI"].mean(),
        "优良天数": good,
        "优良率": good / len(d) * 100,
        "PM2.5年均": d["PM2.5"].mean(),
        "首要污染物Top": (d[d["AQI"] > 50]["首要污染物"].value_counts().idxmax()
                         if (d["AQI"] > 50).any() else "无"),
        "重度及以上天数": d["质量等级"].isin(["重度污染", "严重污染"]).sum(),
    }


# ============================================================
# 标签页 1：总览驾驶舱
# ============================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["总览驾驶舱", "污染物分析", "相关性分析", "日历热力图", "数据浏览"])

with tab1:
    kpi = kpi_values(df)
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("样本天数", f"{kpi['样本天数']} 天")
    c2.metric("年均 AQI", f"{kpi['年均AQI']:.1f}")
    c3.metric("优良天数 / 优良率", f"{kpi['优良天数']} 天 / {kpi['优良率']:.1f}%")
    c4.metric("PM2.5 年均浓度", f"{kpi['PM2.5年均']:.1f} ug/m3")
    c5.metric("重度及以上天数", f"{kpi['重度及以上天数']} 天")

    st.markdown("#### AQI 逐日变化趋势")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["日期"], y=df["AQI"], mode="lines", name="AQI",
        line=dict(color=COLOR_MAIN, width=1.4),
        hovertemplate="%{x|%Y-%m-%d}<br>AQI=%{y}<extra></extra>"))
    for yv, name, col in [(50, "优(50)", "#67C23A"), (100, "良(100)", "#409EFF"),
                          (150, "轻度(150)", "#E6A23C"), (200, "中度(200)", "#F56C6C"),
                          (300, "重度(300)", "#9C27B0")]:
        fig.add_hline(y=yv, line_dash="dot", line_color=col, opacity=0.6,
                      annotation_text=name, annotation_position="right")
    fig.update_layout(
        template=TEMPLATE, height=420, margin=dict(l=10, r=10, t=30, b=10),
        xaxis_title="日期", yaxis_title="AQI",
        hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

    left, right = st.columns([1, 1.2])
    with left:
        st.markdown("#### 空气质量等级分布")
        vc = df["质量等级"].value_counts().reindex(LEVEL_ORDER).fillna(0).astype(int)
        fig = go.Figure(go.Pie(
            labels=vc.index, values=vc.values,
            hole=0.45, marker=dict(colors=[LEVEL_COLOR[k] for k in vc.index]),
            textinfo="label+value+percent", sort=False))
        fig.update_layout(template=TEMPLATE, height=380, showlegend=False,
                          margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig, use_container_width=True)
    with right:
        st.markdown("#### 非优良日首要污染物")
        sub = df[df["AQI"] > 50]
        if not sub.empty:
            prim = sub["首要污染物"].value_counts().reset_index()
            prim.columns = ["污染物", "天数"]
            fig = px.bar(prim, x="污染物", y="天数", color="污染物",
                         color_discrete_sequence=[COLOR_MAIN, "#E6A23C", "#67C23A", "#F56C6C"],
                         text="天数")
            fig.update_layout(template=TEMPLATE, height=380, showlegend=False,
                              margin=dict(l=10, r=10, t=30, b=10))
            fig.update_traces(textposition="outside")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("当前筛选范围内无非优良日。")

    st.markdown("#### 核心结论")
    st.markdown(
        "- **总体良好**：筛选样本优良率 {:.1f}%，年均 AQI {:.1f}，空气质量以优、良为主。\n"
        "- **季节特征明显**：冬季（12–2 月）AQI 与颗粒物浓度显著升高，夏季最低；夏季臭氧（O3）为首要污染物。\n"
        "- **极端过程**：1 月出现多轮静稳天气重污染过程，4 月 12 日出现沙尘天气（AQI 300、PM10 1302 ug/m3）。".format(
            kpi["优良率"], kpi["年均AQI"]))

# ============================================================
# 标签页 2：污染物分析
# ============================================================
with tab2:
    st.markdown("#### 月度污染物平均浓度对比")
    sel_p = st.multiselect("选择污染物（可多选）", POLLUTANTS, default=["PM2.5", "PM10", "O3"])
    if sel_p:
        monthly = df.groupby("月份")[sel_p].mean().reindex(range(1, 13)).reset_index()
        fig = go.Figure()
        for p in sel_p:
            fig.add_trace(go.Bar(
                x=monthly["月份"], y=monthly[p], name=p,
                hovertemplate="%{x}月 %{y:.1f} " + POLLUTANT_UNIT[p] + "<extra></extra>"))
        fig.update_layout(
            template=TEMPLATE, height=430, barmode="group",
            margin=dict(l=10, r=10, t=30, b=10),
            xaxis=dict(tickmode="array", tickvals=list(range(1, 13)), ticktext=[f"{i}月" for i in range(1, 13)]),
            yaxis_title="浓度", legend=dict(orientation="h", y=1.12))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("请至少选择一种污染物。")

    st.markdown("#### 六项污染物月度均值热力图")
    piv = df.groupby("月份")[POLLUTANTS].mean().reindex(range(1, 13))
    z = piv.T.values
    fig = go.Figure(go.Heatmap(
        z=z, x=[f"{i}月" for i in range(1, 13)], y=POLLUTANTS,
        colorscale="YlOrRd", zmin=0,
        text=[[f"{v:.1f}" for v in row] for row in z],
        texttemplate="%{text}", textfont=dict(size=11),
        hovertemplate="%{y} · %{x}：%{z:.1f}<extra></extra>"))
    fig.update_layout(template=TEMPLATE, height=460,
                      margin=dict(l=10, r=10, t=30, b=10),
                      yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### AQI 月度分布箱线图")
    fig = go.Figure()
    for m in range(1, 13):
        vals = df[df["月份"] == m]["AQI"]
        if len(vals) == 0:
            continue
        fig.add_trace(go.Box(y=vals, name=f"{m}月", boxpoints="outliers",
                             marker_color=COLOR_MAIN, line=dict(width=1)))
    fig.update_layout(template=TEMPLATE, height=430,
                      margin=dict(l=10, r=10, t=30, b=10),
                      yaxis_title="AQI", showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# ============================================================
# 标签页 3：相关性分析
# ============================================================
with tab3:
    corr = df[POLLUTANTS + ["AQI"]].corr()
    st.markdown("#### 污染物相关系数矩阵（Pearson）")
    fig = go.Figure(go.Heatmap(
        z=corr.values, x=corr.columns, y=corr.index,
        colorscale="RdYlBu_r", zmin=-1, zmax=1,
        text=[[f"{v:.2f}" for v in row] for row in corr.values],
        texttemplate="%{text}", textfont=dict(size=11),
        hovertemplate="%{y} ↔ %{x}：%{z:.3f}<extra></extra>"))
    fig.update_layout(template=TEMPLATE, height=520,
                      margin=dict(l=10, r=10, t=30, b=10),
                      yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### 双变量散点分析")
    c1, c2 = st.columns(2)
    px_, py_ = c1.selectbox("X 轴污染物", POLLUTANTS + ["AQI"], index=0), \
               c2.selectbox("Y 轴污染物", POLLUTANTS + ["AQI"], index=1)
    if px_ != py_:
        xx, yy = df[px_], df[py_]
        k, b = np.polyfit(xx, yy, 1)
        r = xx.corr(yy)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=xx, y=yy, mode="markers", name="样本",
            marker=dict(size=7, color=df["AQI"], colorscale="Viridis",
                        colorbar=dict(title="AQI"), opacity=0.75),
            text=df["日期"].dt.strftime("%Y-%m-%d"),
            hovertemplate="%{text}<br>%{xaxis.title.text}=%{x}，%{yaxis.title.text}=%{y}<extra></extra>"))
        xs = np.linspace(xx.min(), xx.max(), 60)
        fig.add_trace(go.Scatter(x=xs, y=k * xs + b, mode="lines", name="拟合线",
                                 line=dict(color="#E74C3C", dash="dash")))
        fig.update_layout(
            template=TEMPLATE, height=480,
            xaxis_title=f"{px_} ({POLLUTANT_UNIT[px_]})", yaxis_title=f"{py_} ({POLLUTANT_UNIT[py_]})",
            annotations=[dict(x=0.02, y=0.98, xref="paper", yref="paper", showarrow=False,
                              text=f"Pearson r = {r:.3f} · y = {k:.2f}x {b:+.1f}",
                              bgcolor="#fff3cd", bordercolor="#e6a23c")],
            margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("请选择两个不同的污染物进行对比。")

# ============================================================
# 标签页 4：日历热力图
# ============================================================
with tab4:
    st.markdown("#### 全年 AQI 日历热力图（按星期分布）")
    week_order = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    d = df.copy()
    d["星期"] = pd.Categorical(d["日期"].dt.day_name(locale="zh_CN"), categories=week_order, ordered=True)
    fig = go.Figure(go.Heatmap(
        z=d["AQI"], x=d["日期"], y=d["星期"],
        colorscale=[[0, "#67C23A"], [0.15, "#409EFF"], [0.3, "#E6A23C"],
                    [0.5, "#F56C6C"], [0.75, "#9C27B0"], [1, "#7A1F1F"]],
        zmin=0, zmax=300,
        customdata=np.stack([d["日期"].dt.strftime("%Y-%m-%d"), d["质量等级"]], axis=-1),
        hovertemplate="%{customdata[0]}（%{y}）<br>AQI=%{z} · %{customdata[1]}<extra></extra>"))
    fig.update_layout(
        template=TEMPLATE, height=420,
        margin=dict(l=10, r=10, t=30, b=10),
        xaxis=dict(tickformat="%m月", dtick="M1"),
        yaxis=dict(autorange="reversed", title=""),
        coloraxis_colorbar=dict(title="AQI"))
    st.plotly_chart(fig, use_container_width=True)
    st.caption("颜色由绿到紫代表 AQI 由低到高；该图展示各日期落在星期几的污染强度分布，便于观察周末与工作日差异。")

    st.markdown("#### 月度污染天数堆叠图")
    cnt = df.groupby(["月份", "质量等级"]).size().reset_index(name="天数")
    cnt["质量等级"] = pd.Categorical(cnt["质量等级"], categories=LEVEL_ORDER, ordered=True)
    cnt = cnt.sort_values("月份")
    fig = px.bar(cnt, x="月份", y="天数", color="质量等级",
                 category_orders={"质量等级": LEVEL_ORDER},
                 color_discrete_map=LEVEL_COLOR,
                 labels={"月份": "月份", "天数": "天数"})
    fig.update_layout(template=TEMPLATE, height=420,
                      xaxis=dict(tickmode="array", tickvals=list(range(1, 13)),
                                 ticktext=[f"{i}月" for i in range(1, 13)]),
                      legend=dict(orientation="h", y=1.12),
                      margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig, use_container_width=True)

# ============================================================
# 标签页 5：数据浏览
# ============================================================
with tab5:
    st.markdown("#### 筛选后明细数据")
    show_cols = ["日期", "AQI", "质量等级", "首要污染物", "PM2.5", "PM10", "NO2", "SO2", "CO", "O3"]
    view = df[show_cols].sort_values("日期").copy()
    view["日期"] = view["日期"].dt.strftime("%Y-%m-%d")
    st.dataframe(view, use_container_width=True, height=430)

    st.markdown("#### 描述性统计")
    st.dataframe(df[["AQI", "PM2.5", "PM10", "NO2", "SO2", "CO", "O3"]]
                 .describe().round(2), use_container_width=True)

    csv_buf = io.StringIO()
    df[show_cols].to_csv(csv_buf, index=False, encoding="utf-8-sig")
    st.download_button("下载筛选数据 (CSV)", data=csv_buf.getvalue().encode("utf-8-sig"),
                       file_name="hanzhong_aqi_filtered.csv", mime="text/csv")

st.sidebar.markdown("---")
st.sidebar.caption("制作：汉中城市空气质量检测数据分析 · Streamlit + Plotly")
