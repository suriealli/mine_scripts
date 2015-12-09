#!/usr/bin/python
#-coding:utf-8--
# -*- encoding: utf-8 -*-

import MySQLdb
import json
import sys
from configobj import ConfigObj

#从数据库中读取数据，并保存
def selectData(dump_file):
    conn = MySQLdb.connect(ip,'root',db_pwd,db_name,4580,)
    cursor = conn.cursor()
    cursor.execute('select data from server_status where status_id = 8')
    data = cursor.fetchone()
    cursor.close()
    str = data[0]
    f=open(dump_file,'w')
    f.write(str)
#    f.write(str.decode('latin1').encode('utf8'))
    f.close()

#插入处理后的数据
def insertData(insert_str):
    conn = MySQLdb.connect(ip,'root',db_pwd,db_name,4580,)
    cursor = conn.cursor()
    cursor.execute('update server_status set data = %s where status_id = 8',insert_str)
    conn.commit()
    cursor.close()
    conn.close()


#读取并处理数据
def processJson(inputJsonFile):
    fin = open(inputJsonFile,'rb')
    line = fin.read().strip().decode('latin1')
    line = line.strip()
    global js
    js = None
    try:
        js = json.loads(line)
    except Exception,e:
        print 'bad line'
    fin.close()
    js['special_rank_data']['special_rank_list'][6] = []
    js['special_rank_data']['special_rank_list'][7] = []
    js['special_rank_data']['special_rank_list'][8] = []
    print js	

#配置文件
conf_file='/g2/centerg2/0/rsync/conf/%s/%s_s%s.conf' %(sys.argv[1],sys.argv[1],sys.argv[2])
#读取配置文件
conf = ConfigObj(conf_file)

ip = conf['DB_M_HOST']
db_pwd = conf['DB_MANAGER_PWD']
db_name = 'g2_%s_%s_game' %(sys.argv[1],sys.argv[2])
dump_file='%s_s%s.json' %(sys.argv[1],sys.argv[2])
#查数据并备份
selectData(dump_file)
#处理数据
processJson(dump_file)
#处理后的json转换为str格式
insert_str = json.dumps(js,separators=(',',':'),ensure_ascii = False) + ','
#插入回数据库
insertData(insert_str.strip().encode('latin1'))
