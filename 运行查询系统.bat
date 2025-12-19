@echo off
chcp 65001 >nul
echo. 正在检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo. [错误] 未检测到Python环境，请先安装Python 3.6及以上版本
    pause
    exit /b 1
)

echo. 正在安装必要的依赖包...
python -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple
echo.
python -m pip install streamlit pandas plotly openpyxl -i https://pypi.tuna.tsinghua.edu.cn/simple
echo.
if errorlevel 1 (
    echo. [错误] 依赖包安装失败
    pause
    exit /b 1
)

echo. 正在启动上市公司数字化转型指数查询系统...
echo.
python -m streamlit run "%~dp0digital_index_query_app.py"

echo.
echo. 应用已关闭
pause
exit /b 0