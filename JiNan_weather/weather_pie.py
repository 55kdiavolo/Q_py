import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import Pie
import pymysql

# 连接数据库
connection = pymysql.connect(
    host='localhost',
    user='root',
    password='1234',
    db='jnweather',
    charset='utf8'
)
cursor = connection.cursor()

# 查询数据
query = """
    SELECT weather, date
    FROM ls_tq
"""
cursor.execute(query)
data = cursor.fetchall()
connection.close()

# 将数据转换为 DataFrame
df = pd.DataFrame(data, columns=['weather', 'date'])


# 预处理数据，拆分包含 ' ~ ' 的天气描述
def preprocess_weather(weather):
    return [desc.strip() for desc in weather.split('~')]


# 提取年份
df['year'] = pd.to_datetime(df['date']).dt.year

# 处理数据
weather_list = [(row['year'], desc) for _, row in df.iterrows() for desc in preprocess_weather(row['weather'])]

# 创建 DataFrame 以便统计
weather_df = pd.DataFrame(weather_list, columns=['year', 'weather'])

# 统计每种天气的频率按年份分组
weather_counts = weather_df.groupby(['year', 'weather']).size().reset_index(name='count')

# 存储图表的字典
pie_charts = {}

# 生成环形图并存储到字典
for year in weather_counts['year'].unique():
    year_data = weather_counts[weather_counts['year'] == year]

    pie = Pie()
    pie.add(
        series_name=f"天气分布 - {year}",
        data_pair=[(row['weather'], row['count']) for _, row in year_data.iterrows()],
        radius=["40%", "75%"],  # 设置内外半径
        center=["50%", "50%"]  # 设置中心位置
    )
    pie.set_global_opts(
        title_opts=opts.TitleOpts(
            title=f"天气环形图 - {year}",
            pos_left='center',  # 标题水平居中
            pos_top='90%'  # 标题垂直位置，接近图表底部
        ),
        legend_opts=opts.LegendOpts(
            is_show=True,
            orient="vertical",  # 图例垂直排列
            pos_left="85%",  # 图例水平位置
            pos_top="10%",  # 图例顶部位置
            padding=[10, 20, 10, 20]  # 内边距设置
        )

    )

    # 存储图表到字典
    pie_charts[year] = pie

    # 渲染图表到本地文件
