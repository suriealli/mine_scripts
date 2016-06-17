#!/usr/bin/python
# -*- coding:utf8 -*-
#author:suriealli
#just for sd:四大名捕
from configobj import ConfigObj
import re,os,datetime,MySQLdb

#获取配置
def get_config(config_file):
    global_config = ConfigObj(config_file)
    global_config['db_connect'] = global_config['db_connect'] + " "
    config_info = {}

    config_info['host'] = re.search('-h(.*?)\s',global_config['db_connect'],re.S)
    config_info['host'] = config_info['host'].group(1).replace("-h","")

    config_info['port'] = re.search('-P(.*?)\s',global_config['db_connect'],re.S)
    config_info['port'] = config_info['port'].group(1).replace("-P","")

    config_info['user'] = re.search('-u(.*?)\s',global_config['db_connect'],re.S)
    config_info['user'] = config_info['user'].group(1)
  
    config_info['passwd'] = re.search('-p(.*?)\s',global_config['db_connect'],re.S)
    config_info['passwd'] = config_info['passwd'].group(1)
    
    config_info['db_name'] = global_config['db_name']
    return config_info

#备份数据库
def dump_database(host,port,user,passwd,db_name):
    #此处验证数据库连接
    try:
        conn = MySQLdb.connect(host,user,passwd,db_name,port)
        print "数据库连接成功。"
        conn.close()
    except IOError,e:
        print e
    bak_file = "./mysql_bak%s/%s_%s.sql" %(datetime.datetime.now().strftime("%Y-%m-%d"),db_name,datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
    if not os.path.exists("./mysql_bak" + datetime.datetime.now().strftime("%Y-%m-%d")):
        os.mkdir("./mysql_bak" + datetime.datetime.now().strftime("%Y-%m-%d"))
    print "开始备份数据库...",
    dumpcommand = "mysqldump -h%s -P%s -u%s -p%s %s > %s --default-character-set=utf8" %(host,port,user,passwd,db_name,bak_file)
    os.system(dumpcommand)
    if os.path.exists(bak_file) and os.path.getsize(bak_file) != 0:
        print "备份完成。"
    else:
        sys.exit("备份失败!!!!!请检查")


#读取插入数据
def read_insert_data(insert_file):
    insert_data_list=[]
    with open(insert_file,'rt') as f:
        for line in f:
            if line.startswith('#'):
                continue
            insert_data_list.append(line)
    return insert_data_list

#输出sql语句
def create_sql(insert_data_list):
    per_data_list=[]
    sql=[]
    for i in range(0,len(insert_data_list)):
        per_data_list=insert_data_list[i].split()
        #插入中变量顺序：区ID 数据MySQL 世界ID 机器名 端口 区名 名称前缀 日志MySQL
        str_sql="INSERT INTO zone  VALUES('[]',%s,0,'[]','','%s',%s,'%s',%s,'%s','%s','%s');"  %(per_data_list[0],per_data_list[3],per_data_list[5],per_data_list[2],per_data_list[7],per_data_list[1],per_data_list[6],per_data_list[4])
        sql.append(str_sql)
    return sql

def exec_sql(host,port,user,passwd,db_name,sql_list):
    try:
        conn = MySQLdb.connect(host,user,passwd,db_name,charset='latin1')
        cursor = conn.cursor()
        for i in range(0,len(sql_list)):
            print sql_list[i]
            sql = sql_list[i]
            cursor.execute(sql)
            conn.commit()
        cursor.close()
        conn.close()
    except IOError,e:
        print e
########################################
############start scripts#@#############
########################################
config_file = "./global.conf"
config_info = get_config(config_file)

host = config_info['host']
port = int(config_info['port'])
user = config_info['user']
passwd = config_info['passwd']
db_name = config_info['db_name'] 

insert_data_file = "./format_sd.txt"

#开始执行：

#备份数据库
dump_database(host,port,user,passwd,db_name)
#读取需要插入的数据
insert_data_list=read_insert_data(insert_data_file)
#输出SQL语句
sql_list=create_sql(insert_data_list)
for i in range(0,len(sql_list)):
    print sql_list[i]

#执行SQl
exec_sql(host,port,user,passwd,db_name,sql_list)
