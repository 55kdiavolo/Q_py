import pymysql
import re
from collections import defaultdict
from pyecharts import options as opts
from pyecharts.charts import Bar

# 连接数据库
connection = pymysql.connect(
    host='localhost',
    user='root',
    password='1234',
    db='jnweather',
    charset='utf8'
)
cursor = connection.cursor()

# 查询风向和风速数据
query = """
    SELECT YEAR(date) AS year, wind
    FROM ls_tq
"""
cursor.execute(query)
data = cursor.fetchall()
connection.close()

# 正则表达式提取风向
wind_direction_pattern = re.compile(r'([东南西北]+风)')

wind_direction_count = defaultdict(lambda: defaultdict(int))
for year, wind in data:
    match = wind_direction_pattern.match(wind)
    if match:
        wind_direction = match.group(1)
        wind_direction_count[year][wind_direction] += 1


def create_bar_chart(wind_direction_count):
    bar = Bar()

    for year, directions in wind_direction_count.items():
        bar.add_xaxis(list(directions.keys()))
        bar.add_yaxis(f"{year}年", list(directions.values()))

    bar.set_global_opts(
        title_opts=opts.TitleOpts(title="各年份风向统计"),
        xaxis_opts=opts.AxisOpts(name="风向"),
        yaxis_opts=opts.AxisOpts(name="天数"),
        legend_opts=opts.LegendOpts(is_show=True)
    )
    return bar


# 创建和渲染图表
bar_chart2 = create_bar_chart(wind_direction_count)
