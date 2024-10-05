from selenium import webdriver
from bs4 import BeautifulSoup
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pymysql


def insert(date, weather, high_temperature, low_temperature, wind, AQI, air_quality):
    sql = 'INSERT INTO ls_tq (date, weather, high_temperature, low_temperature, wind, AQI, air_quality) VALUES (%s, %s, %s, %s, %s, %s, %s)'
    try:
        cursor.execute(sql, (date, weather, high_temperature, low_temperature, wind, AQI, air_quality))
    except pymysql.MySQLError as e:
        print(f"Error: {e}")


# MySQL 数据库配置
connect = pymysql.connect(
    host='localhost',
    port=3306,
    user='root',
    password='1234',
    db='jnweather',
    charset='utf8'
)

cursor = connect.cursor()

# 设置 WebDriver
qd = webdriver.Firefox()
url = 'https://tianqi.2345.com/wea_history/54823.htm'
qd.get(url)

try:
    for i in range(63):
        # 通过浏览器解析获取网页信息
        WebDriverWait(qd, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'tr')))
        ym = qd.page_source
        jxym = BeautifulSoup(ym, 'html.parser')

        data = jxym.find_all('tr')
        for row in data:
            columns = row.find_all('td')
            if len(columns) < 6:
                continue  # 如果 <td> 标签少于6个，跳过该行

            date = columns[0].get_text(strip=True).split()[0]
            max_temp = columns[1].get_text(strip=True).replace('°', '')
            min_temp = columns[2].get_text(strip=True).replace('°', '')
            weather = columns[3].get_text(strip=True)
            wind = columns[4].get_text(strip=True)
            aqi_info = columns[5].get_text(strip=True).split()

            aqi = aqi_info[0]
            if len(aqi_info) > 1:
                quality = aqi_info[1]
            else:
                quality = '无'
            insert(date, weather, max_temp, min_temp, wind, aqi, quality)

        # 点击下一页
        try:
            next_button = qd.find_element(By.ID, 'js_prevMonth')
            next_button.click()
            time.sleep(1)  # 等待页面加载
        except Exception as e:
            print(f"Error clicking next button: {e}")
            break  # 如果点击失败，退出循环

    connect.commit()
finally:
    # 关闭浏览器和数据库连接
    qd.quit()
    cursor.close()
    connect.close()
