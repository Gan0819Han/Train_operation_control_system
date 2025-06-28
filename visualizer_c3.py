# visualizer_c3.py
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
from config import MS_TO_KMH

def set_chinese_font():
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
    plt.rcParams['axes.unicode_minus'] = False

def plot_c3_results():
    try:
        data = np.load('c3_simulation_results.npz')
    except FileNotFoundError:
        print("错误: 未找到 'c3_simulation_results.npz'。请先运行 simulation_c3.py。")
        return

    fig, ax1 = plt.subplots(figsize=(18, 9))
    set_chinese_font()

    pos_km = data['position'] / 1000.0
    
    # 绘制速度曲线 (左Y轴)
    ax1.plot(pos_km, data['velocity'] * MS_TO_KMH, 'k-', label='列车实际速度', lw=2.5)
    ax1.set_xlabel('距离 (km)', fontsize=16)
    ax1.set_ylabel('速度 (km/h)', fontsize=16, color='k')
    ax1.tick_params(axis='y', labelcolor='k')
    ax1.grid(True, linestyle='--', alpha=0.6)
    ax1.set_ylim(bottom=0)

    # 创建第二个Y轴，用于显示EOA的变化
    ax2 = ax1.twinx()
    ax2.plot(pos_km, data['eoa'] / 1000.0, 'b--', label='行车许可终点 (EOA)', lw=2)
    ax2.set_ylabel('EOA位置 (km)', fontsize=16, color='b')
    ax2.tick_params(axis='y', labelcolor='b')
    
    fig.suptitle('CTCS-3级动态授权仿真图', fontsize=20)
    # 合并图例
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2, loc='center right', fontsize=14)
    
    plt.savefig("c3_simulation_chart.png", dpi=300)
    print("CTCS-3仿真图表已保存。")
    plt.show()

if __name__ == '__main__':
    plot_c3_results()