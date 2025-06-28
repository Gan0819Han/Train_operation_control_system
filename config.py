# config.py
# -*- coding: utf-8 -*-

"""
仿真配置文件
定义了所有仿真实体（列车、线路、场景）的参数。
"""

# --- 常量定义 ---
KMH_TO_MS = 1 / 3.6  # 公里/小时 到 米/秒 的转换系数
MS_TO_KMH = 3.6      # 米/秒 到 公里/小时 的转换系数

# --- 实体定义 ---

class Train:
    """
    定义列车实体的物理和性能参数。
    这些参数严格参考了课件中的概念。
    """
    def __init__(self):
        # 列车物理属性
        self.length = 400.0  # 列车长度 (米)

        # 列车性能参数
        self.max_velocity = 350.0 * KMH_TO_MS  # 列车最大构造速度 (m/s)
        self.a_traction = 0.5  # 最大牵引加速度 (m/s^2)
        self.a_brake_service = 0.8  # 常用制动减速度 (m/s^2)
        self.a_brake_emergency = 1.2  # 紧急制动减速度 (m/s^2)

        # 安全模型参数 (参考: [4] 列控设备.pdf P17, P21)
        self.t_reaction_driver = 1.0  # 司机反应时间 (秒) - 用于计算告警曲线
        self.t_reaction_atp = 0.5   # ATP系统反应时间 (秒)
        self.t_cutoff = 1.0         # 牵引切除时间 (秒)
        self.t_buildup_sb = 2.0     # 常用制动建立时间 (秒)
        self.t_buildup_eb = 1.5     # 紧急制动建立时间 (秒)


class Track:
    """
    定义线路实体，主要包含静态速度限制(SSP)数据。
    """
    def __init__(self):
        # 静态速度曲线 (Static Speed Profile, SSP)
        # 格式: [起点(m), 终点(m), 限速(km/h), 坡度(千分数, 上坡为正, 下坡为负)]
        # 参考: [4] 列控设备.pdf P9-11
        self.ssp_data = [
            [0, 20000, 350, 0],       # 0-20km, 350km/h, 平坡
            [20000, 25000, 250, 5],   # 20-25km, 250km/h, 5‰上坡
            [25000, 30000, 250, -5],  # 25-30km, 250km/h, 5‰下坡
        ]


class Scenario:
    """
    定义本次仿真的具体运行场景。
    """
    def __init__(self):
        # 行车许可 (Movement Authority, MA)
        # 参考: [2] 列车运行控制系统基.pdf P25
        self.eoa_position = 28000.0  # 行车许可终点 (米)
        self.eoa_speed = 0.0 * KMH_TO_MS  # 终点目标速度 (m/s)

        # 临时限速 (Temporary Speed Restriction, TSR)
        # 格式: [起点(m), 终点(m), 限速(km/h)]
        # 参考: [4] 列控设备.pdf P9
        self.tsr_data = [
            [15000, 18000, 160]
        ]

# --- 实例化配置 ---
# 在其他文件中，可以直接导入这些实例化的对象
train_params = Train()
track_info = Track()
scenario_info = Scenario()

