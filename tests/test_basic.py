"""
测试ATRT包的基本功能
"""

import unittest
import numpy as np
import pandas as pd
import sys
import os

# 添加包路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from atrt import DtsDataProcessing


class TestDtsDataProcessing(unittest.TestCase):
    """测试DtsDataProcessing类"""
    
    def setUp(self):
        """设置测试数据"""
        # 创建简单的测试数据
        time_range = pd.date_range('2024-01-01 10:00:00', 
                                  '2024-01-01 10:10:00', 
                                  freq='1min')
        depths = np.arange(0, 10, 1.0)
        
        # 创建温度数据
        temp_data = np.random.rand(len(depths), len(time_range)) * 5 + 15
        
        # 创建DataFrame
        data_dict = {'Depth': ['Time'] + depths.tolist()}
        for i, time_str in enumerate(time_range.strftime('%Y/%m/%d %H:%M:%S')):
            data_dict[time_str] = [''] + temp_data[:, i].tolist()
        
        self.test_data = pd.DataFrame(data_dict)
        self.processor = DtsDataProcessing(self.test_data)
    
    def test_initialization(self):
        """测试初始化"""
        self.assertIsInstance(self.processor.data, pd.DataFrame)
        self.assertEqual(len(self.processor.time), 11)  # 11个时间点
        self.assertEqual(len(self.processor.depth), 10)  # 10个深度点
        self.assertEqual(self.processor.temp.shape, (10, 11))
    
    def test_find_time_index(self):
        """测试时间索引查找"""
        idx = self.processor.find_time_index('2024/1/1 10:05:00')
        self.assertIsInstance(idx, int)
        self.assertGreaterEqual(idx, 0)
        self.assertLess(idx, len(self.processor.time))
    
    def test_find_depth_index(self):
        """测试深度索引查找"""
        idx = self.processor.find_depth_index(5.0)
        self.assertIsInstance(idx, int)
        self.assertGreaterEqual(idx, 0)
        self.assertLess(idx, len(self.processor.depth))


class TestHelperFunctions(unittest.TestCase):
    """测试辅助函数"""
    
    def test_imports(self):
        """测试模块导入"""
        try:
            from atrt import find_nearest_index, calc_rmse_std
            self.assertTrue(True)
        except ImportError:
            self.fail("无法导入必要的函数")
    
    def test_find_nearest_index(self):
        """测试最近索引查找函数"""
        from atrt import find_nearest_index
        
        array = [1, 3, 5, 7, 9]
        idx = find_nearest_index(array, 6)
        self.assertEqual(idx, 2)  # 应该找到索引2（值为5）


if __name__ == '__main__':
    unittest.main()
