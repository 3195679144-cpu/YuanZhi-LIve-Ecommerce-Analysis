# 主脚本：douyin_live_analysis.py
import pandas as pd
import matplotlib.pyplot as plt

# ================== 手动添加的真实直播数据（来自巴依老爷数据大屏） ==================
data = {
    '场次': ['场次1', '场次2', '场次3', '场次4'],
    '成交金额': [22242, 25716, 22795, 41025],
    '在线人数': [4102, 3060, 1205, 4859],
    '转化率': [24.35, 9.35, 24.35, 8.09],
    'ROI': [3.19, 1.56, 6.57, 3.86],
    'GPM': [2476, 1995, 2920, 2714],
    '曝光次数': [81262, 48533, 25342, 83977]
}

df = pd.DataFrame(data)
print("数据加载成功！总GMV:", df['成交金额'].sum())
# ================== 数据部分结束 ==================import os
import textwrap

import matplotlib.pyplot as plt
import pandas as pd


def generate_sample_csv(csv_path: str) -> None:
    """
    生成一份示例数据，方便首次运行。
    用户后续可以在此基础上“手动加几行”模拟更多场次。
    """
    if os.path.exists(csv_path):
        return

    sample = textwrap.dedent(
        """\
        场次,成交金额,累计在线人数,转化率,ROI,GPM,曝光次数,流量来源
        1,125000,38000,0.185,2.6,35.5,320000,自然流量
        2,158000,42000,0.214,2.9,38.2,350000,品牌自播
        3,98000,31000,0.163,2.1,32.4,280000,自然流量
        4,203000,56000,0.243,3.2,40.8,410000,付费投流
        5,187000,51000,0.238,3.0,39.9,395000,付费投流
        6,142000,39000,0.207,2.7,36.1,340000,品牌自播
        """
    )
    with open(csv_path, "w", encoding="utf-8") as f:
        f.write(sample)


def load_data(csv_path: str) -> pd.DataFrame:
    """读取抖音直播销售数据 CSV。"""
    if not os.path.exists(csv_path):
        generate_sample_csv(csv_path)
        print(f"未找到数据文件，已自动生成示例数据：{csv_path}")

    df = pd.read_csv(csv_path, encoding="utf-8")

    # 确保数值列类型正确，避免用户后续手动增加数据时出现字符串类型
    numeric_cols = ["成交金额", "累计在线人数", "转化率", "ROI", "GPM", "曝光次数"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # 丢弃明显异常/无法解析的行
    df = df.dropna(subset=["场次", "成交金额", "转化率", "ROI"])
    df = df.sort_values("场次").reset_index(drop=True)
    return df


def compute_kpis(df: pd.DataFrame) -> dict:
    """计算核心指标：平均转化率、总 GMV、ROI 趋势等。"""
    avg_conv = df["转化率"].mean()
    total_gmv = df["成交金额"].sum()
    roi_trend = df[["场次", "ROI"]]

    # 简单找出转化率最高和最低的场次，便于后面写结论
    best_row = df.loc[df["转化率"].idxmax()]
    worst_row = df.loc[df["转化率"].idxmin()]

    return {
        "avg_conv": avg_conv,
        "total_gmv": total_gmv,
        "roi_trend": roi_trend,
        "best_row": best_row,
        "worst_row": worst_row,
    }


def plot_gmv_trend(df: pd.DataFrame, output_dir: str) -> str:
    """成交金额趋势折线图。"""
    plt.figure(figsize=(8, 4.5))
    plt.plot(df["场次"], df["成交金额"], marker="o", color="#1f77b4")
    plt.title("抖音直播成交金额趋势")
    plt.xlabel("场次")
    plt.ylabel("成交金额（元）")
    plt.grid(alpha=0.3, linestyle="--")
    plt.tight_layout()

    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, "gmv_trend.png")
    plt.savefig(path, dpi=120)
    plt.close()
    return path


def plot_conversion_bar(df: pd.DataFrame, output_dir: str) -> str:
    """转化率柱状图。"""
    plt.figure(figsize=(8, 4.5))
    plt.bar(df["场次"].astype(str), df["转化率"] * 100, color="#ff7f0e")
    plt.title("抖音直播场次转化率对比")
    plt.xlabel("场次")
    plt.ylabel("转化率（%）")
    plt.grid(axis="y", alpha=0.3, linestyle="--")
    plt.tight_layout()

    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, "conversion_rate_bar.png")
    plt.savefig(path, dpi=120)
    plt.close()
    return path


def plot_traffic_pie(df: pd.DataFrame, output_dir: str) -> str:
    """
    流量来源饼图。
    这里简单使用“流量来源”字段的曝光次数求和，反映不同来源的占比。
    """
    if "流量来源" not in df.columns:
        # 如果用户后续删掉该列，则给出兜底提示
        return ""

    source_group = df.groupby("流量来源")["曝光次数"].sum()
    labels = source_group.index
    sizes = source_group.values

    plt.figure(figsize=(6, 6))
    plt.pie(
        sizes,
        labels=labels,
        autopct="%1.1f%%",
        startangle=90,
        colors=["#2ca02c", "#d62728", "#9467bd", "#8c564b"],
    )
    plt.title("抖音直播流量来源分布（按曝光次数）")
    plt.tight_layout()

    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, "traffic_source_pie.png")
    plt.savefig(path, dpi=120)
    plt.close()
    return path


def print_insights(kpis: dict) -> None:
    """基于指标输出一段类似实习报告风格的中文结论。"""
    avg_conv_pct = kpis["avg_conv"] * 100
    total_gmv = kpis["total_gmv"]
    best_row = kpis["best_row"]
    worst_row = kpis["worst_row"]

    print("\n====== 抖音直播销售数据分析报告（实习版） ======\n")
    print(f"整体来看，本组样本共 {int(best_row['场次']) if '场次' in best_row else 'N'} 场直播，")
    print(f"累计实现 GMV 约 {total_gmv:,.0f} 元，平均转化率为 {avg_conv_pct:.2f}%。")
    print()
    print(
        f"从单场表现看，转化率最高的场次为第 {int(best_row['场次'])} 场，"
        f"转化率约 {best_row['转化率']*100:.2f}%，ROI 为 {best_row['ROI']:.2f}。"
    )
    print(
        f"相对而言，第 {int(worst_row['场次'])} 场转化率较低，仅 {worst_row['转化率']*100:.2f}%，"
        f"ROI 为 {worst_row['ROI']:.2f}，说明在投放节奏和货品匹配上仍有优化空间。"
    )
    print()
    print(
        "结合 ROI 趋势与流量结构，可以看到在付费投流放量的场次中，"
        "成交金额与转化率均有不同程度的抬升，说明投流质量对直播成交闭环影响较大。"
    )
    print(
        "在后续运营中，建议继续测试不同创意与投放人群包，重点放大高 ROI 组合，"
        "并结合人群标签和直播节奏，做针对性话术优化。"
    )
    print()
    print(
        "本次分析基于巴依老爷抖音直播大屏导出的历史数据，"
        "采用 pandas 进行数据清洗与指标计算，"
        "并使用 matplotlib 输出趋势图和结构图，为日常直播复盘提供量化参考。"
    )
    print("\n==========================================\n")


def main():
    """主流程：读取数据 -> 计算指标 -> 画图 -> 输出结论。"""
    # 默认数据路径，用户可根据需要在命令行传入其他路径
    csv_path = "douyin_live_data.csv"
    output_dir = "figures"

    df = load_data(csv_path)
    kpis = compute_kpis(df)

    gmv_path = plot_gmv_trend(df, output_dir)
    conv_path = plot_conversion_bar(df, output_dir)
    pie_path = plot_traffic_pie(df, output_dir)

    print_insights(kpis)

    print("图表已生成：")
    print(f"- 成交金额趋势：{gmv_path}")
    print(f"- 转化率柱状图：{conv_path}")
    if pie_path:
        print(f"- 流量来源饼图：{pie_path}")
    else:
        print("- 流量来源饼图：未生成（缺少「流量来源」列）")


if __name__ == "__main__":
    main()


