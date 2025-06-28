# 基于Python仿真的列车运行控制系统关键技术研究

本项目是一个基于Python的列车运行控制系统仿真平台，主要研究列车ATP（自动列车保护）系统的关键技术，包括单列车运行控制和多列车追踪控制等场景。

## 项目特点

- 实现了完整的ATP（自动列车保护）系统仿真
- 支持多种列车运行策略（效率优先/节能优先）
- 包含多列车追踪场景的仿真与分析
- 提供可视化工具用于结果展示和分析
- 模块化设计，便于扩展和修改

## 文件结构

```
.
├── atp_calculator.py      # ATP系统核心计算模块
├── config.py             # 配置文件（列车参数、轨道信息等）
├── simulation.py         # 单列车仿真主程序
├── simulation_c3.py      # 场景三仿真程序
├── simulation_multitrain.py  # 多列车追踪仿真程序
├── visualizer.py         # 可视化工具
├── visualizer_c3.py      # 场景三可视化工具
└── visualizer_multitrain.py  # 多列车场景可视化工具
```

## 主要功能

### 1. ATP系统仿真
- MRSP（最高允许速度）计算
- 动态速度防护曲线生成
- 紧急制动和常用制动控制

### 2. 列车运行策略
- 效率优先策略：在安全限制下最大化运行效率
- 节能优先策略：通过优化惰行时机实现节能运行

### 3. 多列车追踪控制
- 支持多列车场景仿真
- 动态移动授权点计算
- 安全行车间隔保持

## 使用说明

### 环境要求
- Python 3.x
- NumPy
- Matplotlib（用于可视化）

### 运行单列车仿真

```python
from simulation import run_simulation

# 效率优先策略
results = run_simulation(strategy='efficiency')

# 节能优先策略
results = run_simulation(strategy='energy_saving')
```

### 运行多列车仿真

```python
from simulation_multitrain import run_multitrain_simulation

# 设置行车间隔（单位：秒）
run_multitrain_simulation(headway_seconds=120)
```

### 结果可视化

```python
# 单列车场景
python visualizer.py

# 多列车场景
python visualizer_multitrain.py
```

## 仿真结果

仿真结果将以.npz格式保存在项目根目录下，包含以下文件：
- `multitrain_results.npz`：多列车仿真结果
- `c3_simulation_results.npz`：场景三仿真结果

## 注意事项

1. 运行仿真前请确保已正确配置`config.py`中的参数
2. 多列车仿真时需要特别注意安全距离的设置
3. 可视化结果会自动保存在`result`目录下

## 未来展望

- [ ] 添加更多列车运行策略
- [ ] 优化能耗计算模型
- [ ] 支持更复杂的线路条件
- [ ] 引入机器学习优化控制策略
