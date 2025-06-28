# simulation_multitrain.py
# -*- coding: utf-8 -*-

"""
探究方向三：多列车追踪与行车间隔分析
"""
import numpy as np
from config import train_params, track_info, scenario_info
from atp_calculator import ATPCalculator
import copy

class TrainState:
    """用于存储和管理单个列车状态的类"""
    def __init__(self, train_id):
        self.id = train_id
        self.position = 0.0
        self.velocity = 0.0
        # 每个列车都拥有自己独立的ATP计算器和场景信息
        self.atp = ATPCalculator(train_params, copy.deepcopy(track_info), copy.deepcopy(scenario_info))
        self.log = {'time': [], 'position': [], 'velocity': []}

    def update_log(self, time_now):
        """记录当前状态到日志"""
        self.log['time'].append(time_now)
        self.log['position'].append(self.position)
        self.log['velocity'].append(self.velocity)

def run_multitrain_simulation(headway_seconds=120):
    """
    运行多列车追踪仿真。

    Args:
        headway_seconds (int): 后车相对于前车的发车时间间隔（秒）。
    """
    print(f"--- 开始多列车追踪仿真，目标行车间隔: {headway_seconds}s ---")
    dt = 0.1
    safety_distance = 500  # 后车与前车必须保持的最小物理距离 (m)

    # 初始化两辆列车
    train1 = TrainState(train_id=1)
    train2 = TrainState(train_id=2)
    trains = [train1, train2]

    # 主仿真循环
    for step in range(int(800 / dt)):  # 仿真800秒
        time_now = step * dt

        # 只有当时间到达时，第二辆车才开始启动
        if time_now < headway_seconds and train2.position == 0:
            active_trains = [train1]
        else:
            active_trains = trains

        for i, train in enumerate(active_trains):
            # 1. 确定当前列车的目标(EOA)
            if train.id == 1:  # 前车的目标是线路终点
                train.atp.scenario.eoa_position = scenario_info.eoa_position
            else:  # 后车的目标是前车的位置减去安全距离
                lead_train = active_trains[i-1]
                train.atp.scenario.eoa_position = lead_train.position - safety_distance

            # 2. 计算ATP监控曲线并获取最终限速
            mrsp = train.atp.calculate_mrsp(train.position)
            _, _, v_sbi, v_ebi = train.atp.calculate_dynamic_curves(train.position)
            sbi_final = min(mrsp, v_sbi)
            
            # 3. 应用控制逻辑
            if train.velocity > sbi_final:
                acceleration = -train.atp.train.a_brake_service
            else:
                # 简化逻辑：只要安全就加速到MRSP
                acceleration = train.atp.train.a_traction if train.velocity < mrsp else 0
            
            # 4. 更新列车状态
            train.velocity = max(0, train.velocity + acceleration * dt)
            train.position += train.velocity * dt

            # 5. 记录日志
            train.update_log(time_now)

        # 检查仿真结束条件
        if train1.position >= scenario_info.eoa_position:
            # 确保后车也完成记录
            while len(train2.log['time']) < len(train1.log['time']):
                 train2.update_log(train2.log['time'][-1] + dt)
            break
            
    np.savez('multitrain_results.npz', train1=train1.log, train2=train2.log)
    print("多列车仿真完成，结果已保存。")

if __name__ == '__main__':
    # 您可以修改此处的行车间隔来进行实验
    run_multitrain_simulation(headway_seconds=10)
