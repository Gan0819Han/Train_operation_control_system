# simulation.py
# -*- coding: utf-8 -*-

"""
仿真主程序。
被重构为一个可调用的函数，以支持多场景对比。
"""
import numpy as np
from config import train_params, track_info, scenario_info
from atp_calculator import ATPCalculator

def run_simulation(strategy='efficiency'):
    """
    执行单次仿真过程。
    
    Args:
        strategy (str): 驾驶策略。可选值为 'efficiency' 或 'energy_saving'。

    Returns:
        dict: 包含仿真结果的日志字典。
    """
    print(f"正在以 '{strategy}' 策略运行仿真...")
    
    # --- 仿真参数 ---
    dt = 0.1
    total_time = 400
    num_steps = int(total_time / dt)

    # --- 初始化 ---
    atp = ATPCalculator(train_params, track_info, scenario_info)
    position, velocity, acceleration = 0.0, 0.0, 0.0
    energy = 0.0 # 增加能耗记录

    log = {
        'time': [], 'position': [], 'velocity': [], 'acceleration': [],
        'mrsp': [], 'perm_v': [], 'warn_v': [], 'sbi_v': [], 'ebi_v': [],
        'energy': [] # 增加能耗日志
    }

    # --- 主循环 ---
    for step in range(num_steps):
        mrsp = atp.calculate_mrsp(position)
        v_perm, v_warn, v_sbi, v_ebi = atp.calculate_dynamic_curves(position)
        
        sbi_final = min(mrsp, v_sbi)
        ebi_final = min(mrsp, v_ebi)

        # --- 应用新的、可选择的控制逻辑 ---
        if velocity > ebi_final:
            acceleration = -atp.train.a_brake_emergency
        elif velocity > sbi_final:
            acceleration = -atp.train.a_brake_service
        else:
            # 在ATP安全包络内，应用不同的驾驶策略
            if strategy == 'efficiency':
                # 效率优先策略：只要安全就满弓牵引
                if velocity < mrsp:
                    acceleration = atp.train.a_traction
                else:
                    acceleration = 0
            elif strategy == 'energy_saving':
                # 节能策略：达到目标速度后尽可能惰行
                # 设定一个比SBI曲线稍高的惰行触发线
                coast_trigger_speed = sbi_final * 1.05 
                # 如果当前速度远低于触发线，则加速
                if velocity < coast_trigger_speed and velocity < mrsp * 0.98:
                    acceleration = atp.train.a_traction
                else:
                    # 否则进入惰行状态
                    acceleration = 0
        
        # --- 更新状态与能耗 ---
        velocity += acceleration * dt
        velocity = max(0, velocity)
        position += velocity * dt
        
        # 简单能耗模型：只在牵引时消耗能量
        if acceleration > 0:
            power = train_params.a_traction * velocity # 功率 P = F*v, F=m*a, 简化为 P正比于a*v
            energy += power * dt

        # --- 记录数据 ---
        for key, value in [('time', step * dt), ('position', position), ('velocity', velocity), 
                           ('acceleration', acceleration), ('mrsp', mrsp), ('perm_v', min(mrsp, v_perm)), 
                           ('warn_v', min(mrsp, v_warn)), ('sbi_v', sbi_final), ('ebi_v', ebi_final),
                           ('energy', energy)]:
            log[key].append(value)

        if position >= scenario_info.eoa_position and velocity < 0.1:
            break
            
    print(f"'{strategy}' 策略仿真完成。")
    
    for key in log:
        log[key] = np.array(log[key])
        
    return log

