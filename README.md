# ATRT - Active Temperature Sensing and Thermal Response Test Analysis Package

## 概述

ATRT是一个用于分析分布式温度传感(DTS)数据和热响应测试的Python包。该包提供了完整的工具集，用于处理主动温度传感数据、计算热物性参数、估算地下水流速等。

## 主要功能

- **DTS数据处理**: 处理分布式温度传感数据，包括时间序列和深度剖面分析
- **DTPM计算**: 分布式热物性质(Distributed Thermal Properties Measurement)的相关计算
- **热导率分析**: 热传导系数和热扩散系数的计算与优化
- **地下水流速估算**: 基于温度数据的地下水流速反演

## 安装

### 从源码安装

```bash
# 克隆或下载项目
cd atrt

# 安装依赖
pip install -r requirements.txt

# 安装包
pip install -e .
```

### 依赖要求

- Python >= 3.8
- numpy >= 1.20.0
- pandas >= 1.3.0
- scipy >= 1.7.0
- matplotlib >= 3.4.0

## 快速开始

```python
import atrt
from atrt import DtsDataProcessing

# 加载DTS数据
data_processor = DtsDataProcessing(your_data)

# 提取加热数据
seconds, delta_temp, natural_temp = data_processor.extraction_heating_data(
    top_idx=10, 
    bottom_idx=50, 
    start_str='2024/01/01 10:00:00', 
    end_str='2024/01/01 12:00:00'
)

# 进行DTPM计算
from atrt import NFM_Kluitenberg
rmse = NFM_Kluitenberg(parameters, measured_temp, time_array, variables)
```

## 模块说明

### `dts_dataprocessing.py`
分布式温度传感数据处理模块，包含DtsDataProcessing类用于数据提取和预处理。

### `DTPM_calcfunc.py`
DTPM方法的核心计算函数，包含NFM_Kluitenberg函数用于参数优化和理论温度计算。

### `thermal_conductivity_function.py`
热导率相关的计算函数，包括功率校正和温度分析。

### `flowrate_function.py`
地下水流速计算相关函数，包含参数优化和流速反演算法。

## 使用示例

详细的使用示例请参考`examples/`目录下的Jupyter notebook文件。

## 作者信息

- **作者**: 王丰源
- **邮箱**: wfy22500@smail.nju.edu.cn
- **机构**: 南京大学

## 许可证

本项目采用MIT许可证。详见LICENSE文件。

## 贡献

欢迎提交Issues和Pull Requests来改进这个项目。

## 更新日志

### v0.1.0 (2024-12-07)
- 初始版本发布
- 基本的DTS数据处理功能
- DTPM计算功能
- 热导率分析功能
- 地下水流速估算功能
