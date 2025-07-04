@echo off
REM GitHub发布准备脚本 - 针对GitHub Desktop用户

echo ========================================
echo ATRT Package GitHub Setup Script
echo 专为GitHub Desktop用户设计
echo ========================================

echo.
echo 检查项目文件...
if not exist atrt (
    echo 错误: 找不到atrt文件夹！请确保在正确的项目目录中运行此脚本。
    pause
    exit /b 1
)

if not exist README.md (
    echo 错误: 找不到README.md文件！
    pause
    exit /b 1
)

echo 项目文件检查完成。

echo.
echo 检查.gitignore文件...
if exist .gitignore (
    echo ✅ .gitignore文件存在。
) else (
    echo ⚠️  警告: .gitignore文件不存在！
)

echo.
echo ========================================
echo GitHub Desktop 发布步骤指南
echo ========================================
echo.
echo 第一步: 在GitHub网站创建仓库
echo ----------------------------------------
echo 1. 访问 https://github.com
echo 2. 点击右上角 "+" -^> "New repository"
echo 3. 仓库名: atrt
echo 4. 描述: Active Temperature Sensing and Thermal Response Test Analysis Package
echo 5. 设为Public
echo 6. 不要初始化README
echo 7. 创建仓库
echo.

echo 第二步: 使用GitHub Desktop发布
echo ----------------------------------------
echo 1. 打开GitHub Desktop
echo 2. 点击 File -^> Add local repository
echo 3. 选择此文件夹: %CD%
echo 4. 如果提示创建仓库，点击 "create a repository"
echo 5. 填写Name: atrt
echo 6. 取消勾选 "Initialize this repository with a README"
echo 7. 点击 Create repository
echo.

echo 第三步: 提交并发布
echo ----------------------------------------
echo 1. 在GitHub Desktop的Changes中查看所有文件
echo 2. 在左下角提交框输入:
echo    Summary: Initial commit: ATRT package v0.1.0
echo    Description: First release of Active Temperature Sensing package
echo 3. 点击 Commit to main
echo 4. 点击 Publish repository
echo 5. 确保取消勾选 "Keep this code private"
echo 6. 点击 Publish repository
echo.

echo 第四步: 更新setup.py中的URL
echo ----------------------------------------
echo 1. 发布后，复制GitHub仓库URL
echo 2. 编辑setup.py文件，更新GitHub链接
echo 3. 在GitHub Desktop中提交这个更改
echo.

echo 第五步: 创建Release（可选）
echo ----------------------------------------
echo 1. 访问GitHub仓库页面
echo 2. 点击 Releases -^> Create a new release
echo 3. Tag version: v0.1.0
echo 4. Release title: ATRT v0.1.0 - Initial Release
echo 5. 填写发布说明
echo 6. 点击 Publish release
echo.

echo ========================================
echo 准备工作完成！
echo ========================================
echo.
echo 现在您可以：
echo 1. 按照上述步骤在GitHub Desktop中发布项目
echo 2. 如果已经发布，可以直接运行 publish_pypi.bat 发布到PyPI
echo.

echo 有用的链接:
echo - GitHub Desktop下载: https://desktop.github.com/
echo - GitHub注册: https://github.com
echo - PyPI注册: https://pypi.org
echo.

pause
