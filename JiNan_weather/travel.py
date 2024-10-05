import pymysql
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

# 查询数据
query = """
    SELECT YEAR(date) AS year, weather, high_temperature, low_temperature, aqi
    FROM ls_tq
"""
cursor.execute(query)
data = cursor.fetchall()
connection.close()


# 定义不适宜出行的天气条件
def is_unfit_for_travel(weather, high_temperature, low_temperature, aqi):
    if any(keyword in weather for keyword in ["雨", "雪", "雾", '扬沙', '霾', '浮尘']):
        return True
    try:
        high_temp = float(high_temperature)
        low_temp = float(low_temperature)
        a = float(aqi)
    except ValueError:
        return True  # 如果温度值无法转换为数字，则认为不适宜出行

    if high_temp >= 35 or low_temp <= -10:
        return True
    if a >= 100:
        return True

    return False


# 统计每年适宜和不适宜出行的天数
travel_fit_count = defaultdict(int)
travel_unfit_count = defaultdict(int)

for year, weather, high_temp, low_temp, aqi in data:
    if is_unfit_for_travel(weather, high_temp, low_temp, aqi):
        travel_unfit_count[year] += 1
    else:
        travel_fit_count[year] += 1


def create_bar_chart(travel_fit_count, travel_unfit_count):
    bar = Bar()

    # 获取所有年份
    all_years = sorted(set(travel_fit_count.keys()).union(travel_unfit_count.keys()))

    # 准备数据
    fit_counts = [travel_fit_count.get(year, 0) for year in all_years]
    unfit_counts = [travel_unfit_count.get(year, 0) for year in all_years]

    # 添加 x 轴数据 (年份) 和 y 轴数据 (天数)
    bar.add_xaxis(all_years)
    bar.add_yaxis("适宜出行", fit_counts)
    bar.add_yaxis("不适宜出行", unfit_counts)

    # 设置全局选项
    bar.set_global_opts(
        title_opts=opts.TitleOpts(title="每年适宜与不适宜出行天数统计"),
        xaxis_opts=opts.AxisOpts(name="天数"),
        yaxis_opts=opts.AxisOpts(name="年份"),
    )

    # 翻转 x 轴和 y 轴
    bar.reversal_axis()

    return bar


# 创建和渲染图表
bar_chart = create_bar_chart(travel_fit_count, travel_unfit_count)
