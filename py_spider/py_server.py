import config
import pymysql
from flask import Flask, current_app, redirect, url_for, request
import json
from flask_cors import CORS
import pymysql.cursors

# 1.数据库配置
DB_START_CONFIG = config.getDbConfig()

# 2.连接至数据库
conn = pymysql.connect(
    host = DB_START_CONFIG['host'],
    port = DB_START_CONFIG['port'],
    user = DB_START_CONFIG['user'],
    password = DB_START_CONFIG['password'],
    db = DB_START_CONFIG['db']
)

# 转换数据中的t_name没有斜杠的unicode 为中文
def transChinese(data):
    for item in data:
        t_name = item['t_name']
        item['t_name'] = t_name.replace('u', r'\u').encode('utf-8').decode('unicode_escape')
        
    return data

# 查询详细信息
def getDetailInfo(city = '', name = ''):
    sql = ''
    if (name != ''):
        sql = f"select * from {city}_info where name = '{name}'"
    else:
        sql = f"select * from {city}_info"
    while True:
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql)
            break
        except Exception:
            conn.ping(True)
    # cur.execute(sql)
    res = cursor.fetchall()
    result = []
    for row in res:
        info_one = json.loads(row[3])
        info_two = json.loads(row[4])
        obj = {
            'name': row[1],
            'kind_one': transChinese(info_one),
            'kind_two': transChinese(info_two)
        }
        result.append(obj)
    return result

def getAllLinesNames(city):
    sql = f'select name from {city}_info'
    while True:
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql)
            break
        except Exception:
            conn.ping(True)
    res = cursor.fetchall()
    result = []
    for row in res:
        result.append(row[0])
    return result
# 实例化app
app = Flask(import_name=__name__)

# 通过methods设置GET请求
CORS(app)
@app.route('/line', methods=["GET"])
def line_request():

    # 接收处理GET数据请求
    city = request.args.get('city')
    name = request.args.get('name')
    data = getDetailInfo(city, name)

    return json.dumps(data)

CORS(app)
@app.route('/linenames', methods=["GET"])
def names_request():
    city = request.args.get('city')
    data = getAllLinesNames(city)
    return json.dumps(data)


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=6240, debug=True)



# cur.close()