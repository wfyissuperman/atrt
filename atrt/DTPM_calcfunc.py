import numpy as np
import pandas as pd
from scipy.special import expi
from scipy.optimize import minimize,least_squares
from functools import partial

# 定义常量，避免使用“魔法数字”
MAX_EXPI_ARG = -700.0 # expi 函数参数的阈值，用于避免溢出

def NFM_Kluitenberg(x: list, T_measured: np.ndarray, t: np.ndarray, variables: list) -> float:
    """
    计算理论温度与实测温度之间的均方根误差 (RMSE)。

    输入:
        x - 参数列表 [Cv, lambda]，其中:
            x[0] = Cv (体积热容)
            x[1] = lambda (导热系数)
        T_measured - 实测温度数据 (Numpy 数组)
        t - 对应测量的时间值 (Numpy 数组)
        variables - 额外参数列表:
            variables[0] = r (径向距离)
            variables[1] = q (热源强度)
            variables[2] = t0 (加热持续时间)

    输出:
        RMSE - 实测温度与理论温度之间的均方根误差
    """
    # 提取 Cv 和 lambda
    Cv = x[0]
    lambda_ = x[1]

    # 提取 r, q, t0
    r = variables[0]  # 径向距离 (m)
    q = variables[1]  # 热源强度 (W/m·K)
    t0 = variables[2] # 加热持续时间 (s)

    # 计算热扩散系数 k 和 Q
    k = lambda_ / Cv  # 热扩散系数 (m^2/s)
    Q = q / Cv

    # 初始化理论温度数组，将无效时间点设为 NaN
    T_theoretical = np.full_like(t, np.nan, dtype=float)

    # 计算 expi 的参数
    arg1 = -r**2 / (4 * k * t)
    arg2 = np.full_like(t, np.nan, dtype=float) # 初始化为NaN
    mask_t_gt_t0 = t > t0
    arg2[mask_t_gt_t0] = -r**2 / (4 * k * (t[mask_t_gt_t0] - t0))

    # 创建掩码，区分不同的时间段
    mask_case_a = (t > 0) & (t <= t0)
    mask_case_b = (t > t0)

    # 情况 (a): 0 < t <= t0
    valid_arg_a_mask = (arg1[mask_case_a] > MAX_EXPI_ARG) & np.isfinite(arg1[mask_case_a])
    temp_a_vals = np.where(valid_arg_a_mask, -(Q / (4 * np.pi * k)) * expi(arg1[mask_case_a]), np.nan)
    T_theoretical[mask_case_a] = temp_a_vals

    # 情况 (b): t > t0
    valid_arg_b_mask = (arg1[mask_case_b] > MAX_EXPI_ARG) & \
                       (arg2[mask_case_b] > MAX_EXPI_ARG) & \
                       np.isfinite(arg1[mask_case_b]) & \
                       np.isfinite(arg2[mask_case_b])

    term1_b_vals = np.where(valid_arg_b_mask, expi(arg1[mask_case_b]), np.nan)
    term2_b_vals = np.where(valid_arg_b_mask, expi(arg2[mask_case_b]), np.nan)

    T_theoretical[mask_case_b] = (Q / (4 * np.pi * k)) * (term2_b_vals - term1_b_vals)

    # 计算 RMSE
    RMSE = np.sqrt(np.nanmean((T_measured - T_theoretical) ** 2))

    return RMSE

def calc_temp(parameters: list, t: np.ndarray, variables: list) -> np.ndarray:
    """
    根据给定方程计算理论温度。

    输入:
        parameters - 参数列表 [Cv, lambda]，其中:
            parameters[0] = Cv (体积热容)
            parameters[1] = lambda (导热系数)
        t - 时间值 (Numpy 数组)
        variables - 额外参数列表:
            variables[0] = r (径向距离)
            variables[1] = q (热源强度)
            variables[2] = t0 (加热持续时间)

    输出:
        T_theoretical - 给定时间点上的理论温度值 (Numpy 数组)
    """
    # 提取 Cv 和 lambda
    Cv = parameters[0]
    lambda_ = parameters[1]

    # 提取 r, q, t0
    r = variables[0]  # 径向距离
    q = variables[1]  # 热源强度
    t0 = variables[2] # 加热持续时间

    # 计算热扩散系数 k 和 Q
    k = lambda_ / Cv  # 热扩散系数 (m^2/s)
    Q = q / Cv

    # 初始化理论温度数组，将无效时间点设为 NaN
    T_theoretical = np.full_like(t, np.nan, dtype=float)

    # 计算 expi 的参数
    arg1 = -r**2 / (4 * k * t)
    arg2 = np.full_like(t, np.nan, dtype=float)
    mask_t_gt_t0 = t > t0
    arg2[mask_t_gt_t0] = -r**2 / (4 * k * (t[mask_t_gt_t0] - t0))

    # 创建掩码，区分不同的时间段
    mask_case_a = (t > 0) & (t <= t0)
    mask_case_b = (t > t0)

    # 情况 (a): 0 < t <= t0
    T_theoretical[mask_case_a] = -(Q / (4 * np.pi * k)) * expi(arg1[mask_case_a])

    # 情况 (b): t > t0
    term1 = expi(arg1[mask_case_b])
    term2 = expi(arg2[mask_case_b])
    T_theoretical[mask_case_b] = (Q / (4 * np.pi * k)) * (term2 - term1)

    return T_theoretical

def optimize_soil_properties_RMSE(
    time: np.ndarray,
    temperature_data: np.ndarray | pd.Series,
    variables: list,
    initial_guess: list
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    通过最小化实测温度与理论温度之间的 RMSE 来优化土壤特性参数。

    输入:
        time - 时间值 (Numpy 数组)
        temperature_data - 实测温度的 2D Numpy 数组，每列或每行是一个数据集。
                           **请根据您的实际数据形状调整数据提取方式。**
        variables - 额外参数列表:
            variables[0] = r (径向距离)
            variables[1] = q (热源强度)
            variables[2] = t0 (加热持续时间)
        initial_guess - [Cv_初始值, lambda_初始值] 的初始猜测列表

    输出:
        Cv - 每个数据集的优化体积热容 (J/(m^3·K))
        lambda_ - 每个数据集的优化导热系数 (W/(m·K))
        RMSE - 每个数据集的均方根误差
    """

    # 初始猜测 Cv 和 lambda
    Cv_initial = initial_guess[0]
    lambda_initial = initial_guess[1]

    # 确保 temperature_data 是一个 2D NumPy 数组
    if isinstance(temperature_data, pd.Series):
        temperature_data = temperature_data.to_numpy()

    if temperature_data.ndim == 1:
        temperature_data = temperature_data[np.newaxis, :]
    elif temperature_data.ndim == 2:
        # 假设 temperature_data 的形状是 (num_datasets, num_time_points)
        # 如果您的数据是 (num_time_points, num_datasets)，您需要转置：
        # temperature_data = temperature_data.T
        pass

    # 数据集数量
    num_datasets = temperature_data.shape[0]

    # 初始化输出数组
    Cv_optimized = np.zeros(num_datasets)
    lambda_optimized = np.zeros(num_datasets)
    RMSE_results = np.zeros(num_datasets)

    # 循环处理每个数据集
    for i in range(num_datasets):
        current_temperature = temperature_data[i, :]
        x0 = [Cv_initial, lambda_initial]

        # 定义参数的边界：Cv 和 lambda 必须是正值
        bounds = [(1e-6, None), (1e-6, None)]

        objective_function = partial(NFM_Kluitenberg, T_measured=current_temperature, t=time, variables=variables)

        options = {
            'disp': False,
            'maxiter': 10**5,
            'ftol': 1e-9,
            'xtol': 1e-9
        }

        # 推荐使用 L-BFGS-B 或 TNC 方法，它们支持边界
        result = minimize(objective_function, x0, method='Nelder-Mead', bounds=bounds, options=options)

        Cv_optimized[i] = result.x[0]
        lambda_optimized[i] = result.x[1]
        RMSE_results[i] = result.fun

    return Cv_optimized, lambda_optimized, RMSE_results


def calc_mositureanddensities_micon(Cv, lamda, vars, soil_density=0.72, fsa=1,calc_method='L-BFGS-B'):
    """
    Calculate water moisture and densities from thermal properties
    
    Parameters:
    Cv: array-like, volumetric heat capacity
    lamda: array-like, thermal conductivity  
    vars: list, initial guess [x, y]
    
    Returns:
    water_moisture: numpy array
    densities: numpy array
    """
    Cv = np.array(Cv)
    lamda = np.array(lamda)
    
    water_moisture = np.zeros_like(Cv, dtype=float)
    densities = np.zeros_like(Cv, dtype=float)
    
    def residuals(vars_opt, Cv_i, lamda_i):
        
        x, y = vars_opt
        fc1 = 1 - fsa
        afa = 0.67 * fc1 + 0.24
        beita = 1.97 * fsa + 1.87 * x - 1.36 * fsa * x - 0.95
        
        F1 = soil_density * x + 4.18 * y - Cv_i
        F2 = 0.51 - 0.56 * (1 - x / 2.65) + np.exp(beita - y**(-afa)) - lamda_i
        return [F1, F2]
    
    bounds = ([1, 0], [2, 0.5])
    
    for i in range(len(Cv)):
        try:
            result = least_squares(
                residuals, 
                vars, 
                args=(Cv[i], lamda[i]),
                bounds=bounds,
                method='trf'  # Trust Region Reflective algorithm
            )
            
            if result.success:
                densities[i] = result.x[0]
                water_moisture[i] = result.x[1]
            else:
                densities[i] = np.nan
                water_moisture[i] = np.nan
        except:
            densities[i] = np.nan
            water_moisture[i] = np.nan

# 计算平均电压
def estimate_avg_power(U0, Ut, I, T=120):
    k = 5 / T  # or tune based on observed heating dynamics
    exp_term = (np.exp(-k * T) - 1) / (k * T)
    U_avg = U0 + (Ut - U0) * (1 + exp_term)
    P_avg = I * U_avg
    return P_avg