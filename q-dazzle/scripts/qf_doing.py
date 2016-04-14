#!/usr/bin/python2
#coding:utf8
import time
import md5
import socket
from configobj import ConfigObj
def get_plat_sn(file):
    f = open(file,'r')
    line = f.readline()
    global lines
    lines = []
    while line:
        lines.append(line.strip('\n'))
        line = f.readline()
       

def get_plat_sn_ip(plat_sn):
    plat = plat_sn.split("-")[0]
    sn = plat_sn.split("-")[1]
    file = '%s%s/%s_s%s.conf' %(game_info[str(game_id)][1],plat,plat,sn)
    print file





#游戏信息
game_id = '1'
game_info = {'1':['183.61.119.173','/ssqy/center/0/rsync/conf/'],'2':['42.62.86.196','/g2/centerg2/0/rsync/conf/'],'3':['123.59.33.146','/fshx/centerg3/0/rsync/conf/'],'4':['183.61.119.173','/t1/t1center/0/rsync/conf/']}

#获取本机ip地址
def get_local_ip():
    tempSocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    tempSocket.connect(('8.8.8.8',80))
    ip = tempSocket.getsockname()[0]
    tempSocket.close()

#是否为本机上操作,此功能暂不实现
#is_server=''
#if ip != game_info[str(game_id)][0]:
#    is_server=0
#    print "Now is not on the plat's own server!!"
#else:
#    is_server=1
#    print "Now is the plat's on own server!!"






get_plat_sn('./dlplat_sn')
get_plat_sn_ip(lines[1])
