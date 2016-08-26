#!/usr/bin/env python
# -*- coding:utf8 -*-
#create server_conf
import re,os,datetime,MySQLdb,sys
import global_config

#参数检查
if len(sys.argv) == 1:
    print "%s plat  生成改平台配置" %sys.argv[0]
    sys.exit()

mysql_conn = global_config.mysql_conn_list[sys.argv[1]]
db_name = global_config.db_name_list[sys.argv[1]]

script_dir = os.path.dirname(os.path.realpath(__file__))

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



def create_srv_conf(host,user,passwd,db_name,port):
    try:
        conn = MySQLdb.connect(host,user,passwd,db_name,port)
        print "数据库连接成功。"
    except Exception,e:
        sys.exit("数据库连接失败:%s" %e)
    #读取每个区服的信息，并保存
    sql = "select zone_id,zone_name,computer_name,(select public_ip from computer where computer.computer_name = zone.computer_name) public_ip,(select computer_ip from computer where computer.computer_name = zone.computer_name) intranet_ip,gateway_port,world_id,role_name_prefix,merge_zone_ids,zone_mysql_name,(select mysql_ip from mysql where mysql.mysql_name = zone.zone_mysql_name) log_mysql_ip,(select mysql_user from mysql where mysql.mysql_name = zone.zone_mysql_name) zone_mysql_user,(select mysql_pwd from mysql where mysql.mysql_name = zone.zone_mysql_name) zone_mysql_pwd,(select mysql_port from mysql where mysql.mysql_name = zone.zone_mysql_name) zone_mysql_port,log_mysql_name,(select mysql_ip from mysql where mysql.mysql_name = zone.log_mysql_name) log_mysql_ip,(select mysql_user from mysql where mysql.mysql_name = zone.log_mysql_name) log_mysql_user,(select mysql_pwd from mysql where mysql.mysql_name = zone.log_mysql_name) log_mysql_pwd,(select mysql_port from mysql where mysql.mysql_name = zone.log_mysql_name) log_mysql_port from zone;"
    sql1 = "select computer_name,public_ip,computer_ip from computer;"
    cursor = conn.cursor()
    cursor.execute("set names utf8;")
    cursor.execute(sql)
    data = cursor.fetchall()
    #配置文件目录
    if not os.path.exists(script_dir + '/conf'):
        os.mkdir(script_dir + '/conf')

    for i in range(0,len(data)):
        #逐行数据处理，保存为配置文件
        config_file_name='%s/conf/%s_%s.conf' %(script_dir,sys.argv[1],data[i][0])
        file = open(config_file_name,'w')
        conf_info = '''#区ID
Server_id=%s
#区名
Server_name=\'%s\'
#所在服务器
Server_site=%s
#所在服务器公网IP
public_ip=%s
#内网ip
intranet_ip=%s
#Logic端口
Logic_port=%s
#世界ID
world_id=%s
#名称前缀
role_name_prefix=%s
#被合服的区
merge_zids=%s
####数据数据库连接信息####
data_mysql_db=%s
data_mysql_ip=%s
data_mysql_user=%s
data_mysql_passwd=%s
data_mysql_port=%s
####日志数据库连接信息####
log_mysql_db=%s
log_mysql_ip=%s
log_mysql_user=%s
log_mysql_passwd=%s
log_mysql_port=%s'''  %(data[i][0],data[i][1],data[i][2],data[i][3],data[i][4],data[i][5],data[i][6],data[i][7],data[i][8],data[i][9],data[i][10],data[i][11],data[i][12],data[i][13],data[i][14],data[i][15],data[i][16],data[i][17],data[i][18])
        file.write(conf_info)
        file.close()

    #读取服务器信息,computer
    cursor.execute(sql1)
    data = cursor.fetchall()
    for i in range(0,len(data)):
        config_file_name='%s/conf/%s_%s.conf' %(script_dir,sys.argv[1],data[i][0])
        file = open(config_file_name,'w')
        conf_info = '''#名称
name=%s
#公网ip
public_ip=%s
#内网ip
intranet_ip=%s''' %(data[i][0],data[i][1],data[i][2])
        file.write(conf_info)
        file.close()
    cursor.close()
    conn.close()



create_srv_conf(host,user,passwd,db_name,port)
