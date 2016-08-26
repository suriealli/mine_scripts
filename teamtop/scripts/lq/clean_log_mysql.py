#!/usr/bin/python
#coding:utf8
#clean up mysql:role_sys_log_id before date
#for lq
#author:suriealli/Joklin


from configobj import ConfigObj
import os,sys,argparse,tarfile,re,shutil
import MySQLdb

def get_opts():
    parse = argparse.ArgumentParser()
    help = "Use this argument to specify the plat./这个参数用来指定平台名。"
    parse.add_argument("-p","--plat", help = help)

    help = "Use this argument to define the mysql_name./这个参数来指定mysql实例。"
    parse.add_argument("-d","--db",help = help)
    args = parse.parse_args()
    return args

#压缩文件(夹)
def tar(fname,type = 'f'):
    t = tarfile.open(fname + ".tar.gz", "w:gz")
    if type == 'f':
        t.add(fname)
    elif type == 'd':
        for root, dir, files in os.walk(fname):
            for file in files:
                fullpath = os.path.join(root, file)
                t.add(fullpath)
    t.close()


def dump_database(db_name,table):
    #此处验证数据库连接
    os.chdir(script_dir)
    bak_file = "./mysql_bak/%s/%s.sql" %(db_name,table)
    if not os.path.exists(os.path.dirname(os.path.realpath(bak_file))):
        os.makedirs(os.path.dirname(os.path.realpath(bak_file)))
    if check_file_exist("./mysql_bak/%s/%s.sql.tar.gz" %(db_name,table)):
        print "数据库%s表%s备份文件已存在:"%(db_name,table)
        os.system("ls -lh ./mysql_bak/%s/%s.sql.tar.gz" %(db_name,table))
        return
    dumpcommand = "mysqldump -h%s -P%s -u%s -p%s %s %s > %s --default-character-set=utf8 2>/dev/null" %(host,port,user,pwd,db_name,table,bak_file)
    os.system(dumpcommand)
    if not os.path.exists(bak_file) or os.path.getsize(bak_file) == 0:
        sys.exit("备份%s.%s失败!!!!!请检查" %(db_name,table))
    os.chdir(os.path.dirname(os.path.realpath(bak_file)))
    tar(table + ".sql")
    os.chdir(script_dir)
    os.remove(bak_file)

def check_file_exist(bak_file):
    os.chdir(script_dir)
    if os.path.exists(bak_file) and os.path.getsize(bak_file) != 0: 
        return True
    else:
        return False

#获取配置文件中所有等于db_name的
def link_and_id_in_mysql(conf_dir,db_name):
    server_id_list = []
    mysql_conn={}
    os.chdir(conf_dir)
    for root,dir,files in os.walk(conf_dir):
        for file in files:
            conf = ConfigObj(file)
            try:
                if conf['mysql_db'] == db_name:
                    server_id_list.append(re.search('\d+',file,re.S).group(0))
            except Exception,e:
                continue
    mysql_conf = ConfigObj('%s_%s.conf' %(plat,server_id_list[1]))
    mysql_conn['host'] = mysql_conf['mysql_ip']
    mysql_conn['user'] = mysql_conf['mysql_user']
    mysql_conn['pwd'] = mysql_conf['mysql_passwd']
    mysql_conn['port'] = mysql_conf['mysql_port']
    server_id_list.sort()
    return mysql_conn,server_id_list

def make_clean_table_list(server_id_list):
    serverid_table_list = {}
    print '尝试链接数据库...',
    try:
        conn = MySQLdb.connect(host,user,pwd,'mysql',port)
        print '成功'
        conn.close()
    except Exception,e:
        print "失败！！\n错误信息:%s" %e
        sys.exit()
    for id in server_id_list:
        db_name = "role_sys_log_%s" %id
        conn = MySQLdb.connect(host,user,pwd,db_name,port)
        cursor = conn.cursor()
        cursor.execute('show tables;')
        tables = cursor.fetchall()
        serverid_table_list[id]=[]
        for table in tables:
            if '2014' in str(table) or '2015' in str(table): serverid_table_list[id].append(table)
    os.chdir(script_dir)
    return serverid_table_list

def show_tables(server_id_list):
    table_list = {}
    print '尝试链接数据库...',
    try:
        conn = MySQLdb.connect(host,user,pwd,'mysql',port)
        print '成功'
        conn.close()
    except Exception,e:
        print "失败！！\n错误信息:%s" %e
        sys.exit()
    for id in server_id_list:
        db_name = "role_sys_log_%s" %id
        conn = MySQLdb.connect(host,user,pwd,db_name,port)
        cursor = conn.cursor()
        cursor.execute('show tables;')
        tables = cursor.fetchall()
        table_list[id]=[]
        for table in tables:
            table_list[id].append(table)
    return table_list


def bak_mysql_data(serverid_table_list):
    for id in serverid_table_list:
        if serverid_table_list[id] == []:continue
        for tables in serverid_table_list[id]:
            db_name = "role_sys_log_%s" %id
            for table in tables:
                try:
                    print "备份数据库%s表%s..."%(db_name,table),
                    dump_database(db_name,table)
                except Exception,e:
                    sys.exit("数据库%s表%s备份失败，请检查:%s" %(db_name,table,e))
                print '完成。'

def drop_tables(serverid_table_list):
    os.chdir(script_dir)
    for id in serverid_table_list:
        if serverid_table_list[id] == []:continue
        db_name = "role_sys_log_%s" %id
        for tables in serverid_table_list[id]:
            for table in tables:
                bak_file = "./mysql_bak/%s/%s.sql.tar.gz" %(db_name,table)
                if not check_file_exist(bak_file):
                    sys.exit("备份文件不存在或大小为0，表不可删除，请检查！！！！！")
                # os.system("ls -lh ./mysql_bak/%s/%s.sql.tar.gz" %(db_name,table))
                try:
                    conn = MySQLdb.connect(host,user,pwd,db_name,port)
                    cursor = conn.cursor()
                    print "database %s drop table %s" %(db_name,table)
                    cursor.execute("drop table %s;" %table)
                    conn.commit()
                    cursor.close()
                    conn.close()
                except Exception,e:
                    sys.exit("数据库%s表%s 删除失败：%s" %(db_name,table,e))
    print "数据表删除完成。"




#########################################################
################### Start    ############################
script_dir = os.path.dirname(os.path.realpath(__file__))
os.chdir(script_dir)
conf_dir = script_dir + '/conf'
db_list = []
opts = get_opts()
plat = opts.plat
DB = opts.db

#产生Serverid列表和mysql连接
mysql_conn,server_id_list = link_and_id_in_mysql(conf_dir,DB)
host = mysql_conn['host']
user = mysql_conn['user']
pwd = mysql_conn['pwd']
port = int(mysql_conn['port'])

#产生一个字典，键为服id，值为需要备份和删除的表
serverid_table_list = make_clean_table_list(server_id_list)


#备份数据库
# bak_mysql_data(serverid_table_list)

os.chdir(script_dir)
#保存删除表前的数据库表情况

str1 = ""
bf =  open("%s_bf.txt" %DB,"w")
table_list=show_tables(server_id_list)
for i in table_list:
    str1 = str1 + "%s : %s \n"%(i,table_list[i])
bf.write(str1)
bf.close()

#删除表
drop_tables(serverid_table_list)

#保存数据库删除后的表情况
str1 = ""
af =  open("%s_af.txt" %DB,"w")
table_list=show_tables(server_id_list)
for i in table_list:
    str1 = str1 + "%s : %s \n"%(i,table_list[i])
af.write(str1)
af.close()

#保存被删除的表
str1 = ""
df =  open("%s_df.txt" %DB,"w")
for i in serverid_table_list:
    str1 = str1 + "%s : %s \n"%(i,serverid_table_list[i])
df.write(str1)
df.close()