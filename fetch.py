# 请求库
import requests
# 解析html的类jquery库
from pyquery import PyQuery as pq
# 正则模块
import re
# Excel表格操作
import xlwt
# 时间模块记录代码运行时间
from time import time
# mysql连接器
import mysql.connector


def save_mysql():
    return 1


def fetch_douban(page_num):
    url = 'https://movie.douban.com/top250'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36'
    }
    params = {'start': page_num}
    res = requests.get(url=url, params=params, headers=headers)
    if (res.ok):
        return res.text
    else:
        print('爬取失败！')


def resolve_html(htmlStr):
    titles_list = []
    doc = pq(htmlStr)
    items = doc('.grid_view li').items()
    for item in items:
        # 电影名称
        movie_name = item.find('.hd .title:first-child').text()
        # 电影排名
        rank = item.find('.pic em').text()
        # 电影评分
        rate = item.find('.star .rating_num').text()
        # 电影评分人数
        viewer = re.sub('\D', '', item.find('.star span:nth-child(4)').text())
        # 相关名言
        quote = item.find('.quote .inq').text()
        titles_list.append({'豆瓣排名': rank, '电影名称': movie_name, '评分': rate, '评价人数': viewer, '名言': quote})
    return titles_list


def get_allmovies():
    movie_list = []
    for i in range(0, 250, 25):
        htmlStr = fetch_douban(i)
        titles_list = resolve_html(htmlStr)
        movie_list += titles_list
    return movie_list


def sava_excel(move_list, file_name):
    # 1 新建工作簿
    workbook = xlwt.Workbook()
    # 2 新建工作表并重命名
    worksheet = workbook.add_sheet('DouBan_rank')  # 将工作表worksheet命名为‘Python’
    first_line = 0
    # 写入表头
    for num, item in enumerate(move_list[first_line].keys()):
        worksheet.write(first_line, num, item)
    # 一行行写入数据
    for row_num, row_item in enumerate(move_list):
        row_num += 1
        for col_num, col_item in enumerate(row_item.keys()):
            worksheet.write(row_num, col_num, row_item[col_item])
    workbook.save(file_name)


def save_txt(move_list, file_name):
    path = file_name
    file = open(path, 'w+', encoding='utf-8')
    for item in move_list:
        file.write(f'{item["电影名称"]}\n')

def save_mysql(move_list):
    # 存储到mysql
    config = {
        'host': 'localhost',
        'port': '3306',
        'user': 'root',
        'password': 'ljg114671213',
        'database': 'muke'
    }
    mydb = mysql.connector.connect(**config)

    mycursor = mydb.cursor()

    mycursor.execute(
        "CREATE TABLE douban (rank_order SMALLINT PRIMARY KEY, movie_name VARCHAR(20),rate decimal(2,1),viewer MEDIUMINT unsigned,quote VARCHAR(255))")
    tuple_list = []
    for item in move_list:
        item['豆瓣排名'] = int(item['豆瓣排名'])
        item['评分'] = float(item['评分'])
        item['评价人数'] = int(item['评价人数'])
        tuple_list.append(tuple(item.values()))
    sqlInsertStr = 'INSERT INTO douban (rank_order, movie_name,rate,viewer,quote) VALUES (%s, %s,%s, %s,%s)'
    mycursor.executemany(sqlInsertStr, tuple_list)
    mydb.commit()
if __name__ == '__main__':
    # 爬取并解析豆瓣top250 html
    start_time = time()
    total_list = get_allmovies()
    # 存储到excel表格
    sava_excel(total_list, '豆瓣250排名.xls')
    # 存储到txt
    save_txt(total_list, '豆瓣250排名.txt')
    # 存储到mysql数据库
    save_mysql(total_list)
    end_time = time()
    total_time = end_time - start_time
    print(f'爬取时间和存储时间总共是{round(total_time, 2)}秒！！！')
