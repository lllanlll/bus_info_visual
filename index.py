
# 1. 初始化数据库链接
# 引入全局库
import pymysql
from datetime import datetime

# 工具函数
# a.生成一个包含数字1-9和字母A-Z的list
def generateList():
    res = []
    for i in range(1, 10):
        res.append(i)
    for i in map(chr, range(ord('A'), ord('Z') + 1)):
        res.append(i)
    return res

# b.计时器及提示信息 目的: 提示某一操作开始时间，耗时多久，多久结束
# event: 执行的事件名称
# flag: 开始还是结束 1开始 0 结束
# 全局时间戳记录耗时
timeRange = 0
def timeAndInfo(event, flag):
    global timeRange
    timeStart = datetime.now()
    timeStampStart = timeStart.timestamp()
    if flag == 1:
        timeRange = timeStampStart
        print(f'{event}, 当前时间为: {timeStart}')
    else:
        timeRange = timeStampStart - timeRange
        print(f'{event}, 当前时间为: {timeStart}, 这一步操作耗时: {timeRange}s')

# 全局变量
# 数据库配置
DB_START_CONFIG = {
    'host': 'bdm721269539.my3w.com',
    'port': 3306,
    'user': 'bdm721269539',
    'password': 'Root0516',
    'db': 'bdm721269539_db',
}

# 城市名称
CITY_NAMES = {
    'chengdu': '成都',
    'beijing': '北京',
    'tianjin': '天津',
    'hangzhou': '杭州',
    'shanghai': '上海',
    'wuhan': '武汉',
    'chongqing': '重庆',
    'guangzhou': '广州',
}

# 2.连接至数据库
conn = pymysql.connect(
    host = DB_START_CONFIG['host'],
    port = DB_START_CONFIG['port'],
    user = DB_START_CONFIG['user'],
    password = DB_START_CONFIG['password'],
    db = DB_START_CONFIG['db']
)

# 创建游标来执行sql
cur = conn.cursor()

# 一个测试方法来查询表数据
def searchTableData(table):
    sql = 'select * from ' + table
    cur.execute(sql)
    res = cur.fetchall()
    for row in res:
        print(row)


# 3.创建城市名称表
def createCityTable():
    sql = '''
    CREATE TABLE CITY_NAME_TABLE (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name_pinyin CHAR(20) NOT NULL,
        name_ch CHAR(20) NOT NULL
    )
    '''
    cur.execute(sql)

# 调一次来创建表
# createCityTable()


# 4.将预设的城市名称插入城市名称表中
def insertCityNamesToTable(cityNames):
    for obj in cityNames:
        pinyin = obj
        ch = cityNames[obj]
        # 坑点: 字符串记得加引号
        sql = f'INSERT INTO CITY_NAME_TABLE(name_pinyin, name_ch) values ("{pinyin}", "{ch}")'
        try:
            cur.execute(sql)
            # 提交sql结果
            conn.commit()
        except:
            conn.rollback()


# 运行一次即可
# insertCityNamesToTable(CITY_NAMES)

# 查询表中的数据是否插入成功
# searchTableData('CITY_NAME_TABLE')

# 5.获取所有城市的数据放入citys
def getCitysData():
    sql = 'select * from CITY_NAME_TABLE'
    cur.execute(sql)
    res = cur.fetchall()
    citys = []
    for row in res:
        citys.append(row[1])
    return citys


# 6.爬取单个城市公交线路函数
import requests
from lxml import etree
def getLines(city):
    lst = {}
    lst[city] = []
    lines_range = generateList()
    for i in lines_range:
        url = f"https://{city}.8684.cn/list{i}"
        try:
            r = requests.get(url).text
        except:
            continue
            
        et = etree.HTML(r)
        line = et.xpath('//div[@class="list clearfix"]//a/text()')
        line_info = et.xpath('//div[@class="list clearfix"]//a/@href')
        for name, info in zip(line, line_info):
            obj = {
                'name': name,
                'info': info[3:]
            }
            lst[city].append(obj)
    return lst

# 7.遍历所有城市 爬取所有公交线路 存入各自城市表中
def createCityInfoTable(citys):
    for city in citys:
        sql = f'''   
        CREATE TABLE {city}_info (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name CHAR(20) NOT NULL,
            info_code CHAR(20) NOT NULL
        )
        '''
        cur.execute(sql)

# 新建各城市对应表来存储线路信息
# createCityInfoTable(CITY_NAMES)

# 将数据插入表
def insertBusInfoToCityTable(table, name, code):
    sql = f'INSERT INTO {table}_info (name, info_code) values ("{name}", "{code}")'
    try:
        cur.execute(sql)
        # 提交sql结果
        conn.commit()
    except:
        conn.rollback()

# 遍历8个城市 依次插入所有数据
def getAllLines(citys):
    lst = {}
    print('开始插入数据...')
    for city in citys:
        timeAndInfo(f'开始爬取{city}的线路...', 1)
        lst = getLines(city)
        timeAndInfo(f'结束爬取', 0)
        timeAndInfo(f'开始将线路插入{city}_info表中...', 1)
        for item in lst[city]:
            insertBusInfoToCityTable(city, item['name'], item['info'])
        timeAndInfo(f'结束{city}_info表的插入', 0)

# 插入所有线路
getAllLines(CITY_NAMES)


cur.close()


