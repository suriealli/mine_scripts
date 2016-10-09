#!/usr/bin/python
# -*- coding:utf8 -*-
#author:suriealli
#just for sd:四大名捕
import re,os,datetime,MySQLdb,argparse,sys,stat,tarfile,shutil
import global_config


def get_opts():
    parse = argparse.ArgumentParser()
    help = "Use this argument to specify the plat./这个参数用来指定平台名。"
    parse.add_argument("-p","--plat", help = help)

    default = "%s.txt" %(datetime.datetime.now().strftime("%b%d"))
    help = "Use this argument to specify the data_file,default file is %s./这个选项用来指定要增加的区列表，默认为‘./%s’" %(default,default)
    parse.add_argument("-f","--data-file",default = default,help = help)
    
    help = "Use this argument to syncdb in fact./这个参数如被设置，则直接插入数据库。执行前建议先检查"
    parse.add_argument("--syncdb",action='store_true',help = help)

    help = "Use this argument to define the action./这个参数设置操作。如add、update、start、backup"
    parse.add_argument("-s","--schedule",help = help)
    args = parse.parse_args()
    return args

#备份数据库
def tar(fname):
    try:
        t = tarfile.open(fname + ".tar.gz", "w:gz")
        for root, dir, files in os.walk(fname):
            for file in files:
                fullpath = os.path.join(root, file)
                t.add(fullpath)
        t.close()
    except Exception,e:
        sys.exit("文件打包出错，请检查。")

def dump_database(host,port,user,passwd,db_name):
    print "开始备份数据库...",
    #此处验证数据库连接
    try:
        conn = MySQLdb.connect(host,user,passwd,db_name,port)
    except Exception,e:
        print "失败！！\n错误信息:%s" %e
        sys.exit()
    cursor = conn.cursor()
    cursor.execute('show tables;')
    table_list = cursor.fetchall()
    cursor.close()
    conn.close()
    Ttime = datetime.datetime.now().strftime("%Y-%m-%d")
    now_time = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    for table in table_list:
        table=table[0]
        bak_file = "./mysql_bak/%s/%s_%s/%s.sql" %(Ttime,db_name,now_time,table)
        if not os.path.exists(os.path.dirname(os.path.realpath(bak_file))):
            os.makedirs(os.path.dirname(os.path.realpath(bak_file)))
        dumpcommand = "mysqldump -h%s -P%s -u%s -p%s %s %s > %s --default-character-set=utf8 2>/dev/null" %(host,port,user,passwd,db_name,table,bak_file)
        os.system(dumpcommand)
        if not os.path.exists(bak_file) and os.path.getsize(bak_file) == 0:
            sys.exit("备份%s.%s失败!!!!!请检查" %(db_name,table))
    os.chdir(os.path.dirname(os.path.realpath(bak_file))+"/../")
    tar(db_name + "_" + now_time)
    os.chdir(script_dir)
    shutil.rmtree(os.path.dirname(os.path.realpath(bak_file)))
    print "完成。"

#读取插入数据
def read_data(data_file):
    data_list=[]
    with open(data_file,'rt') as f:
        for line in f:
            if line.startswith('#'):
                continue
            data_list.append(line)
    return data_list

#输出sql语句
def create_add_sql(data_list):
    per_data_list=[]
    sql=[]
    for i in range(0,len(data_list)):
        per_data_list=data_list[i].split()
        #插入中变量顺序：区ID 数据MySQL 世界ID 机器名 端口 区名 名称前缀 日志MySQL
        str_sql="INSERT INTO zone  VALUES('[]',%s,0,'[]','',%s,%s,%s,%s,%s,%s,%s);"  %(per_data_list[0],per_data_list[3],per_data_list[5],per_data_list[2],per_data_list[7],per_data_list[1],per_data_list[6],per_data_list[4])
        sql.append(str_sql)
    return sql

#检查zone_id是否已存在
def has_zone_id(cur, zone_id):
    cur.execute("select count(*) from zone where zone_id = %s;" % zone_id)
    result = cur.fetchall()
    return result[0][0]

#检查端口是否已经被占用
def has_computer_port(cur, computer_name, port):
    if port > 10000:
        return False
    cur.execute("select world_id from world where computer_name = %s and process_port = %s;", (computer_name, port))
    if cur.fetchall():
        return True
    cur.execute("select zone_id from zone where computer_name = %s and gateway_port = %s and merged_zone_id = 0;", (computer_name, port))
    if cur.fetchall():
        return True
    return False

#获取公网ip
def get_public_ip(cur, computer_name):
    cur.execute("select count(*) from computer where computer_name = '%s';" % computer_name)
    result = cur.fetchall()
    return result[0][0]

    
ADD_ZONE_sql = "INSERT INTO zone  VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"

#增加区
def add_zone(host,port,user,passwd,db_name,data_list):
    try:
        conn = MySQLdb.connect(host,user,passwd,db_name,charset='utf8')
    except Exception,e:
        print "连接错误信息：%s" %e
        sys.exit()
    print "开始执行SQL...",
    cursor=conn.cursor()
    cursor.execute("set names utf8;")
    for data in data_list:
        data = data.split()
        if has_zone_id(cursor, int(data[0])):
            sys.exit("重复的区ID:" + data[0])
        if has_computer_port(cursor, data[2], data[7]):
            sys.exit("重复的端口:" + data[2] + ":" + data[7])
        if not get_public_ip(cursor, data[2]):
            sys.exit("无此game服务器:" + data[2])
        cursor.execute(ADD_ZONE_sql,('[]',data[0],0,'[]','',data[3],data[5],data[2],data[7],data[1],data[6],data[4]))
    conn.commit()
    cursor.close()
    conn.close()
    print "完成。"



########################################
############start scripts#@#############
########################################
#开始执行：
#获取参数
opts = get_opts()
#要插入的文件
data_file = opts.data_file
schedule = opts.schedule

mysql_conn = global_config.mysql_conn_list[opts.plat]
db_name = global_config.db_name_list[opts.plat]

script_dir = os.path.dirname(os.path.realpath(__file__))
os.chdir(script_dir)
#切割数据库配置

mysql_conn = mysql_conn + " "
host = re.search('-h(.*?)\s',mysql_conn,re.S)
host = host.group(1).replace("-h","")
port = re.search('-P(.*?)\s',mysql_conn,re.S)
port = int(port.group(1).replace("-P",""))
user = re.search('-u(.*?)\s',mysql_conn,re.S)
user = user.group(1)
passwd = re.search('-p(.*?)\s',mysql_conn,re.S)
passwd = passwd.group(1)



if __name__ == "__main__":
    #是否为备份
    if schedule == "backup":
        dump_database(host,port,user,passwd,db_name)
    #输出SQL语句
    elif opts.syncdb == False and schedule == 'add':
        data_list=read_data(data_file)
        sql_list=create_add_sql(data_list)
        for i in range(0,len(sql_list)):
            print sql_list[i]
    elif opts.syncdb == True and schedule == 'add':
        #备份数据库
        data_list=read_data(data_file)
    
        sql_list=create_add_sql(data_list)
        #执行SQL
        sel = raw_input("确定要同步到数据库？(yes/no)")
        if sel == "yes":
            dump_database(host,port,user,passwd,db_name)
            add_zone(host,port,user,passwd,db_name,data_list)
    