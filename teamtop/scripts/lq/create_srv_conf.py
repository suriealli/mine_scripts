#!/usr/bin/env python
# -*- coding:utf8 -*-
#create server_conf
import re,os,datetime,MySQLdb,sys
import global_config
#参数检查
if len(sys.argv) == 1:
    print "%s plat  生成改平台配置" %sys.argv[0]
    sys.exit()

mysql_conn=global_config.mysql_conn_list[sys.argv[1]]
db_name=global_config.db_name_list[sys.argv[1]]

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
    # except Exception,e:
    except MySQLdb.Error,e:
        sys.exit("数据库连接失败:%s" %e)
    #读取每个区服的信息，并保存
    if len(sys.argv) >= 3 and sys.argv[2] == "tmp":
        sql = "select zid id,name,(select computer_name from process_tmp where zone_tmp.ghl_process_key = process_tmp.pkey) server_name,ghl_process_key GHL_name,d_process_key D_name,(select port from process_tmp where process_tmp.pkey=zone_tmp.ghl_process_key) GHL_port,(select port from process_tmp where process_tmp.pkey=zone_tmp.d_process_key) D_port,(select public_ip from computer_tmp,process_tmp where zone_tmp.d_process_key = process_tmp.pkey and process_tmp.computer_name = computer_tmp.name) public_ip,(select ip from computer_tmp,process_tmp where zone_tmp.d_process_key = process_tmp.pkey and process_tmp.computer_name = computer_tmp.name) intranet_ip,merge_zids,mysql_name,(select master_ip from mysql_tmp where name = zone_tmp.mysql_name) mysql_ip,(select master_user from mysql_tmp where name = zone_tmp.mysql_name) mysql_user,(select master_pwd from mysql_tmp where name = zone_tmp.mysql_name) mysql_pwd, (select master_port from mysql_tmp where name = zone_tmp.mysql_name) mysql_port from zone_tmp;" 
        sql1 = "select public_ip,ip,name from computer_tmp;"
    else:
        sql = "select zid id,name,(select computer_name from process where zone.ghl_process_key = process.pkey) server_name,ghl_process_key GHL_name,d_process_key D_name,(select port from process where process.pkey=zone.ghl_process_key) GHL_port,(select port from process where process.pkey=zone.d_process_key) D_port,(select public_ip from computer,process where zone.d_process_key = process.pkey and process.computer_name = computer.name) public_ip,(select ip from computer,process where zone.d_process_key = process.pkey and process.computer_name = computer.name) intranet_ip,merge_zids,mysql_name,(select master_ip from mysql where name = zone.mysql_name) mysql_ip,(select master_user from mysql where name = zone.mysql_name) mysql_user,(select master_pwd from mysql where name = zone.mysql_name) mysql_pwd, (select master_port from mysql where name = zone.mysql_name) mysql_port from zone;"
        sql1 = "select public_ip,ip,name from computer;"
    cursor = conn.cursor()
    cursor.execute("set names utf8")
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
#GHL进程
GHL_name=%s
#D进程
D_name=%s
#GHL端口
GHL_port=%s
#D端口
D_port=%s
#所在服务器公网IP
public_ip=%s
#内网ip
intranet_ip=%s
#被合服的区
merge_zids=%s
####数据库连接信息####
mysql_db=%s
mysql_ip=%s
mysql_user=%s
mysql_passwd=%s
mysql_port=%s'''  %(data[i][0],data[i][1],data[i][2],data[i][3],data[i][4],data[i][5],data[i][6],data[i][7],data[i][8],data[i][9],data[i][10],data[i][11],data[i][12],data[i][13],data[i][14])
        file.write(conf_info)
        file.close()

    #读取服务器信息,computer
    cursor.execute(sql1)
    data = cursor.fetchall()
    for i in range(0,len(data)):
        config_file_name='%s/conf/%s_%s.conf' %(script_dir,sys.argv[1],data[i][2])
        file = open(config_file_name,'w')
        conf_info = '''#名称
name=%s
#公网ip
public_ip=%s
#内网ip
intranet_ip=%s''' %(data[i][2],data[i][0],data[i][1])
        file.write(conf_info)
        file.close()
    cursor.close()
    conn.close()

create_srv_conf(host,user,passwd,db_name,port)
