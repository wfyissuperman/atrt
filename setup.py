from setuptools import setup, find_packages
import os

# 读取README文件
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return "Active Temperature Sensing and Thermal Response Test Analysis Package"

# 读取requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if os.path.exists(requirements_path):
        with open(requirements_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return [
        "numpy>=1.20.0,<2.0.0",
        "pandas>=1.3.0,<2.1.0",
        "scipy>=1.7.0",
        "matplotlib>=3.4.0,<3.9.0"
    ]

setup(
    name="atrt",
    version="0.1.0",
    author="王丰源",
    author_email="wfy22500@smail.nju.edu.cn",
    description="Active Temperature Sensing and Thermal Response Test Analysis Package",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/wfyissuperman/atrt_0.1.0",  
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Physics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    keywords="thermal conductivity, DTS, temperature sensing, groundwater flow, heat transfer",
    project_urls={
        "Bug Reports": "https://github.com/wfyissuperman/atrt_0.1.0/issues",
        "Source": "https://github.com/wfyissuperman/atrt_0.1.0",
    },
)