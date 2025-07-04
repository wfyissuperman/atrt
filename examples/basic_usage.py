"""
ATRT包基本使用示例

本示例展示了如何使用ATRT包进行基本的DTS数据处理和分析。
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# 导入ATRT包
try:
    import atrt
    from atrt import DtsDataProcessing, NFM_Kluitenberg
    print(f"成功导入ATRT包，版本: {atrt.__version__}")
except ImportError as e:
    print(f"导入ATRT包失败: {e}")
    print("请确保已正确安装ATRT包")
    exit(1)

def create_sample_data():
    """
    创建示例DTS数据
    """
    # 创建时间序列（1小时，每分钟一个数据点）
    time_range = pd.date_range('2024-01-01 10:00:00', 
                              '2024-01-01 11:00:00', 
                              freq='1min')
    
    # 创建深度序列（0-50米，每0.5米一个测点）
    depths = np.arange(0, 50.5, 0.5)
    
    # 创建基础温度场（线性梯度 + 随机噪声）
    base_temp = 15 + depths * 0.03  # 15°C + 3°C/100m的地温梯度
    
    # 添加加热信号（模拟主动加热实验）
    heating_zone = (depths >= 20) & (depths <= 30)  # 20-30m加热区间
    
    # 创建温度数据矩阵
    temp_data = np.zeros((len(depths), len(time_range)))
    
    for i, t in enumerate(time_range):
        # 基础温度
        temp_profile = base_temp.copy()
        
        # 添加随机噪声
        temp_profile += np.random.normal(0, 0.1, len(depths))
        
        # 在特定时间段添加加热信号
        heating_start = pd.Timestamp('2024-01-01 10:15:00')
        heating_end = pd.Timestamp('2024-01-01 10:45:00')
        
        if heating_start <= t <= heating_end:
            # 加热期间温度升高
            minutes_heated = (t - heating_start).total_seconds() / 60
            heating_amplitude = np.minimum(minutes_heated * 0.1, 3.0)  # 最大升温3°C
            temp_profile[heating_zone] += heating_amplitude
        
        temp_data[:, i] = temp_profile
    
    # 创建DataFrame
    # 第一行为时间，第一列为深度
    data_dict = {'Depth': ['Time'] + depths.tolist()}
    
    for i, time_str in enumerate(time_range.strftime('%Y/%m/%d %H:%M:%S')):
        data_dict[time_str] = [''] + temp_data[:, i].tolist()
    
    return pd.DataFrame(data_dict)

def main():
    """
    主要示例函数
    """
    print("=" * 60)
    print("ATRT包基本使用示例")
    print("=" * 60)
    
    # 1. 创建示例数据
    print("\n1. 创建示例DTS数据...")
    sample_data = create_sample_data()
    print(f"数据形状: {sample_data.shape}")
    print(f"深度范围: {sample_data.iloc[1, 0]} - {sample_data.iloc[-1, 0]} 米")
    print(f"时间范围: {sample_data.columns[1]} 到 {sample_data.columns[-1]}")
    
    # 2. 初始化DTS数据处理器
    print("\n2. 初始化DTS数据处理器...")
    dts_processor = DtsDataProcessing(sample_data)
    print(f"时间点数量: {len(dts_processor.time)}")
    print(f"深度点数量: {len(dts_processor.depth)}")
    
    # 3. 查找特定时间和深度的索引
    print("\n3. 查找索引示例...")
    start_time = '2024/1/1 10:15:00'
    end_time = '2024/1/1 10:45:00'
    target_depth = 25.0
    
    start_idx = dts_processor.find_time_index(start_time)
    end_idx = dts_processor.find_time_index(end_time)
    depth_idx = dts_processor.find_depth_index(target_depth)
    
    print(f"开始时间 {start_time} 对应索引: {start_idx}")
    print(f"结束时间 {end_time} 对应索引: {end_idx}")
    print(f"深度 {target_depth}m 对应索引: {depth_idx}")
    
    # 4. 提取加热数据
    print("\n4. 提取加热数据...")
    top_idx = dts_processor.find_depth_index(20.0)
    bottom_idx = dts_processor.find_depth_index(30.0)
    
    try:
        seconds, delta_temp, natural_temp = dts_processor.extraction_heating_data(
            top_idx=top_idx,
            bottom_idx=bottom_idx, 
            start_str=start_time,
            end_str=end_time
        )
        
        print(f"提取的时间序列长度: {len(seconds)}")
        print(f"温度数据形状: {delta_temp.shape}")
        print(f"自然温度长度: {len(natural_temp)}")
        print(f"最大温升: {np.max(delta_temp):.2f}°C")
        
        # 5. 简单的数据可视化
        print("\n5. 生成数据可视化...")
        
        plt.figure(figsize=(12, 8))
        
        # 绘制温升时间序列
        plt.subplot(2, 2, 1)
        mid_depth_idx = delta_temp.shape[0] // 2
        plt.plot(seconds, delta_temp[mid_depth_idx, :])
        plt.xlabel('时间 (秒)')
        plt.ylabel('温升 (°C)')
        plt.title(f'深度 {dts_processor.depth[top_idx + mid_depth_idx]:.1f}m 处的温升')
        plt.grid(True)
        
        # 绘制温度剖面
        plt.subplot(2, 2, 2)
        depths_range = dts_processor.depth[top_idx:bottom_idx+1]
        plt.plot(natural_temp, depths_range, 'b-', label='自然温度')
        final_temp = natural_temp + delta_temp[:, -1]
        plt.plot(final_temp, depths_range, 'r-', label='加热后温度')
        plt.xlabel('温度 (°C)')
        plt.ylabel('深度 (m)')
        plt.title('温度剖面对比')
        plt.legend()
        plt.grid(True)
        plt.gca().invert_yaxis()
        
        # 绘制温度场热图
        plt.subplot(2, 1, 2)
        im = plt.imshow(delta_temp, aspect='auto', cmap='hot', origin='upper')
        plt.colorbar(im, label='温升 (°C)')
        plt.xlabel('时间步')
        plt.ylabel('深度索引')
        plt.title('温升场热图')
        
        plt.tight_layout()
        plt.show()
        
    except Exception as e:
        print(f"数据提取过程中出现错误: {e}")
    
    print("\n" + "=" * 60)
    print("基本使用示例完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()
