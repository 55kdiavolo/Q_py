import pymysql
import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import Line, Page
from travel import bar_chart
from wind import bar_chart2
from weather_pie import pie_charts
from weather_ciyun import wordcloud  # 词云


# 数据库配置
def create_connection():
    """创建与MySQL数据库的连接。"""
    return pymysql.connect(
        host='localhost',  # 数据库主机
        port=3306,  # 数据库端口
        user='root',  # 用户名
        password='1234',  # 密码
        db='jnweather',  # 数据库名称
        charset='utf8'  # 字符集
    )


# 月平均气温走势
def t():
    """生成月平均气温的折线图。"""
    conn = create_connection()  # 建立数据库连接
    query_t = "SELECT date, high_temperature, low_temperature FROM ls_tq"  # SQL查询
    df_t = pd.read_sql(query_t, con=conn)  # 将数据读取到DataFrame中
    conn.close()  # 关闭连接

    df_t['date'] = pd.to_datetime(df_t['date'])  # 将日期列转换为datetime格式
    df_t['high_temperature'] = df_t['high_temperature'].astype(float)  # 确保温度列为浮点数
    df_t['low_temperature'] = df_t['low_temperature'].astype(float)
    df_t['month'] = df_t['date'].dt.to_period('M')  # 从日期中提取月份

    # 按月份分组，计算平均温度
    monthly_avg_temps = df_t.groupby('month').agg({'high_temperature': 'mean', 'low_temperature': 'mean'})
    monthly_avg_temps = monthly_avg_temps.round().astype(int)  # 四舍五入并转换为整数

    line_chart = Line()  # 创建折线图
    months = monthly_avg_temps.index.astype(str).tolist()  # 将月份索引转换为字符串

    # 向折线图添加数据
    line_chart.add_xaxis(months)
    line_chart.add_yaxis("月平均最高气温", monthly_avg_temps['high_temperature'].tolist(), color='red')  # 高温系列
    line_chart.add_yaxis("月平均最低气温", monthly_avg_temps['low_temperature'].tolist(), color='blue')  # 低温系列

    # 设置图表的全局选项
    line_chart.set_global_opts(
        title_opts=opts.TitleOpts(title="月平均气温走势图"),
        xaxis_opts=opts.AxisOpts(
            name="月份",
            axislabel_opts=opts.LabelOpts(rotate=-45),  # 旋转x轴标签以提高可读性
            axisline_opts=opts.AxisLineOpts(),
            axistick_opts=opts.AxisTickOpts(is_inside=True),
            splitline_opts=opts.SplitLineOpts(is_show=True)  # 显示网格线
        ),
        yaxis_opts=opts.AxisOpts(
            name="气温",
            axisline_opts=opts.AxisLineOpts(),
            axistick_opts=opts.AxisTickOpts(is_inside=True),
            splitline_opts=opts.SplitLineOpts(is_show=True)
        ),
        tooltip_opts=opts.TooltipOpts(trigger="axis"),  # 悬停时显示工具提示
        datazoom_opts=[
            opts.DataZoomOpts(type_="slider"),  # 启用滑动缩放
            opts.DataZoomOpts(type_="inside")  # 启用内部缩放
        ]
    )
    return line_chart  # 返回创建的折线图


# 月平均AQI
def aqi():
    """生成月平均空气质量指数(AQI)的折线图。"""
    conn = create_connection()  # 建立数据库连接
    query_aqi = "SELECT date, aqi FROM ls_tq"  # SQL查询AQI
    df_aqi = pd.read_sql(query_aqi, conn)  # 将AQI数据读取到DataFrame中
    conn.close()  # 关闭连接

    df_aqi['aqi'] = pd.to_numeric(df_aqi['aqi'], errors='coerce')  # 将AQI转换为浮点型
    df_aqi = df_aqi.dropna(subset=['aqi'])  # 删除AQI值为NaN的行
    df_aqi['date'] = pd.to_datetime(df_aqi['date'])  # 将日期转换为datetime格式
    df_aqi['year_month'] = df_aqi['date'].dt.to_period('M')  # 提取年月

    # 按年月分组，计算平均AQI
    monthly_avg_aqi = df_aqi.groupby('year_month')['aqi'].mean().reset_index()

    monthly_avg_aqi['aqi'] = monthly_avg_aqi['aqi'].round().astype(int)  # 四舍五入并转换为整数
    monthly_avg_aqi['year_month'] = monthly_avg_aqi['year_month'].astype(str)  # 将周期转换为字符串

    # 创建AQI的折线图
    line_chart = (
        Line()
            .add_xaxis(monthly_avg_aqi['year_month'].tolist())  # X轴
            .add_yaxis("平均AQI", monthly_avg_aqi['aqi'].tolist())  # Y轴
            .set_global_opts(
            title_opts=opts.TitleOpts(title="月平均空气质量指数走势图"),
            xaxis_opts=opts.AxisOpts(name="月份", type_="category"),
            yaxis_opts=opts.AxisOpts(name="平均AQI"),
            datazoom_opts=opts.DataZoomOpts()  # 启用AQI图表的缩放
        )
    )
    return line_chart  # 返回创建的AQI折线图


# 生成图表
monthly_avg_aqi = aqi()  # 创建AQI图表
monthly_avg_t = t()  # 创建温度图表

# 创建一个页面以容纳多个图表
page = Page(layout=Page.DraggablePageLayout)
for year, pie_chart in pie_charts.items():  # 添加自定义模块中的饼图
    page.add(pie_chart)
page.add(monthly_avg_aqi, monthly_avg_t, bar_chart, bar_chart2, wordcloud)  # 添加其他图表

# 将所有图表渲染到一个HTML文件中
page.render('总页面.html')
