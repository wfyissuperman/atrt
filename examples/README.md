# ATRT 使用示例

本目录包含了ATRT包的使用示例，帮助用户快速上手。

## 示例文件说明

- `basic_usage.py` - 基本使用示例
- `dts_analysis_example.ipynb` - DTS数据分析完整示例(Jupyter Notebook)
- `thermal_conductivity_example.py` - 热导率计算示例
- `groundwater_flow_example.py` - 地下水流速估算示例

## 数据格式要求

请确保您的DTS数据格式符合以下要求：
- 第一列为深度信息
- 第一行为时间信息  
- 数据部分为温度值

## 运行示例

```bash
cd examples
python basic_usage.py
```

或者在Jupyter环境中打开notebook文件。
