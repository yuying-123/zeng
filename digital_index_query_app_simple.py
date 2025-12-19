import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

# 设置页面配置
st.set_page_config(
    page_title="上市公司数字化转型指数查询系统",
    page_icon="📊",
    layout="centered"
)

# 加载数据
def load_data():
    try:
        # 获取当前脚本所在目录
        app_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(app_dir, '历年数字化转型指数汇总.xlsx')
        
        if os.path.exists(file_path):
            st.success(f"成功读取数据文件: {file_path}")
            # 读取Excel文件，将股票代码转换为字符串以保留前导零
            data = pd.read_excel(file_path, dtype={'股票代码': str})
            return data
        else:
            st.error(f"数据文件不存在: {file_path}")
            return None
    except Exception as e:
        st.error(f"读取数据失败: {str(e)}")
        return None

# 绘制单个公司的趋势图
def plot_company_trend(data, company_name, selected_year, selected_stock):
    """绘制单个公司的数字化转型指数趋势图"""
    # 获取该公司的所有数据
    company_data = data[data['企业名称'] == company_name].copy()
    
    # 确保数据按年份排序
    company_data = company_data.sort_values('年份')
    
    # 创建1999-2023年的完整年份列表
    full_years = pd.DataFrame({'年份': range(1999, 2024)})
    
    # 将企业数据与完整年份列表合并，确保每个年份都有数据点
    company_data = pd.merge(full_years, company_data, on='年份', how='left')
    
    # 对于缺失的数据点，使用前向填充和后向填充
    company_data['数字化转型指数'] = company_data['数字化转型指数'].ffill().bfill()
    
    # 创建Plotly图表
    fig = go.Figure()
    
    # 添加趋势线
    fig.add_trace(go.Scatter(
        x=company_data['年份'],
        y=company_data['数字化转型指数'],
        name='数字化转型指数',
        line=dict(color='blue', width=2),
        mode='lines+markers',
        marker=dict(size=6, color='blue')
    ))
    
    # 标注选中年份的数据点
    selected_year_data = company_data[company_data['年份'] == selected_year]
    if not selected_year_data.empty:
        fig.add_trace(go.Scatter(
            x=[selected_year_data['年份'].iloc[0]],
            y=[selected_year_data['数字化转型指数'].iloc[0]],
            name=f'{selected_year}年',
            mode='markers',
            marker=dict(size=10, color='orange', symbol='star'),
            text=f'{selected_year}: {selected_year_data["数字化转型指数"].iloc[0]:.2f}',
            textposition='top center'
        ))
    
    # 设置图表布局
    fig.update_layout(
        title=f"{company_name} 数字化转型指数趋势",
        xaxis_title="年份",
        yaxis_title="数字化转型指数",
        font=dict(family="Microsoft YaHei, SimHei, Arial, sans-serif"),
        xaxis=dict(
            tickmode='linear',
            dtick=1,
            tickangle=45,
            range=[1998.5, 2023.5]
        ),
        hovermode="x unified",
        showlegend=True
    )
    
    return fig

# 绘制所有公司所有年份的折线图
def plot_all_companies_trend(data):
    """绘制所有公司所有年份的数字化转型指数趋势图"""
    # 计算每年的平均指数
    annual_avg = data.groupby('年份')['数字化转型指数'].mean().reset_index()
    
    # 创建完整的年份列表（1999-2023）
    full_years = pd.DataFrame({'年份': range(1999, 2024)})
    
    # 合并数据，确保每个年份都有数据
    annual_avg = pd.merge(full_years, annual_avg, on='年份', how='left')
    
    # 处理缺失值
    annual_avg['数字化转型指数'] = annual_avg['数字化转型指数'].fillna(method='ffill').fillna(method='bfill')
    
    # 创建图表
    fig = go.Figure()
    
    # 添加平均线
    fig.add_trace(go.Scatter(
        x=annual_avg['年份'],
        y=annual_avg['数字化转型指数'],
        name='平均数字化转型指数',
        line=dict(color='green', width=2),
        mode='lines+markers',
        marker=dict(size=6, color='green')
    ))
    
    # 设置图表布局
    fig.update_layout(
        title='所有公司数字化转型指数趋势(1999-2023)',
        xaxis_title='年份',
        yaxis_title='数字化转型指数',
        font=dict(family="Microsoft YaHei, SimHei, Arial, sans-serif"),
        xaxis=dict(
            tickmode='linear',
            dtick=1,
            tickangle=45,
            range=[1998.5, 2023.5]
        ),
        hovermode="x unified",
        showlegend=True
    )
    
    return fig

# 主函数
def main():
    st.title("📊 上市公司数字化转型指数查询系统")
    st.markdown("**查询1999-2023年上市公司的数字化转型指数数据**")
    
    # 加载数据
    df = load_data()
    
    if df is not None:
        # 筛选有效年份的数据
        df = df[(df['年份'] >= 1999) & (df['年份'] <= 2023)]
        
        # 核心查询区域
        with st.form("查询表单"):
            # 选择搜索方式
            search_method = st.radio("搜索方式", ['股票代码', '企业名称'], horizontal=True)
            
            # 根据搜索方式显示不同的选择框
            if search_method == '股票代码':
                selected_stock = st.selectbox("选择股票代码", df['股票代码'].unique())
                # 获取对应的企业名称
                company_name = df[df['股票代码'] == selected_stock]['企业名称'].iloc[0]
            else:
                selected_company = st.selectbox("选择企业名称", df['企业名称'].unique())
                company_name = selected_company
                # 获取对应的股票代码
                selected_stock = df[df['企业名称'] == selected_company]['股票代码'].iloc[0]
            
            # 年份选择
            year_options = sorted(df['年份'].unique())
            selected_year = st.selectbox("选择年份", year_options, index=0)
            
            # 提交按钮
            submitted = st.form_submit_button("查询")
        
        # 如果表单提交，显示结果
        if submitted or 'selected_company' not in st.session_state:
            # 保存当前选择到会话状态
            st.session_state.selected_company = company_name
            st.session_state.selected_stock = selected_stock
            st.session_state.selected_year = selected_year
        
        # 使用会话状态中的选择
        company_name = st.session_state.selected_company
        selected_stock = st.session_state.selected_stock
        selected_year = st.session_state.selected_year
        
        # 显示查询结果
        st.subheader(f"📈 {company_name} ({selected_stock}) 数字化转型指数")
        
        # 绘制单个公司的趋势图
        company_fig = plot_company_trend(df, company_name, selected_year, selected_stock)
        st.plotly_chart(company_fig, use_container_width=True)
        
        # 显示所有公司的趋势图
        st.subheader("📈 所有公司数字化转型指数整体趋势")
        all_fig = plot_all_companies_trend(df)
        st.plotly_chart(all_fig, use_container_width=True)
        
        # 显示选中年份的数据
        st.subheader(f"📊 {selected_year}年数据详情")
        company_year_data = df[(df['企业名称'] == company_name) & (df['年份'] == selected_year)]
        if not company_year_data.empty:
            st.dataframe(company_year_data, use_container_width=True)
        else:
            st.info(f"该公司在{selected_year}年没有数据")

if __name__ == "__main__":
    main()