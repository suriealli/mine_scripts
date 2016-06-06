#!/usr/bin/python
# -*- coding:utf8 -*-
#import argparse
import sys,re,argparse

def create_srv_name_list(start_srv_name,total_num,base_srv_name):
    if base_srv_name == None and start_srv_name != None:
        srv_name_list = []
        start_srv_name_id = re.findall(r"[0-9]{1,100}",start_srv_name)[0]    
        for i in range(int(start_srv_name_id),int(start_srv_name_id) + total_num):
            srv_name = re.sub(r'[0-9]{1,100}',str(i),start_srv_name)
            srv_name_list.append(srv_name)
        return srv_name_list
    elif base_srv_name != None and start_srv_name != None:
        srv_name_list = []
        for i in range(int(start_srv_name),int(start_srv_name) + total_num ):
            srv_name = base_srv_name + str(i)
            srv_name_list.append(srv_name)
        return srv_name_list
    else:
        sys.exit("参数错误。")

def create_id_list(pass_id,start_srv_id,total_num):
    id_list = []
    #结束id值
    end_srv_id = int(start_srv_id) + int(total_num) + len(pass_id)
    #总长度的id列表
    for id in range(int(start_srv_id),end_srv_id):
        id_list.append(id)
    #生成的ID列表
    for p_id in pass_id:
        for l_id in id_list:
            if int(p_id) == int(l_id):
                id_list.remove(int(p_id))
    return id_list

def Parser_args():
    parse = argparse.ArgumentParser()
    help = "Use this argument to specify the start_srv_name./这个参数用来设置初始区名及格式"
    parse.add_argument("-Sn","--start-srv-name",help=help)

    help = "Use this argument to specify the base_name format./这个参数用来设置区名格式，如:160yx,如此选项被设置，start_srv_name请设置为初始id"
    parse.add_argument("-Bn","--base-srv-name",help=help)

    help = "Use this argument to specify the start_srv_id./这个参数用来设置初始ID"
    parse.add_argument("-Si","--start-srv-id",help=help)

    help = "Use this argument to specify the Num you want to set./这个参数用来设置的要部署的去的数量"
    parse.add_argument("-N","--total-num", type = int, help=help)

    help = "Use this argument to specify the file__name./这个参数用来设置要生成的文件名"
    parse.add_argument("-F","--file-name",help=help)

    help = "Use this argument to specify the pass_id_list./这个参数用来设置被跳过的id列表"
    parse.add_argument("-P","--pass-id",default = "[]", nargs = '*',help=help)

    help = "Use this argument to specify the host./这个参数用来设置所在的服务器(全部)"
    parse.add_argument("-H","--host",default = "",help=help)
 
    help = "Use this argument to specify the start_port./这个参数用来设置初始端口，默认8000,且自增1"
    parse.add_argument("-Sp","--start-srv-port",default = 8000,type = int,help=help)

    help = "Use this argument to specify the db./这个参数用来设置db进程(全部)"
    parse.add_argument("-D","--db",help=help)

    help = "Use this argument to specify the control./这个参数用来设置控制进程"
    parse.add_argument("-C","--control",help=help)
    args = parse.parse_args()
    return args


#############################
#########Start Running#######
#############################
args = Parser_args()
if len(sys.argv) < 3:
    sys.exit('argument error')

start_srv_name = args.start_srv_name
base_srv_name = args.base_srv_name
start_srv_id = args.start_srv_id
srv_port = args.start_srv_port
total_num = args.total_num
file_name = args.file_name
host = args.host
pass_id = args.pass_id
db = args.db
control = args.control

#如果不跳过id
if pass_id == "[]":
    pass_id = ["0"]



id_list = create_id_list(pass_id,start_srv_id,total_num)

srv_name_list = create_srv_name_list(start_srv_name,total_num,base_srv_name)
str = ''
#写入到文件中
for i in range(total_num):
    str = str + "%s \t %s \t %s \t %s \t %s \t %s\n" %(srv_name_list[i],id_list[i],host,srv_port,db,control)
#    print "%s \t %s \t %s \t %s \t %s \t %s" %(srv_name_list[i],id_list[i],host,srv_port,db,control)
    srv_port += 1
print str
#f = open(file_name,'w')
#f.write(str)
#f.close()

