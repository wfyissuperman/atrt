import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from scipy.special import exp1

# 查找最接近的索引函数
def find_nearest_index(array, value):
    array = np.array(array)
    idx = (np.abs(array - value)).argmin()
    return idx
# 计算单位长度电阻丝的加热功率分布
def corrected_power_per_meter(I, T, T0,R0=0.08, alpha=0.00393, time= None):
    """
    计算考虑温度影响的单位长度电阻丝的加热功率分布（W/m），并返回平均功率。

    参数:
    - I: 恒定电流 (A)
    - R0: 参考温度 T0 下的单位长度电阻 (Ω/m),南智内加热光缆为0.08 Ω/m 或者0.02 Ω/m
    - T: 各时间点的温度数组 (°C)，与 time 一一对应
    - T0: 参考温度 (°C)，初始地温
    - alpha: 铜的电阻温度系数 (1/°C)，默认 0.00393
    - time: 时间点数组 (s)，用于精确积分（可选）

    返回:
    - P_array: 各时间点的单位长度加热功率数组 (W/m)
    - P_avg: 平均单位长度加热功率 (W/m)
    """
    T = np.array(T)
    R_T = R0 * (1 + alpha * (T - T0))
    P_array = I**2 * R_T

    # 计算平均功率
    if time is not None:
        time = np.array(time)
        P_avg = np.trapz(P_array, time) / (time[-1] - time[0])
    else:
        P_avg = np.mean(P_array)

    return P_array, P_avg

# 导热系数计算函数
def calculate_thermal_conductivity(delta_temperature, seconds, start_calc_hour, 
                                 end_calc_hour, heating_power):
    """
    计算导热系数及其相关参数
    
    Parameters:
    -----------
    delta_temperature : array_like
        温度变化数组
    seconds : array_like
        时间数组（秒）
    start_calc_hour : float
        计算开始时间（小时）
    end_calc_hour : float
        计算结束时间（小时）
    heating_power : float
        加热功率
        
    Returns:
    --------
    tuple
        包含以下元素的元组：
        - thermal_conductivity : float
            导热系数
        - error : float
            误差值
        - r_squared : float
            拟合优度 R²
        - fitted_params : array
            拟合参数 [k, b]
        - x_fitted : array
            拟合使用的x值（ln(t)）
            
    Raises:
    -------
    ValueError
        当输入参数不合法时抛出异常
    """
    # 输入验证
    if len(delta_temperature) != len(seconds):
        raise ValueError("delta_temperature和seconds数组长度必须相同")
    
    if start_calc_hour >= end_calc_hour:
        raise ValueError("start_calc_hour必须小于end_calc_hour")
    
    if heating_power <= 0:
        raise ValueError("heating_power必须大于0")

    # 计算ln(t)，从第二个元素开始，因为第一个元素是0
    ln_time = np.log(seconds[1:])
    
    # 找到计算区间的索引
    start_calc_index = find_nearest_index(ln_time, np.log(start_calc_hour * 3600))
    end_calc_index = find_nearest_index(ln_time, np.log(end_calc_hour * 3600))

    # 提取计算区间的数据
    y_data = delta_temperature[start_calc_index:end_calc_index]
    x_data = ln_time[start_calc_index:end_calc_index]
 
    def linear_function(x, slope, intercept):
        """线性拟合函数"""
        return slope * x + intercept

    # 进行曲线拟合
    fitted_params, covariance_matrix = curve_fit(linear_function, x_data, y_data)
    slope = fitted_params[0]
    parameter_errors = np.sqrt(np.diag(covariance_matrix))

    # 计算导热系数
    thermal_conductivity = heating_power / (4 * np.pi * slope)

    # 计算误差（误差传播公式）
    error = abs(-heating_power / (4 * np.pi * slope**2)) * parameter_errors[0]

    # 计算拟合优度 R²
    y_predicted = linear_function(x_data, *fitted_params)
    residuals = y_data - y_predicted
    sum_squared_residuals = np.sum(residuals**2)
    sum_squared_total = np.sum((y_data - np.mean(y_data))**2)
    r_squared = 1 - (sum_squared_residuals / sum_squared_total)

    return thermal_conductivity, error, r_squared, fitted_params, x_data

# 可视化拟合结果
def plot_thermal_conductivity_fit(delta_temperature, seconds, start_calc_hour, 
                                end_calc_hour, heating_power, figsize=(10, 7)):
    """
    绘制 ln(t)-temperature 曲线与拟合的线性回归曲线
    
    Parameters:
    -----------
    delta_temperature : array_like
        温度变化数组
    seconds : array_like
        时间数组（秒）
    start_calc_hour : float
        计算开始时间（小时）
    end_calc_hour : float
        计算结束时间（小时）
    heating_power : float
        加热功率
    figsize : tuple, optional
        图像大小，默认为 (12, 8)
        
    Returns:
    --------
    dict
        包含计算结果的字典：
        - thermal_conductivity : float
            导热系数
        - error : float
            误差值
        - r_squared : float
            拟合优度 R²
        - fitted_params : array
            拟合参数 [slope, intercept]
    """
    
    # 调用原函数获取计算结果
    thermal_conductivity, error, r_squared, fitted_params, x_data = calculate_thermal_conductivity(
        delta_temperature, seconds, start_calc_hour, end_calc_hour, heating_power
    )
    
    # 计算完整的 ln(t) 数组（从第二个元素开始，因为第一个元素是0）
    ln_time_full = np.log(seconds[1:])
    delta_temp_full = delta_temperature[1:]  # 对应去掉第一个元素
    
    # 找到计算区间的索引
    start_calc_index = find_nearest_index(ln_time_full, np.log(start_calc_hour * 3600))
    end_calc_index = find_nearest_index(ln_time_full, np.log(end_calc_hour * 3600))
    
    # 生成拟合线的数据点
    x_fit_extended = np.linspace(x_data.min(), x_data.max(), 100)
    y_fit_extended = fitted_params[0] * x_fit_extended + fitted_params[1]
    
    # 创建图像
    plt.figure(figsize=figsize)
    
    # 绘制完整的数据点（浅色）
    plt.scatter(ln_time_full, delta_temp_full, alpha=0.5, s=20, color='lightgray', 
                label='All data points', zorder=1)
    
    # 添加垂直线标记计算区间
    plt.axvline(x=np.log(start_calc_hour * 3600), color='green', linestyle='--', alpha=0.7,
                label=f'Start: {start_calc_hour}h', zorder=2)
    plt.axvline(x=np.log(end_calc_hour * 3600), color='orange', linestyle='--', alpha=0.7,
                label=f'End: {end_calc_hour}h', zorder=2)
    
    # 绘制用于拟合的数据点（深色）
    plt.scatter(x_data, delta_temperature[start_calc_index:end_calc_index], 
                color='blue', s=20, alpha=0.5, 
                label=f'Fitting data ({start_calc_hour}-{end_calc_hour} hours)', zorder=3)
    
    # 绘制拟合直线（最上层）
    plt.plot(x_fit_extended, y_fit_extended, 'r-', linewidth=3, 
             label=f'λ = {thermal_conductivity:.4f} W/(m·K), R² = {r_squared:.4f}', zorder=4)
    
    # 设置标签和标题
    plt.xlabel('ln(t) [ln(seconds)]', fontsize=12)
    plt.ylabel('Temperature Rise (°C)', fontsize=12)
    plt.title('Thermal Conductivity Analysis: ln(t) vs Temperature Rise', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=10, loc='upper left')
    
    plt.tight_layout()
    plt.show()
    
    # 返回计算结果
    return {
        'thermal_conductivity': thermal_conductivity,
        'error': error,
        'r_squared': r_squared,
        'fitted_params': fitted_params
    }

# === 温升解析函数（无限介质线热源）===
def temperature_response(t, q, k, alpha):

    r = 0.0007
    t = np.maximum(t, 1e-6)  # 避免除零
    ei_arg = r**2 / (4 * alpha * t)
    return (q / (4 * np.pi * k)) * exp1(ei_arg)

# === 持续线热源理论的损失函数 ===
def CLHS_RMSE(x, T_measured, t, q):
    
    alpha = x[0]
    lambda_ = x[1]
    # alpha = lambda_ / Cv
    
    T_predicted = temperature_response(t, q, lambda_, alpha)
    rmse = np.sqrt(np.mean((T_measured - T_predicted) ** 2))
    return rmse