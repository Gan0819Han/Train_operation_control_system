# visualizer.py
# -*- coding: utf-8 -*-

"""
结果可视化与对比分析模块。
作为主程序运行，组织多次仿真并生成对比图表。
"""
import numpy as np
import matplotlib.pyplot as plt
from config import MS_TO_KMH
from simulation import run_simulation # 导入仿真函数

def set_chinese_font():
    """
    查找并设置一个可用的中文字体，以解决图表中文显示为方框的问题。
    """
    try:
        # 优先使用更现代、跨平台的黑体
        plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'PingFang SC', 'WenQuanYi Micro Hei']
        plt.rcParams['axes.unicode_minus'] = False  # 解决负号'-'显示为方块的问题
        # 尝试绘制一个简单的中文图例来测试字体是否生效
        fig, ax = plt.subplots()
        ax.plot([0, 1], [0, 1], label='测试')
        ax.legend()
        plt.close(fig)
        print("中文字体设置成功。")
    except Exception:
        print("警告：未能自动设置中文字体。图表中的中文可能无法正常显示。")
        # 如果找不到，也设置一下负号，避免报错
        plt.rcParams['axes.unicode_minus'] = False


def plot_velocity_comparison(log_eff, log_es):
    """绘制两种策略下的速度-距离对比图"""
    plt.figure(figsize=(18, 9))

    # 绘制一次ATP安全包络线 (两条策略下都一样)
    pos_km = log_eff['position'] / 1000.0
    plt.plot(pos_km, log_eff['ebi_v'] * MS_TO_KMH, 'r-', label='紧急制动触发曲线 (EBI)', lw=1.5, alpha=0.8)
    plt.plot(pos_km, log_eff['sbi_v'] * MS_TO_KMH, 'y-', label='常用制动触发曲线 (SBI)', lw=1.5, alpha=0.8)
    plt.plot(pos_km, log_eff['mrsp'] * MS_TO_KMH, color='gray', linestyle=':', label='最严格限制速度 (MRSP)', lw=2)

    # 绘制两种策略的实际速度轨迹
    plt.plot(pos_km, log_eff['velocity'] * MS_TO_KMH, 'k-', label='实际速度 (效率优先)', lw=2.5)
    plt.plot(log_es['position'] / 1000.0, log_es['velocity'] * MS_TO_KMH, 'g--', label='实际速度 (节能优先)', lw=2.5)

    # 图表美化
    plt.title('不同驾驶策略下的速度监控对比图', fontsize=20)
    plt.xlabel('距离 (km)', fontsize=16)
    plt.ylabel('速度 (km/h)', fontsize=16)
    plt.legend(fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.xlim(left=0)
    plt.ylim(bottom=0)
    plt.tight_layout()
    plt.savefig("velocity_comparison_chart.png", dpi=300)
    print("速度对比图已保存为 'velocity_comparison_chart.png'")
    plt.show()

def plot_energy_comparison(log_eff, log_es):
    """绘制两种策略下的能耗-距离对比图"""
    plt.figure(figsize=(18, 9))

    # 绘制能耗曲线
    plt.plot(log_eff['position'] / 1000.0, log_eff['energy'] / 1e6, 'k-', label='累计能耗 (效率优先)', lw=2.5)
    plt.plot(log_es['position'] / 1000.0, log_es['energy'] / 1e6, 'g--', label='累计能耗 (节能优先)', lw=2.5)

    # 图表美化
    plt.title('不同驾驶策略下的累计能耗对比图', fontsize=20)
    plt.xlabel('距离 (km)', fontsize=16)
    plt.ylabel('累计能耗 (兆焦耳-MJ)', fontsize=16)
    plt.legend(fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.xlim(left=0)
    plt.ylim(bottom=0)
    plt.tight_layout()
    plt.savefig("energy_comparison_chart.png", dpi=300)
    print("能耗对比图已保存为 'energy_comparison_chart.png'")
    plt.show()


if __name__ == '__main__':
    # --- 优先设置中文字体 ---
    set_chinese_font()

    # --- 运行两次仿真，获取不同策略的结果 ---
    log_efficiency = run_simulation(strategy='efficiency')
    log_energy_saving = run_simulation(strategy='energy_saving')

    # --- 绘制对比图表 ---
    plot_velocity_comparison(log_efficiency, log_energy_saving)
    plot_energy_comparison(log_efficiency, log_energy_saving)

