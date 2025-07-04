'''
作者:王丰源
时间:2024-12-07
功能：本程序为地下水渗流数据处理的函数库,包含了计算RMSE和标准差、优化参数、计算反演温度和地下水流速的函数
联系方式:wfy22500@smail.nju.edu.cn
注：本人水平极其有限，如有错误或不足之处，还请批评指正
'''
import numpy as np
from scipy.integrate import quad
from scipy.optimize import minimize
from scipy.special import kv
from scipy.optimize import dual_annealing

# 计算 RMSE 和标准差
def calc_rmse_std(parameter_process_0, t_observed, temp_observed, calc_timeidx):
    """
    计算 RMSE 和标准差的加权平均。
    :param parameter_process_0: 输入的模型参数 [T_steady, r_divide_B, A]
    :param t_observed: 观测时间数据
    :param temp_observed: 观测温度数据
    :param calc_timeidx: 计算从该索引开始的数据
    :return: RMSE 和标准差的加权平均值
    """
    a = parameter_process_0[0]  # T_steady
    b = parameter_process_0[1]  # r_divide_B
    c = parameter_process_0[2]  # A
    d = kv(0, b)  # 第二类0阶贝塞尔函数

    num_datasets = len(t_observed)
    temp_computed = np.zeros(num_datasets)
    w_1 = np.zeros(num_datasets)
    temp_computed[0] = 0  # 初始温度假设为0

    # 计算温度
    for i in range(1, num_datasets):
        ti = t_observed[i]
        fun1 = lambda s: np.exp(-s - ((b ** 2) / (4 * s))) / s  # 井函数自变量
        w_1[i], _ = quad(fun1, c / ti, np.inf)  # 使用quad进行数值积分
        temp_computed[i] = a * w_1[i] / (2 * d)  # 计算每个时刻的温度

    residuals = temp_computed[calc_timeidx:] - temp_observed[calc_timeidx:]
    rmse_value = np.sqrt(np.sum(residuals ** 2) / len(temp_observed[calc_timeidx:]))
    residual_std_value = np.std(residuals)

    # 计算加权RMSE和标准差
    rmse_std = 0.5* rmse_value + 0.5* residual_std_value
    return rmse_std

# 优化参数——梯度下降法
def optimize_parameters_GD(t_observed, temp_observed, calc_timeidx, parameter_process, method):
    """
    使用 Nelder-Mead 方法优化模型参数，以最小化 RMSE 和标准差。
    :param t_observed: 观测时间数据
    :param temp_observed: 观测温度数据
    :param calc_timeidx: 计算从该索引开始的数据
    :param parameter_process: 初始参数
    :param method: 优化方法
    :return: 优化后的参数值、RMSE和优化过程记录
    """
    # 定义损失函数（RMSE和标准差的加权平均）
    def loss(parameter):
        return calc_rmse_std(parameter, t_observed, temp_observed, calc_timeidx)
    
    # 用于记录优化过程
    history = []

    # 包装损失函数以记录路径
    def loss_with_history(parameter):
        value = loss(parameter)
        history.append((parameter.copy(), value))
        return value

    # 优化选项
    options = {
        'disp': True,
        'maxiter': 10**7, 
        'maxfun': 10**7,
        'ftol': 10e-7,
        'xtol': 10e-7,      
    }

    # 使用梯度下降方法进行优化
    result = minimize(loss_with_history, parameter_process, method=method, options=options)
    parameter_estimated = result.x  # 最优参数
    rmse_std = result.fun  # 最优RMSE_std值

    return parameter_estimated, rmse_std, history

# 优化参数——模拟退火法
def optimize_parameters_SA(t_observed, temp_observed, calc_timeidx, parameter_process, bounds):
    """
    使用模拟退火方法优化模型参数，以最小化 RMSE 和标准差。
    :param t_observed: 观测时间数据
    :param temp_observed: 观测温度数据
    :param calc_timeidx: 计算从该索引开始的数据
    :param parameter_process: 初始参数
    :param bounds: 参数的边界
    :return: 优化后的参数值、RMSE和求解路径
    """
    # 定义损失函数（RMSE和标准差的加权平均）
    def loss(parameter):
        return calc_rmse_std(parameter, t_observed, temp_observed, calc_timeidx)
    
    # 用于记录求解路径
    history = []

    # 包装损失函数以记录路径
    def loss_with_history(parameter, *args, **kwargs):
        value = loss(parameter)
        history.append((parameter.copy(), value))
        return value

    # 使用模拟退火方法进行优化
    result = dual_annealing(loss_with_history, bounds=bounds, x0=parameter_process)
    parameter_estimated = result.x  # 最优参数
    rmse_std = result.fun  # 最优RMSE_std值

    return parameter_estimated, rmse_std, history

# 计算温度
def compute_temperature(parameter_estimated, time):
    """
    根据给定的参数和时间数据计算温度。
    :param parameter_estimated: 优化后的参数 [T_steady, r_divide_B, A]
    :param time: 时间数据
    :return: 计算得到的温度数据
    """
    a = parameter_estimated[0]  # T_steady
    b = parameter_estimated[1]  # r_divide_B
    c = parameter_estimated[2]  # A

    # 计算第二类0阶贝塞尔函数
    d = kv(0, b)

    num_datasets = len(time)
    temp_computed = np.zeros(num_datasets)  # 存储计算的温度
    w_1 = np.zeros(num_datasets)  # 存储积分结果

    # 从第1个数据开始计算
    for i in range(1, num_datasets):
        ti = time[i]

        # 井函数自变量的定义
        fun1 = lambda s: np.exp(-s - ((b ** 2) / (4 * s))) / s

        # 使用quad计算数值积分
        w_1[i], _ = quad(fun1, c / ti, np.inf)
        
        # 计算温度
        temp_computed[i] = a * w_1[i] / (2 * d)

    return temp_computed

# 计算地下水流速
def calculate_flow_rate(parameter_estimated, rho_c_soil, thermal_conductivity_soil):
    """
    计算地下水流速的函数

    参数:
    parameter_estimated (list or array): 包含估计参数的列表或数组
    rho_c_soil (float): 土体的比热容
    thermal_conductivity (float): 土体热导率
    rho_c_water (float): 水的比热容，默认值为 4.2 * 1e6

    返回:
    float: 计算得到的流量
    """
    rho_c_water=4.2e6
    flow_rate = parameter_estimated[1] * np.sqrt(rho_c_soil * thermal_conductivity_soil) / rho_c_water / np.sqrt(parameter_estimated[2])
    return flow_rate