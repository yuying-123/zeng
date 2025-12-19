import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import os

# 设置页面配置
st.set_page_config(
    page_title="上市公司数字化转型指数查询系统",
    page_icon="📊",
    layout="wide"
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



# 绘制所有公司1999-2023年的折线图
def plot_all_companies_trend(data):
    """绘制所有公司1999-2023年的数字化转型指数趋势图"""
    # 过滤1999-2023年的数据
    filtered_data = data[(data['年份'] >= 1999) & (data['年份'] <= 2023)]
    
    # 计算每年的平均指数
    annual_avg = filtered_data.groupby('年份')['数字化转型指数'].mean().reset_index()
    
    # 创建完整的年份列表（1999-2023）
    full_years = pd.DataFrame({'年份': range(1999, 2024)})
    
    # 合并数据，确保每个年份都有数据
    annual_avg = pd.merge(full_years, annual_avg, on='年份', how='left')
    
    # 处理缺失值，使用前向填充和后向填充确保折线连续
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
        marker=dict(size=8, color='green')
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
            tickfont=dict(size=10),
            range=[1998.5, 2023.5]
        ),
        hovermode="x unified",
        showlegend=True
    )
    
    return fig

# 绘制公司分布地图
def plot_company_map(data):
    """绘制公司分布地图"""
    # 过滤1999-2023年的数据
    filtered_data = data[(data['年份'] >= 1999) & (data['年份'] <= 2023)]
    
    # 获取唯一的公司数据
    companies = filtered_data[['企业名称', '股票代码']].drop_duplicates()
    
    # 如果公司数量太多，随机选择一部分显示，避免地图过于拥挤
    if len(companies) > 1000:
        companies = companies.sample(n=1000, random_state=42)
    
    # 模拟经纬度数据（使用中国主要城市的大致范围）
    # 经度范围：73-135度（中国西到东）
    # 纬度范围：18-53度（中国南到北）
    np.random.seed(42)  # 设置随机种子，确保结果可重复
    companies['经度'] = np.random.uniform(100, 125, len(companies))  # 集中在中国东部
    companies['纬度'] = np.random.uniform(20, 45, len(companies))   # 集中在中国中南部
    
    # 确保有足够的数据点
    if len(companies) == 0:
        # 如果没有公司数据，创建一些示例数据
        sample_companies = pd.DataFrame({
            '企业名称': ['示例公司1', '示例公司2', '示例公司3'],
            '股票代码': ['000001', '000002', '000003'],
            '经度': [116.4074, 121.4737, 113.2644],  # 北京、上海、广州
            '纬度': [39.9042, 31.2304, 23.1291]       # 北京、上海、广州
        })
        companies = sample_companies
    
    # 使用go.Scattermapbox创建地图（更可靠的方式）
    fig = go.Figure()
    
    # 生成随机颜色列表
    colors = px.colors.qualitative.Plotly * (len(companies) // len(px.colors.qualitative.Plotly) + 1)
    colors = colors[:len(companies)]
    
    fig.add_trace(go.Scattermapbox(
        lat=companies['纬度'],
        lon=companies['经度'],
        mode='markers',
        marker=dict(
            size=10,
            color=colors,  # 使用随机颜色
            opacity=0.7
        ),
        text=companies['企业名称'] + ' (股票代码: ' + companies['股票代码'] + ')',
        hoverinfo='text'
    ))
    
    # 设置地图布局
    fig.update_layout(
        title='上市公司分布地图',
        mapbox=dict(
            style='open-street-map',  # 使用更可靠的地图样式
            center=dict(lat=35, lon=110),  # 中国中心位置
            zoom=4
        ),
        font=dict(family="Microsoft YaHei, SimHei, Arial, sans-serif"),
        height=600,
        margin=dict(l=0, r=0, t=50, b=0)
    )
    
    return fig

# 主函数
def main():
    st.title("📊 上市公司数字化转型指数查询系统")
    st.markdown("**查询1999-2023年上市公司的数字化转型指数数据**")
    
    # 加载数据
    df = load_data()
    
    if df is not None:
        # 添加筛选条件区域
        st.sidebar.subheader("数据筛选")
        
        # 行业筛选（如果数据中有行业字段）
        if '行业' in df.columns:
            selected_industry = st.sidebar.multiselect(
                "选择行业",
                df['行业'].unique(),
                default=[]
            )
        
        # 年份筛选 - 改为选择起始年份和结束年份
        min_year = 1999
        max_year = 2023
        year_options = list(range(min_year, max_year + 1))
        
        start_year = st.sidebar.selectbox(
            "起始年份",
            year_options,
            index=0,
            key="start_year_select"
        )
        
        # 结束年份只能选择大于等于起始年份的选项
        end_year_options = [year for year in year_options if year >= start_year]
        end_year = st.sidebar.selectbox(
            "结束年份",
            end_year_options,
            index=len(end_year_options) - 1,
            key="end_year_select"
        )
        
        # 设置年份范围
        selected_year_range = (start_year, end_year)
        
        # 指数范围筛选 - 改为选择最小值和最大值
        min_index = float(df['数字化转型指数'].min())
        max_index = float(df['数字化转型指数'].max())
        
        # 创建指数选项列表（按0.5间隔）
        index_step = 0.5
        index_options = [round(i, 1) for i in list(range(int(min_index * 2), int(max_index * 2) + 1))]
        index_options = [i / 2 for i in index_options]
        
        min_index_select = st.sidebar.selectbox(
            "最小指数",
            index_options,
            index=0,
            key="min_index_select"
        )
        
        # 最大指数只能选择大于等于最小指数的选项
        max_index_options = [index for index in index_options if index >= min_index_select]
        max_index_select = st.sidebar.selectbox(
            "最大指数",
            max_index_options,
            index=len(max_index_options) - 1,
            key="max_index_select"
        )
        
        # 设置指数范围
        selected_index_range = (min_index_select, max_index_select)
        
        # 应用筛选条件
        filtered_df = df.copy()
        if '行业' in df.columns and selected_industry:
            filtered_df = filtered_df[filtered_df['行业'].isin(selected_industry)]
        
        filtered_df = filtered_df[
            (filtered_df['年份'] >= selected_year_range[0]) & 
            (filtered_df['年份'] <= selected_year_range[1]) &
            (filtered_df['数字化转型指数'] >= selected_index_range[0]) &
            (filtered_df['数字化转型指数'] <= selected_index_range[1])
        ]
        # 数据基本统计
        total_records = len(df)
        total_companies = len(df['企业名称'].unique())
        min_year = df['年份'].min()
        max_year = df['年份'].max()
        
        # 创建左右两栏布局
        col1, col2 = st.columns([1, 3])
        
        # 左侧：查询条件
        with col1:
            st.subheader("查询条件")
            
            # 查询方式选择
            search_method = st.radio(
                "搜索方式",
                ['股票代码', '企业名称']
            )
            
            # 股票代码选择
            if search_method == '股票代码':
                selected_stock = st.selectbox(
                    "选择股票代码",
                    df['股票代码'].unique(),
                    key="stock_selectbox"
                )
                # 根据股票代码获取企业名称
                company_name = df[df['股票代码'] == selected_stock]['企业名称'].iloc[0]
            else:
                # 企业名称选择
                selected_company = st.selectbox(
                    "选择企业名称",
                    df['企业名称'].unique(),
                    key="company_selectbox"
                )
                # 根据企业名称获取股票代码
                selected_stock = df[df['企业名称'] == selected_company]['股票代码'].iloc[0]
                company_name = selected_company
            
            # 年份选择 - 只显示1999-2023年
            available_years = sorted(df['年份'].unique())
            filtered_years = [year for year in available_years if 1999 <= year <= 2023]
            
            selected_year = st.selectbox(
                "选择年份",
                filtered_years,
                key="year_selectbox_original"
            )
            
            # 执行查询按钮
            execute_query = st.button("执行查询", type="primary")
        
        # 右侧：结果展示
        with col2:
            # 数据概览卡片
            col_stats1, col_stats2, col_stats3 = st.columns(3)
            with col_stats1:
                st.metric("数据总量", f"{total_records:,}")
            with col_stats2:
                st.metric("企业数量", f"{total_companies:,}")
            with col_stats3:
                st.metric("年份跨度", "1999-2023")
            
            # 企业信息卡片
            st.subheader(f"{company_name} (股票代码: {selected_stock})")
            
            # 绘制趋势图
            st.subheader(f"{company_name}历年数字化转型指数趋势({min_year}-{max_year})")
            
            # 获取该企业的所有年份数据，过滤掉1998年和2024年
            company_data = df[df['股票代码'] == selected_stock]
            company_data = company_data[(company_data['年份'] >= 1999) & (company_data['年份'] <= 2023)]
            company_data = company_data.sort_values('年份')
            
            # 创建1999-2023年的完整年份列表
            full_years = pd.DataFrame({'年份': range(1999, 2024)})
            
            # 将企业数据与完整年份列表合并，确保每个年份都有数据点
            company_data = pd.merge(full_years, company_data, on='年份', how='left')
            
            # 对于缺失的数据点，使用前向填充
            company_data['数字化转型指数'] = company_data['数字化转型指数'].ffill()
            
            # 创建Plotly图表
            fig = go.Figure()
            
            # 添加趋势线，增大数据点大小使其更明显
            fig.add_trace(go.Scatter(
                x=company_data['年份'],
                y=company_data['数字化转型指数'],
                name='数字化转型指数',
                line=dict(color='blue', width=2),
                mode='lines+markers',
                marker=dict(size=8, color='blue', symbol='circle')  # 增大数据点大小
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
                    text=f'{selected_year}: {selected_year_data["数字化转型指数"].iloc[0]}',
                    textposition='top center'
                ))
            
            # 设置图表布局，限定x轴范围为1999-2023年
            fig.update_layout(
                title=f"{company_name} 数字化转型指数趋势",
                xaxis_title="年份",
                yaxis_title="数字化转型指数",
                font=dict(family="Microsoft YaHei, SimHei, Arial, sans-serif"),
                xaxis=dict(
                    tickmode='linear',
                    dtick=1,  # 每年显示一个刻度
                    tickangle=45,  # 标签旋转45度
                    tickfont=dict(size=10),  # 适当减小字体大小以避免拥挤
                    range=[1998.5, 2023.5]  # 限定x轴范围，不显示1998和2024年
                ),
                hovermode="x unified",
                showlegend=True
            )
            
            # 显示图表
            st.plotly_chart(fig, use_container_width=True, key="company_trend_chart")
            
            # 显示选中年份的详细数据
            if execute_query:
                st.subheader(f"{selected_year}年详细数据")
                st.dataframe(selected_year_data)
            
            # 显示筛选后的数据表格
            st.subheader("筛选后的数据列表")
            st.dataframe(filtered_df, use_container_width=True)
            
            # 显示所有公司的趋势图
            st.subheader("所有公司数字化转型指数趋势")
            all_companies_fig = plot_all_companies_trend(df)
            st.plotly_chart(all_companies_fig, use_container_width=True, key="all_companies_trend_chart")
            
            # 添加新的筛选条件和数据表格区域
            st.markdown("---")
            st.header("数据查询与表格展示")
            
            # 创建新的左右布局
            filter_col, table_col = st.columns([1, 3])
            
            # 左侧筛选条件区域
            with filter_col:
                st.subheader("筛选条件")
                
                # 按股票代码搜索
                stock_code_input = st.text_input("输入股票代码，如：600000")
                
                # 选择年份下拉框
                year_options = sorted(df['年份'].unique())
                selected_year = st.selectbox("选择年份", year_options, index=0, key="year_selectbox_new")
                
                # 按企业名称搜索
                company_name_input = st.text_input("输入企业名称，如：浦发银行")
            
            # 右侧数据表格区域
            with table_col:
                # 应用筛选条件
                filtered_table_data = df.copy()
                
                # 按股票代码筛选
                if stock_code_input:
                    filtered_table_data = filtered_table_data[filtered_table_data['股票代码'].str.contains(stock_code_input, case=False)]
                
                # 按年份筛选
                filtered_table_data = filtered_table_data[filtered_table_data['年份'] == selected_year]
                
                # 按企业名称筛选
                if company_name_input:
                    filtered_table_data = filtered_table_data[filtered_table_data['企业名称'].str.contains(company_name_input, case=False)]
                
                # 显示筛选结果数量
                st.subheader("筛选结果")
                st.success(f"找到 {len(filtered_table_data)} 条符合条件的数据")
                
                # 确保表格包含所需列
                required_columns = ['股票代码', '企业名称', '年份', '数字化转型指数']
                if '行业名称' in filtered_table_data.columns:
                    required_columns.insert(3, '行业名称')
                if '技术维度' in filtered_table_data.columns:
                    required_columns.append('技术维度')
                if '应用维度' in filtered_table_data.columns:
                    required_columns.append('应用维度')
                
                # 显示数据表格
                st.subheader("数据表格")
                st.dataframe(filtered_table_data[required_columns], use_container_width=True)
            
            # 显示公司分布地图
            st.subheader("上市公司分布地图")
            map_fig = plot_company_map(df)
            st.plotly_chart(map_fig, use_container_width=True, key="company_distribution_map")

if __name__ == "__main__":
    main()