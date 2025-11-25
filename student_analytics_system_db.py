#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""学生消费行为分析系统（数据库版）"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import os
import warnings
from utils.db_connection import db_conn

# 忽略警告
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class StudentAnalyticsSystem:
    """学生消费行为分析系统（从数据库读取数据）"""
    
    def __init__(self):
        self.data1 = None  # 学生信息
        self.data2 = None  # 消费记录
        self.data3 = None  # 门禁记录
        self.consumption = None  # 合并后的消费数据
        self.access = None  # 合并后的门禁数据
        self.analysis_results = {}  # 分析结果
        self.figures = {}  # 图表对象
        
    def load_raw_data(self):
        """从数据库加载原始数据"""
        try:
            print("🚀 系统启动：正在从数据库加载原始数据...")
            
            # 连接数据库
            if not db_conn.connect():
                raise Exception("无法连接到数据库")
            
            # 加载学生信息
            print("📚 加载学生信息表...")
            query_students = """
                SELECT id, card_no, sex, major, access_card_no 
                FROM students 
                ORDER BY id
            """
            self.data1 = db_conn.get_dataframe(query_students)
            
            # 加载消费记录
            print("💳 加载消费记录表...")
            query_consumption = """
                SELECT id, card_no, date_time, money, dept 
                FROM consumption_records 
                ORDER BY date_time
            """
            self.data2 = db_conn.get_dataframe(query_consumption)
            
            # 加载门禁记录
            print("🚪 加载门禁记录表...")
            query_access = """
                SELECT id, access_card_no, date_time, address, access, describe_text 
                FROM access_records 
                ORDER BY date_time
            """
            self.data3 = db_conn.get_dataframe(query_access)
            
            # 检查数据是否成功加载
            if self.data1 is None or self.data2 is None or self.data3 is None:
                raise Exception("❌ 无法加载数据库表")
                
            print(f"✅ 数据加载完成：")
            print(f"  - 学生信息: {len(self.data1)} 条")
            print(f"  - 消费记录: {len(self.data2)} 条")
            print(f"  - 门禁记录: {len(self.data3)} 条")
            
        except Exception as e:
            print(f"❌ 数据加载失败: {str(e)}")
            raise
        finally:
            # 关闭数据库连接
            db_conn.disconnect()
    
    def clean_data(self):
        """清洗数据"""
        try:
            print("🧹 正在清洗数据...")
            
            # data1清洗 - 学生信息
            if len(self.data1.columns) >= 5:
                # 重命名列以便后续处理
                self.data1.columns = ['序号', '校园卡号', '性别', '专业名称', '门禁卡号']
                
                # 尝试修复性别编码问题
                self.data1['性别'] = self.data1['性别'].apply(lambda x: '男' if str(x).strip() in ['男', 'M', 'm', '��', '1'] else 
                                                            ('女' if str(x).strip() in ['女', 'F', 'f', 'Ů', '2'] else x))
            
            # data2清洗 - 消费记录
            if len(self.data2.columns) >= 5:
                # 重命名列以便后续处理
                self.data2.columns = ['流水号', '校园卡号', '消费时间', '消费金额', '消费地点']
                
                # 确保消费时间是datetime类型
                if not pd.api.types.is_datetime64_any_dtype(self.data2['消费时间']):
                    try:
                        self.data2['消费时间'] = pd.to_datetime(self.data2['消费时间'])
                    except:
                        date_formats = ['%Y/%m/%d %H:%M', '%Y-%m-%d %H:%M', '%d/%m/%Y %H:%M']
                        for fmt in date_formats:
                            try:
                                self.data2['消费时间'] = pd.to_datetime(self.data2['消费时间'], format=fmt, errors='coerce')
                                if not self.data2['消费时间'].isna().all():
                                    break
                            except:
                                continue
                
                # 清理无效数据
                self.data2 = self.data2.dropna(subset=['消费时间', '消费地点'])
                # 过滤异常金额
                self.data2 = self.data2[(self.data2['消费金额'] > 0) & (self.data2['消费金额'] < 1000)]
            
            # data3清洗 - 门禁记录
            if len(self.data3.columns) >= 6:
                # 重命名列以便后续处理
                self.data3.columns = ['序号', '门禁卡号', '进出时间', '进出地点', '是否通过', '描述']
                
                # 确保进出时间是datetime类型
                if not pd.api.types.is_datetime64_any_dtype(self.data3['进出时间']):
                    try:
                        self.data3['进出时间'] = pd.to_datetime(self.data3['进出时间'])
                    except:
                        date_formats = ['%Y/%m/%d %H:%M', '%Y-%m-%d %H:%M', '%d/%m/%Y %H:%M']
                        for fmt in date_formats:
                            try:
                                self.data3['进出时间'] = pd.to_datetime(self.data3['进出时间'], format=fmt, errors='coerce')
                                if not self.data3['进出时间'].isna().all():
                                    break
                            except:
                                continue
                
                self.data3 = self.data3.dropna(subset=['进出时间'])
                self.data3 = self.data3[self.data3['是否通过'] == 1]
            
            print(f"✅ 数据清洗完成")
            
        except Exception as e:
            print(f"❌ 数据清洗失败: {str(e)}")
            raise
    
    def merge_data(self):
        """合并数据"""
        try:
            print("🔗 正在合并数据...")
            
            # 学生信息 + 消费记录
            self.consumption = pd.merge(self.data1, self.data2, on='校园卡号', how='inner')
            # 学生信息 + 门禁记录
            self.access = pd.merge(self.data1, self.data3, on='门禁卡号', how='inner')
            
            print(f"✅ 数据合并完成：")
            print(f"  - 消费分析数据集: {len(self.consumption)} 条")
            print(f"  - 门禁分析数据集: {len(self.access)} 条")
            
        except Exception as e:
            print(f"❌ 数据合并失败: {str(e)}")
            raise
    
    def preprocess_for_analysis(self):
        """为分析做预处理"""
        # 添加时间维度特征
        if self.consumption is not None:
            self.consumption['日期'] = self.consumption['消费时间'].dt.date
            self.consumption['小时'] = self.consumption['消费时间'].dt.hour
            self.consumption['星期'] = self.consumption['消费时间'].dt.dayofweek + 1  # 1-7
            self.consumption['月份'] = self.consumption['消费时间'].dt.month
            
            # 添加时间段分类
            def get_time_period(hour):
                if 0 <= hour < 6:
                    return '凌晨'
                elif 6 <= hour < 12:
                    return '上午'
                elif 12 <= hour < 14:
                    return '中午'
                elif 14 <= hour < 18:
                    return '下午'
                elif 18 <= hour < 22:
                    return '晚上'
                else:
                    return '深夜'
            
            self.consumption['时间段'] = self.consumption['小时'].apply(get_time_period)
    
    def analyze_gender_consumption(self):
        """性别消费分析"""
        print("📊 正在进行性别消费分析...")
        
        # 总消费金额分析
        gender_total = self.consumption.groupby('性别')['消费金额'].sum().reset_index()
        gender_count = self.consumption.groupby('性别')['校园卡号'].nunique().reset_index()
        gender_count.columns = ['性别', '学生数量']
        
        # 人均消费
        gender_analysis = pd.merge(gender_total, gender_count, on='性别')
        gender_analysis['人均消费'] = gender_analysis['消费金额'] / gender_analysis['学生数量']
        
        self.analysis_results['gender_analysis'] = gender_analysis
        
        # 创建更美观的可视化
        fig = make_subplots(rows=1, cols=2, specs=[[{'type': 'bar'}, {'type': 'bar'}]], 
                           subplot_titles=('男女总消费金额对比', '男女人均消费对比'))
        
        fig.add_trace(go.Bar(x=gender_analysis['性别'], y=gender_analysis['消费金额'], 
                            marker_color=['#4472C4', '#ED7D31'], name='总消费金额'), row=1, col=1)
        fig.add_trace(go.Bar(x=gender_analysis['性别'], y=gender_analysis['人均消费'], 
                            marker_color=['#70AD47', '#FFC000'], name='人均消费'), row=1, col=2)
        
        fig.update_layout(title_text="性别维度消费分析", height=500, template='plotly_white')
        self.figures['gender_analysis'] = fig
        
        return gender_analysis
    
    def analyze_major_consumption(self):
        """专业消费分析"""
        print("📊 正在进行专业消费分析...")
        
        # 专业消费总额排序
        major_analysis = self.consumption.groupby('专业名称')['消费金额'].sum().reset_index()
        major_analysis = major_analysis.sort_values(by='消费金额', ascending=False)
        
        # 取前15个专业进行展示
        top_majors = major_analysis.head(15)
        self.analysis_results['major_analysis'] = major_analysis
        
        # 创建交互式条形图
        fig = px.bar(top_majors, x='消费金额', y='专业名称', orientation='h',
                    title='各专业消费金额排名（前15）', color='消费金额',
                    color_continuous_scale='Viridis', text_auto='.0f',
                    labels={'消费金额': '总消费金额（元）', '专业名称': '专业'})
        
        fig.update_layout(height=600, template='plotly_white', margin={'l': 150})
        self.figures['major_analysis'] = fig
        
        return major_analysis
    
    def analyze_canteen_distribution(self):
        """食堂消费分布分析"""
        print("📊 正在进行食堂消费分布分析...")
        
        # 消费地点分布
        canteen_counts = self.consumption['消费地点'].value_counts().head(8)
        canteen_amounts = self.consumption.groupby('消费地点')['消费金额'].sum().sort_values(ascending=False).head(8)
        
        self.analysis_results['canteen_counts'] = canteen_counts
        self.analysis_results['canteen_amounts'] = canteen_amounts
        
        # 创建饼图和条形图组合
        fig = make_subplots(rows=1, cols=2, specs=[[{'type': 'pie'}, {'type': 'bar'}]],
                           subplot_titles=('消费次数分布', '消费金额分布'))
        
        fig.add_trace(go.Pie(labels=canteen_counts.index, values=canteen_counts.values,
                            hole=0.3, name='消费次数', textinfo='label+percent'), row=1, col=1)
        
        fig.add_trace(go.Bar(x=canteen_amounts.values, y=canteen_amounts.index, orientation='h',
                            marker_color='royalblue', name='消费金额'), row=1, col=2)
        
        fig.update_layout(title_text="消费地点分析", height=500, template='plotly_white')
        self.figures['canteen_analysis'] = fig
        
        return canteen_counts, canteen_amounts
    
    def analyze_time_patterns(self):
        """时间模式分析"""
        print("📊 正在进行时间模式分析...")
        
        # 时间段消费分析
        time_period_analysis = self.consumption.groupby('时间段')['消费金额'].agg(['sum', 'count']).reset_index()
        time_period_analysis.columns = ['时间段', '总金额', '次数']
        
        # 按合理顺序排列时间段
        period_order = ['凌晨', '上午', '中午', '下午', '晚上', '深夜']
        time_period_analysis['时间段'] = pd.Categorical(time_period_analysis['时间段'], categories=period_order, ordered=True)
        time_period_analysis = time_period_analysis.sort_values('时间段')
        
        # 每日消费趋势
        daily_trend = self.consumption.groupby('日期')['消费金额'].sum().reset_index()
        daily_trend['日期'] = pd.to_datetime(daily_trend['日期'])
        
        self.analysis_results['time_period_analysis'] = time_period_analysis
        self.analysis_results['daily_trend'] = daily_trend
        
        # 创建时间模式分析图表
        fig = make_subplots(rows=2, cols=1, subplot_titles=('不同时间段消费分布', '每日消费金额趋势'),
                           vertical_spacing=0.2)
        
        fig.add_trace(go.Bar(x=time_period_analysis['时间段'], y=time_period_analysis['总金额'],
                            marker_color='lightgreen', name='时间段消费'), row=1, col=1)
        
        fig.add_trace(go.Scatter(x=daily_trend['日期'], y=daily_trend['消费金额'],
                               mode='lines+markers', line=dict(color='royalblue', width=2),
                               name='每日消费'), row=2, col=1)
        
        fig.update_layout(height=700, template='plotly_white', title_text="消费时间模式分析")
        self.figures['time_analysis'] = fig
        
        return time_period_analysis, daily_trend
    
    def analyze_consumption_distribution(self):
        """消费金额分布分析"""
        print("📊 正在进行消费金额分布分析...")
        
        # 消费金额分布
        consumption_ranges = pd.cut(self.consumption['消费金额'], 
                                   bins=[0, 5, 10, 20, 50, 100, float('inf')],
                                   labels=['0-5元', '5-10元', '10-20元', '20-50元', '50-100元', '100元以上'])
        
        range_distribution = consumption_ranges.value_counts().sort_index()
        self.analysis_results['range_distribution'] = range_distribution
        
        # 创建消费金额分布图
        fig = go.Figure()
        fig.add_trace(go.Bar(x=range_distribution.index, y=range_distribution.values,
                            marker_color='skyblue', name='交易次数'))
        
        fig.update_layout(title='单笔消费金额分布',
                        xaxis_title='消费金额区间',
                        yaxis_title='交易次数',
                        template='plotly_white',
                        height=500)
        
        self.figures['consumption_distribution'] = fig
        return range_distribution
    
    def analyze_all(self):
        """执行所有分析"""
        try:
            print("📊 开始数据分析...")
            
            # 预处理
            self.preprocess_for_analysis()
            
            # 执行各项分析
            self.analyze_gender_consumption()
            self.analyze_major_consumption()
            self.analyze_canteen_distribution()
            self.analyze_time_patterns()
            self.analyze_consumption_distribution()
            
            print("✅ 所有分析完成")
            
        except Exception as e:
            print(f"❌ 数据分析失败: {str(e)}")
            raise
    
    def save_figures(self, output_dir='.'):
        """保存图表为HTML文件"""
        try:
            print("💾 正在保存交互式图表...")
            
            for name, fig in self.figures.items():
                html_path = os.path.join(output_dir, f'{name}_plot.html')
                fig.write_html(html_path, include_plotlyjs='cdn')
                print(f"  - 已保存: {html_path}")
            
            # 暂时注释掉静态图片保存，需要安装kaleido包
            # for name, fig in self.figures.items():
            #     img_path = os.path.join(output_dir, f'{name}.png')
            #     fig.write_image(img_path, width=1200, height=800, scale=2)
            #     print(f"  - 已保存: {img_path}")
            # 生成模拟的图片路径用于HTML报告
            for name in self.figures.keys():
                print(f"  - 模拟图片路径: {name}.png")
                
        except Exception as e:
            print(f"❌ 图表保存失败: {str(e)}")
            raise
    
    def generate_report(self):
        """生成美观的HTML分析报告"""
        try:
            print("📄 正在生成分析报告...")
            
            # 获取分析结果
            gender_df = self.analysis_results['gender_analysis']
            major_df = self.analysis_results['major_analysis']
            daily_df = self.analysis_results['daily_trend']
            canteen_counts = self.analysis_results['canteen_counts']
            
            # 生成统计摘要
            total_students = self.consumption['校园卡号'].nunique()
            total_transactions = len(self.consumption)
            total_amount = self.consumption['消费金额'].sum()
            avg_transaction = self.consumption['消费金额'].mean()
            
            # 生成HTML报告
            html = f'''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>学生消费行为分析报告</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            background-color: #f8f9fa;
            color: #333;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 60px 0;
            margin-bottom: 40px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        .header h1 {{
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 10px;
        }}
        .header p {{
            font-size: 1.2rem;
            opacity: 0.9;
        }}
        .section {{
            background: white;
            border-radius: 10px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        }}
        .section-title {{
            color: #495057;
            font-weight: 700;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e9ecef;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            text-align: center;
            transition: transform 0.3s ease;
        }}
        .stat-card:hover {{
            transform: translateY(-5px);
        }}
        .stat-number {{
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 5px;
        }}
        .stat-label {{
            font-size: 1rem;
            opacity: 0.9;
        }}
        .chart-container {{
            margin-top: 30px;
            margin-bottom: 30px;
        }}
        .highlight {{
            background-color: #fff3cd;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #ffc107;
            margin: 15px 0;
        }}
        .recommendation {{
            background-color: #d1ecf1;
            padding: 20px;
            border-radius: 8px;
            margin-top: 20px;
        }}
        .list-group-item {{
            border: none;
            padding: 10px 0;
            border-bottom: 1px solid #e9ecef;
        }}
        .list-group-item:last-child {{
            border-bottom: none;
        }}
        .data-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        .data-table th, .data-table td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        .data-table th {{
            background-color: #f8f9fa;
            font-weight: 600;
            color: #495057;
        }}
        .data-table tr:hover {{
            background-color: #f8f9fa;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="container">
            <h1>学生消费行为分析报告</h1>
            <p>基于数据库数据的智能分析 | 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>

    <div class="container">
        <!-- 数据感知部分 -->
        <div class="section">
            <h2 class="section-title">📊 数据感知</h2>
            <p>本次分析基于学校提供的学生消费和行为数据，旨在深入了解学生消费行为模式，为学校优化服务提供数据支持。</p>
            
            <div class="row mt-4">
                <div class="col-md-3">
                    <div class="stat-card">
                        <div class="stat-number">{total_students:,}</div>
                        <div class="stat-label">参与学生</div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-card">
                        <div class="stat-number">{total_transactions:,}</div>
                        <div class="stat-label">消费交易</div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-card">
                        <div class="stat-number">¥{total_amount:,.2f}</div>
                        <div class="stat-label">总消费金额</div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-card">
                        <div class="stat-number">¥{avg_transaction:.2f}</div>
                        <div class="stat-label">平均交易额</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 数据分析部分 -->
        <div class="section">
            <h2 class="section-title">📈 数据分析</h2>
            
            <!-- 性别维度分析 -->
            <div class="mb-6">
                <h3 class="text-lg font-semibold mb-3">1. 性别维度分析</h3>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>性别</th>
                            <th>总消费金额 (元)</th>
                            <th>学生数量</th>
                            <th>人均消费 (元)</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join([f'<tr><td>{row["性别"]}</td><td>{row["消费金额"]:.2f}</td><td>{row["学生数量"]}</td><td>{row["人均消费"]:.2f}</td></tr>' for _, row in gender_df.iterrows()])}
                    </tbody>
                </table>
                <div class="chart-container">
                    <iframe src="gender_analysis_plot.html" width="100%" height="500" frameborder="0"></iframe>
                </div>
            </div>
            
            <!-- 专业维度分析 -->
            <div class="mb-6">
                <h3 class="text-lg font-semibold mb-3">2. 专业维度分析</h3>
                <div class="highlight">
                    <p>消费最高的专业: <strong>{major_df.iloc[0]['专业名称']}</strong>，消费金额: <strong>¥{major_df.iloc[0]['消费金额']:,.2f}</strong></p>
                </div>
                <div class="chart-container">
                    <iframe src="major_analysis_plot.html" width="100%" height="600" frameborder="0"></iframe>
                </div>
            </div>
            
            <!-- 消费地点分析 -->
            <div class="mb-6">
                <h3 class="text-lg font-semibold mb-3">3. 消费地点分析</h3>
                <div class="highlight">
                    <p>最受欢迎的消费地点: <strong>{canteen_counts.index[0]}</strong>，消费次数: <strong>{canteen_counts.iloc[0]}</strong>次</p>
                </div>
                <div class="chart-container">
                    <iframe src="canteen_analysis_plot.html" width="100%" height="500" frameborder="0"></iframe>
                </div>
            </div>
            
            <!-- 时间模式分析 -->
            <div class="mb-6">
                <h3 class="text-lg font-semibold mb-3">4. 时间模式分析</h3>
                <div class="chart-container">
                    <iframe src="time_analysis_plot.html" width="100%" height="700" frameborder="0"></iframe>
                </div>
            </div>
            
            <!-- 消费金额分布 -->
            <div>
                <h3 class="text-lg font-semibold mb-3">5. 消费金额分布</h3>
                <div class="chart-container">
                    <iframe src="consumption_distribution_plot.html" width="100%" height="500" frameborder="0"></iframe>
                </div>
            </div>
        </div>

        <!-- 总结部分 -->
        <div class="section">
            <h2 class="section-title">📋 总结</h2>
            
            <div class="recommendation">
                <h3 class="text-lg font-semibold mb-3">🎯 关键发现</h3>
                <ul class="list-group">
                    <li class="list-group-item">
                        <strong>性别差异：</strong>
                        {"男生人均消费高于女生" if gender_df[gender_df['性别']=='男']['人均消费'].values[0] > gender_df[gender_df['性别']=='女']['人均消费'].values[0] else "女生人均消费高于男生"}
                    </li>
                    <li class="list-group-item">
                        <strong>专业差异：</strong>
                        不同专业间消费差异明显，建议针对高消费专业优化服务
                    </li>
                    <li class="list-group-item">
                        <strong>地点偏好：</strong>
                        {canteen_counts.index[0]}是最受欢迎的消费地点，应确保服务质量
                    </li>
                    <li class="list-group-item">
                        <strong>时间规律：</strong>
                        消费行为呈现明显的时间规律，可据此优化资源配置
                    </li>
                </ul>
            </div>
            
            <div class="recommendation mt-4">
                <h3 class="text-lg font-semibold mb-3">💡 改进建议</h3>
                <ul class="list-group">
                    <li class="list-group-item">
                        <strong>资源配置：</strong>
                        在消费高峰期增加服务人员，提高服务效率
                    </li>
                    <li class="list-group-item">
                        <strong>个性化服务：</strong>
                        根据不同性别和专业的消费特点，提供更有针对性的服务
                    </li>
                    <li class="list-group-item">
                        <strong>营销策略：</strong>
                        在消费低谷期推出优惠活动，平衡消费时段分布
                    </li>
                    <li class="list-group-item">
                        <strong>数据质量：</strong>
                        建议进一步完善数据收集，提高数据准确性和完整性
                    </li>
                </ul>
            </div>
        </div>
    </div>

    <footer class="mt-5 py-4 bg-dark text-white text-center">
        <div class="container">
            <p>&copy; {datetime.now().year} 学生消费行为分析系统 | 基于生成式人工智能技术</p>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''
            
            # 保存报告
            report_path = os.path.join(os.getcwd(), 'report_db.html')
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(html)
            
            print(f"✅ 报告已生成：{report_path}")
            return report_path
            
        except Exception as e:
            print(f"❌ 报告生成失败: {str(e)}")
            raise
    
    def run(self):
        """运行整个分析流程"""
        try:
            # 加载数据
            self.load_raw_data()
            # 清洗数据
            self.clean_data()
            # 合并数据
            self.merge_data()
            # 执行分析
            self.analyze_all()
            # 保存图表
            self.save_figures()
            # 生成报告
            report_path = self.generate_report()
            
            print("🎉 所有任务完成！")
            print(f"📄 请查看分析报告: {report_path}")
            
        except Exception as e:
            print(f"❌ 系统运行失败: {str(e)}")
            raise

# 主函数
if __name__ == '__main__':
    system = StudentAnalyticsSystem()
    system.run()