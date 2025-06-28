# visualizer_multitrain.py
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt

def set_chinese_font():
    """查找并设置一个可用的中文字体"""
    try:
        plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'PingFang SC', 'WenQuanYi Micro Hei']
        plt.rcParams['axes.unicode_minus'] = False
    except Exception:
        print("警告：未能自动设置中文字体。")

def plot_multitrain_results():
    """加载多列车仿真结果并绘制时空图"""
    try:
        data = np.load('multitrain_results.npz', allow_pickle=True)
    except FileNotFoundError:
        print("错误: 未找到 'multitrain_results.npz'。请先运行 simulation_multitrain.py。")
        return
        
    log1 = data['train1'].item()
    log2 = data['train2'].item()
    set_chinese_font()

    # --- 绘制时空图 (Time-Space Diagram) ---
    plt.figure(figsize=(12, 10))
    
    plt.plot(np.array(log1['position']) / 1000.0, log1['time'], 'k-', label='列车 1', lw=2.5)
    plt.plot(np.array(log2['position']) / 1000.0, log2['time'], 'g--', label='列车 2', lw=2.5)
    
    plt.title('多列车追踪运行时空图', fontsize=20)
    plt.xlabel('距离 (km)', fontsize=16)
    plt.ylabel('时间 (s)', fontsize=16)
    plt.legend(fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # 翻转Y轴是时空图的惯例，使时间向下流逝
    plt.gca().invert_yaxis() 
    
    plt.tight_layout()
    plt.savefig("multitrain_timespace_chart.png", dpi=300)
    print("时空图已保存为 'multitrain_timespace_chart.png'。")
    plt.show()

if __name__ == '__main__':
    plot_multitrain_results()
