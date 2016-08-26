#!/usr/bin/python
# -*- coding:utf8 -*-
#author:suriealli
#just for sd:龙骑
import re,os,datetime,MySQLdb,argparse,sys,stat,tarfile,shutil
import global_config


def get_opts():
    parse = argparse.ArgumentParser()
    help = "Use this argument to specify the plat./这个参数用来指定平台名。"
    parse.add_argument("-p","--plat", help = help)

    help = "Use this argument to define the action./这个参数设置操作。如add、update、start、backup"
    parse.add_argument("-s","--schedule",help = help)
    args = parse.parse_args()
    return args

#备份数据库
def tar(fname):
    t = tarfile.open(fname + ".tar.gz", "w:gz")
    for root, dir, files in os.walk(fname):
        for file in files:
            fullpath = os.path.join(root, file)
            t.add(fullpath)
    t.close()

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
        if not os.path.exists(bak_file) or os.path.getsize(bak_file) == 0:
            sys.exit("备份%s.%s失败!!!!!请检查" %(db_name,table))
    os.chdir(os.path.dirname(os.path.realpath(bak_file))+"/../")
    tar(db_name + "_" + now_time)
    os.chdir(script_dir)
    shutil.rmtree(os.path.dirname(os.path.realpath(bak_file)))
    print "完成。"
    #删除一天前的备份文件
    # file_list=os.listdir("./mysql_bak/")
    # for file in file_list:
    #     ctime = int(os.stat("./mysql_bak/" + file)[stat.ST_CTIME])
    #     ntime = int(datetime.datetime.now().strftime("%s"))
    #     if ntime - ctime >= 86400:
    #         os.remove("./mysql_bak/" + file)




###################
opts = get_opts()
#要插入的文件
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




#是否为备份
if schedule == "backup":
    dump_database(host,port,user,passwd,db_name)