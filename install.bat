@echo off
REM ATRT包构建和安装脚本

echo ================================
echo ATRT包构建和安装
echo ================================

echo.
echo 1. 检查Python环境...
python --version
if %errorlevel% neq 0 (
    echo 错误: Python未正确安装或不在PATH中
    pause
    exit /b 1
)

echo.
echo 2. 升级pip和安装构建工具...
python -m pip install --upgrade pip setuptools wheel build

echo.
echo 3. 安装依赖包...
pip install -r requirements.txt

echo.
echo 4. 构建包...
python -m build

echo.
echo 5. 安装包（开发模式）...
pip install -e .

echo.
echo 6. 验证安装...
python -c "import atrt; print(f'ATRT版本: {atrt.__version__}')"

if %errorlevel% equ 0 (
    echo.
    echo ================================
    echo 安装成功！
    echo ================================
    echo.
    echo 您现在可以使用以下命令测试包：
    echo python examples/basic_usage.py
    echo python -m pytest tests/
) else (
    echo.
    echo ================================
    echo 安装失败！
    echo ================================
    echo 请检查错误信息并重试
)

echo.
pause
