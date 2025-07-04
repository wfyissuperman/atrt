"""
ATRT: Active Temperature Sensing and Thermal Response Test Analysis Package

This package provides tools for analyzing distributed temperature sensing (DTS) data
and thermal response tests, including:
- DTPM (Distributed Temperature Profiling Method) calculations
- DTS data processing
- Groundwater flow rate estimation
- Thermal conductivity analysis

Author: 王丰源
Email: wfy22500@smail.nju.edu.cn
"""

__version__ = "0.1.0"
__author__ = "王丰源"
__email__ = "wfy22500@smail.nju.edu.cn"

# 延迟导入以避免依赖问题
def get_dts_data_processing():
    """获取DtsDataProcessing类"""
    from .dts_dataprocessing import DtsDataProcessing
    return DtsDataProcessing

def get_nfm_kluitenberg():
    """获取NFM_Kluitenberg函数"""
    from .DTPM_calcfunc import NFM_Kluitenberg
    return NFM_Kluitenberg

def get_thermal_functions():
    """获取热导率相关函数"""
    from .thermal_conductivity_function import (
        find_nearest_index,
        corrected_power_per_meter
    )
    return find_nearest_index, corrected_power_per_meter

def get_flow_functions():
    """获取流速相关函数"""
    from .flowrate_function import calc_rmse_std
    return calc_rmse_std

# 尝试直接导入，如果失败则提供获取函数
try:
    from .dts_dataprocessing import DtsDataProcessing
    from .DTPM_calcfunc import NFM_Kluitenberg
    from .thermal_conductivity_function import (
        find_nearest_index,
        corrected_power_per_meter
    )
    from .flowrate_function import calc_rmse_std
    
    # 定义公开的API
    __all__ = [
        "DtsDataProcessing",
        "NFM_Kluitenberg", 
        "find_nearest_index",
        "corrected_power_per_meter",
        "calc_rmse_std",
        "get_dts_data_processing",
        "get_nfm_kluitenberg", 
        "get_thermal_functions",
        "get_flow_functions"
    ]
    
except ImportError as e:
    # 如果直接导入失败，只导出获取函数
    __all__ = [
        "get_dts_data_processing",
        "get_nfm_kluitenberg", 
        "get_thermal_functions",
        "get_flow_functions"
    ]
    import warnings
    warnings.warn(f"部分模块导入失败: {e}，请使用get_*函数来获取相应功能", ImportWarning)