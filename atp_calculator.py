# atp_calculator.py
# -*- coding: utf-8 -*-

"""
ATP (Automatic Train Protection) 核心算法模块。
负责计算MRSP和动态速度监控曲线。
"""
import numpy as np
from config import KMH_TO_MS

G = 9.8  # 重力加速度 (m/s^2)

class ATPCalculator:
    """
    封装所有ATP计算逻辑。
    """
    def __init__(self, train, track, scenario):
        self.train = train
        self.track = track
        self.scenario = scenario

    def get_gradient_at(self, position):
        """根据位置获取线路坡度"""
        for start, end, _, gradient in self.track.ssp_data:
            if start <= position < end:
                return gradient / 1000.0  # 转换为小数
        return 0.0

    def get_ssp_limit_at(self, position):
        """根据位置获取SSP限速"""
        for start, end, speed_kmh, _ in self.track.ssp_data:
            if start <= position < end:
                return speed_kmh * KMH_TO_MS
        return self.train.max_velocity

    def get_tsr_limit_at(self, position):
        """根据位置获取TSR限速"""
        for start, end, speed_kmh in self.scenario.tsr_data:
            if start <= position < end:
                return speed_kmh * KMH_TO_MS
        return float('inf') # 如果没有TSR，则返回无穷大

    def calculate_mrsp(self, position):
        """
        计算在给定位置的最严格限制速度曲线 (MRSP)。
        严格实现 "取最低值" 和 "车尾保持" 原则。
        参考: [4] 列控设备.pdf P11-12
        """
        # 1. 计算车头位置的原始限速
        head_pos = position
        v_ssp = self.get_ssp_limit_at(head_pos)
        v_tsr = self.get_tsr_limit_at(head_pos)
        v_head_limit = min(v_ssp, v_tsr, self.train.max_velocity)

        # 2. 计算车尾位置的原始限速，实现"车尾保持"
        rear_pos = position - self.train.length
        if rear_pos < 0: # 刚发车时，车尾在起点后
            v_rear_limit = v_head_limit
        else:
            v_ssp_rear = self.get_ssp_limit_at(rear_pos)
            v_tsr_rear = self.get_tsr_limit_at(rear_pos)
            v_rear_limit = min(v_ssp_rear, v_tsr_rear, self.train.max_velocity)
        
        # 3. MRSP取车头和车尾限速中的较小值
        mrsp = min(v_head_limit, v_rear_limit)
        return mrsp

    def calculate_dynamic_curves(self, position):
        """
        计算从当前位置到EOA的动态监控曲线簇。
        使用反向积分法，从目标点反向计算制动距离。
        参考: [4] 列控设备.pdf P17, P21
        """
        dist_to_eoa = self.scenario.eoa_position - position
        if dist_to_eoa <= 0:
            return 0, 0, 0, 0 # 如果已越过EOA，所有限速为0

        # --- 紧急制动曲线 (EBI) ---
        # 坡度影响
        gradient_eb = self.get_gradient_at(position) # 简化为使用当前点坡度
        a_eff_eb = self.train.a_brake_emergency - G * gradient_eb
        # 系统延迟距离
        # 简化模型：假设在延迟时间内速度不变
        # 速度v_ebi下的延迟距离 = v_ebi * (t_reaction + t_cutoff + t_buildup)
        # 完整制动距离 = (v_ebi^2 - v_eoa^2) / (2 * a_eff)
        # dist_to_eoa = 延迟距离 + 完整制动距离
        # 这是一个关于v_ebi的二次方程，为简化，我们用迭代法求解
        v_ebi = np.sqrt(max(0, 2 * a_eff_eb * dist_to_eoa + self.scenario.eoa_speed**2))
        delay_time_eb = self.train.t_reaction_atp + self.train.t_cutoff + self.train.t_buildup_eb
        # 迭代求解更精确的v_ebi
        for _ in range(3): # 迭代几次以收敛
            dist_brake = max(0, dist_to_eoa - v_ebi * delay_time_eb)
            v_ebi = np.sqrt(max(0, 2 * a_eff_eb * dist_brake + self.scenario.eoa_speed**2))

        # --- 常用制动曲线 (SBI) ---
        gradient_sb = self.get_gradient_at(position)
        a_eff_sb = self.train.a_brake_service - G * gradient_sb
        v_sbi = np.sqrt(max(0, 2 * a_eff_sb * dist_to_eoa + self.scenario.eoa_speed**2))
        delay_time_sb = self.train.t_reaction_atp + self.train.t_cutoff + self.train.t_buildup_sb
        for _ in range(3):
            dist_brake = max(0, dist_to_eoa - v_sbi * delay_time_sb)
            v_sbi = np.sqrt(max(0, 2 * a_eff_sb * dist_brake + self.scenario.eoa_speed**2))
            
        # --- 告警曲线 (Warning) 和 允许速度曲线 (Permitted) ---
        # 在SBI基础上增加安全裕量
        v_warn = v_sbi - 2 * KMH_TO_MS # 减去2km/h作为裕量
        v_perm = v_sbi - 5 * KMH_TO_MS # 减去5km/h作为裕量

        return max(0, v_perm), max(0, v_warn), max(0, v_sbi), max(0, v_ebi)

