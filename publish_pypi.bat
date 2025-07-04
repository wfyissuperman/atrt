@echo off
REM ATRT包PyPI发布脚本

echo ========================================
echo ATRT Package PyPI Release Script
echo ========================================

echo.
echo 检查当前版本...
python -c "import atrt; print('当前版本:', atrt.__version__)"

echo.
echo 1. 清理之前的构建...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist *.egg-info rmdir /s /q *.egg-info

echo.
echo 2. 安装/更新发布工具...
python -m pip install --upgrade pip setuptools wheel build twine

echo.
echo 3. 构建包...
python -m build

if %errorlevel% neq 0 (
    echo 构建失败！
    pause
    exit /b 1
)

echo.
echo 4. 检查包的完整性...
twine check dist/*

if %errorlevel% neq 0 (
    echo 包检查失败！
    pause
    exit /b 1
)

echo.
echo 5. 列出构建文件...
dir dist

echo.
echo ========================================
echo 构建完成！现在可以选择：
echo ========================================
echo.
echo [1] 上传到TestPyPI（推荐先测试）
echo [2] 上传到正式PyPI
echo [3] 退出
echo.

set /p choice="请选择 (1/2/3): "

if "%choice%"=="1" (
    echo.
    echo 上传到TestPyPI...
    twine upload --repository-url https://test.pypi.org/legacy/ dist/*
    echo.
    echo 测试安装命令:
    echo pip install --index-url https://test.pypi.org/simple/ atrt
) else if "%choice%"=="2" (
    echo.
    echo 确认要上传到正式PyPI吗？这个操作不可撤销！
    set /p confirm="确认 (y/N): "
    if /i "%confirm%"=="y" (
        echo.
        echo 上传到正式PyPI...
        twine upload dist/*
        echo.
        echo 发布完成！可以通过以下命令安装:
        echo pip install atrt
    ) else (
        echo 取消发布。
    )
) else (
    echo 退出。
)

echo.
pause
