# simulation_c3.py
# -*- coding: utf-8 -*-

"""
探究方向二：CTCS-3级与RBC动态授权仿真 (加速版)
"""
import numpy as np
# import time # 不再需要time模块
from config import train_params, track_info, scenario_info
from atp_calculator import ATPCalculator
import copy

class RBC:
    """一个简化的无线闭塞中心(RBC)模拟器"""
    def __init__(self, line_end_position):
        # 修正：RBC初始化时就应知道线路的最终目的地
        self.line_end_position = line_end_position
        self.emergency_triggered = False

    def grant_ma(self, train_position):
        # 模拟RBC根据列车位置授予行车许可(MA)
        ma_length = 10000.0  # 每次授予10km
        eoa_provisional = train_position + ma_length
        
        # 修正：EOA的上限是线路的最终目的地，而不是一个动态变量
        final_eoa = min(eoa_provisional, self.line_end_position)
        
        # 模拟一个突发事件：当列车经过22km后，RBC收到前方线路占用信息，紧急缩短MA
        if train_position > 22000 and not self.emergency_triggered:
            final_eoa = 24000 # 紧急停车目标点
            print(f"RBC紧急通知：前方占用，MA缩短至 {final_eoa}m!")
            self.emergency_triggered = True

        return final_eoa, 0.0 # 目标速度为0

class CommunicationChannel:
    """一个简化的车地通信信道模拟器 (已移除延迟)"""
    def __init__(self):
        pass

    def request_and_receive_ma(self, rbc, train_position):
        return rbc.grant_ma(train_position)

def run_c3_simulation():
    print("--- 开始CTCS-3级动态授权仿真 (加速版) ---")
    dt = 0.1
    
    # 修正：在仿真开始前，保存原始的、最终的EOA
    original_eoa_from_config = scenario_info.eoa_position
    
    # 修正：用线路的最终目的地来初始化RBC
    rbc = RBC(line_end_position=original_eoa_from_config)
    comm_channel = CommunicationChannel()

    # 初始化列车和ATP
    position, velocity = 0.0, 0.0
    # 初始MA：从RBC获取第一次授权
    current_eoa, _ = rbc.grant_ma(position)
    
    # 修正：为ATP计算器创建一个独立的、可动态修改的场景对象
    dynamic_scenario = copy.deepcopy(scenario_info)
    dynamic_scenario.eoa_position = current_eoa
    atp = ATPCalculator(train_params, track_info, dynamic_scenario)
    
    log = {'time': [], 'position': [], 'velocity': [], 'eoa': []}
    
    last_request_pos = -1 # 用于防止在同一点重复请求

    for step in range(int(600 / dt)): # 仿真600秒
        # 动态更新ATP计算器中的场景信息
        atp.scenario.eoa_position = current_eoa
        
        mrsp = atp.calculate_mrsp(position)
        _, _, v_sbi, v_ebi = atp.calculate_dynamic_curves(position)
        sbi_final = min(mrsp, v_sbi)
        ebi_final = min(mrsp, v_ebi)

        # 控制逻辑
        if velocity > ebi_final:
            acceleration = -atp.train.a_brake_emergency
        elif velocity > sbi_final:
            acceleration = -atp.train.a_brake_service
        else:
            acceleration = atp.train.a_traction if velocity < mrsp else 0

        # 更新状态
        velocity = max(0, velocity + acceleration * dt)
        position += velocity * dt

        # 记录数据
        log['time'].append(step * dt)
        log['position'].append(position)
        log['velocity'].append(velocity)
        log['eoa'].append(current_eoa)

        # 检查是否需要请求新的MA
        dist_to_current_eoa = current_eoa - position
        if dist_to_current_eoa < 5000 and velocity > 0 and abs(position - last_request_pos) > 100:
            last_request_pos = position
            new_eoa, _ = comm_channel.request_and_receive_ma(rbc, position)
            if new_eoa != current_eoa:
                current_eoa = new_eoa
        
        if position >= current_eoa and velocity < 0.1:
            break
            
    np.savez('c3_simulation_results.npz', **log)
    print("CTCS-3仿真完成，结果已保存。")

if __name__ == '__main__':
    run_c3_simulation()
