@echo off
cd /d "%~dp0"

REM 检查Python是否可用
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python未安装或未添加到PATH环境变量
    pause
    exit /b 1
)

REM 检查必要的依赖包是否已安装
python -c "import streamlit, pandas, plotly, numpy, openpyxl" >nul 2>&1
if %errorlevel% neq 0 (
    echo 正在安装必要的依赖包...
    pip install streamlit pandas plotly numpy openpyxl
    if %errorlevel% neq 0 (
        echo 依赖包安装失败
        pause
        exit /b 1
    )
)

REM 运行Streamlit应用程序
echo 正在启动上市公司数字化转型指数查询系统...
python -m streamlit run digital_index_query_app_simple.py

pause