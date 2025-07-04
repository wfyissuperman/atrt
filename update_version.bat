@echo off
REM 版本更新脚本

echo ========================================
echo ATRT Package Version Update Script
echo ========================================

echo.
echo 当前版本信息:
python -c "import atrt; print('当前版本:', atrt.__version__)"

echo.
echo 请输入新版本号 (格式: x.y.z):
set /p new_version="新版本: "

if "%new_version%"=="" (
    echo 没有输入版本号，退出。
    pause
    exit /b 1
)

echo.
echo 将版本更新为: %new_version%

echo.
echo 1. 更新 setup.py...
powershell -Command "(Get-Content setup.py) -replace 'version=\"0\.1\.0\"', 'version=\"%new_version%\"' | Set-Content setup.py"

echo.
echo 2. 更新 pyproject.toml...
powershell -Command "(Get-Content pyproject.toml) -replace 'version = \"0\.1\.0\"', 'version = \"%new_version%\"' | Set-Content pyproject.toml"

echo.
echo 3. 更新 atrt/__init__.py...
powershell -Command "(Get-Content atrt/__init__.py) -replace '__version__ = \"0\.1\.0\"', '__version__ = \"%new_version%\"' | Set-Content atrt/__init__.py"

echo.
echo 4. 验证更新...
python -c "import atrt; print('更新后版本:', atrt.__version__)"

echo.
echo 版本更新完成！

echo.
echo 下一步操作:
echo 1. git add .
echo 2. git commit -m "Bump version to %new_version%"
echo 3. git push
echo 4. 重新构建和发布包

echo.
set /p auto_commit="是否自动提交到Git? (y/N): "

if /i "%auto_commit%"=="y" (
    echo.
    echo 提交到Git...
    git add .
    git commit -m "Bump version to %new_version%"
    git push
    
    echo.
    echo Git提交完成！
    
    echo.
    set /p create_tag="是否创建Git标签? (y/N): "
    
    if /i "%create_tag%"=="y" (
        git tag -a v%new_version% -m "Release version %new_version%"
        git push origin v%new_version%
        echo 标签 v%new_version% 已创建并推送。
    )
)

echo.
pause
