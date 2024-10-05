import pymysql
import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import WordCloud

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
    SELECT weather
    FROM ls_tq
"""
cursor.execute(query)
data = cursor.fetchall()
connection.close()

# 将数据转换为 DataFrame
df = pd.DataFrame(data, columns=['weather'])

# 预处理数据，拆分包含 ' ~ ' 的天气描述
def preprocess_weather(weather):
    # 拆分并返回所有天气描述
    return [desc.strip() for desc in weather.split('~')]

# 应用预处理
weather_list = [desc for weather in df['weather'] for desc in preprocess_weather(weather)]

# 统计每种天气的频率
weather_counts = pd.Series(weather_list).value_counts()

# 创建词云数据
wordcloud_data = [(word, count) for word, count in weather_counts.items()]

# 生成词云图
wordcloud = WordCloud()
wordcloud.add(
    series_name="天气词云",
    data_pair=wordcloud_data,
    word_size_range=[20, 100]  # 词语大小范围
)
wordcloud.set_global_opts(
    title_opts=opts.TitleOpts(title="天气词云"),
    tooltip_opts=opts.TooltipOpts(is_show=False)
)


