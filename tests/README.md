# Tests for ATRT package

本目录包含ATRT包的单元测试。

## 运行测试

在项目根目录下运行：

```bash
# 运行所有测试
python -m pytest tests/

# 运行特定测试文件
python -m pytest tests/test_basic.py

# 运行测试并显示覆盖率
python -m pytest tests/ --cov=atrt --cov-report=html
```

## 测试文件说明

- `test_basic.py` - 基本功能测试
- `test_dts_processing.py` - DTS数据处理测试
- `test_calculations.py` - 计算函数测试

## 添加新测试

请按照以下规范添加新测试：
1. 测试文件以`test_`开头
2. 测试类继承`unittest.TestCase`
3. 测试方法以`test_`开头
4. 包含必要的断言和错误处理
