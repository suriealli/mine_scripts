#!/usr/bin/python2.7
#coding:utf8
from fabric.api import *
from os import path
from re import findall 
from sys import argv
from fabric.context_managers import hide
import sys,argparse,datetime
#default set
USER='root'
HOST,IP_LIST=[],[]
PORT='22'
PRI_KEy,PASSWORD,CMD,uSRC,uDST,dSRC,dDST='','','','','','',''
TIMEOUT=0

def parser_args():
    parse = argparse.ArgumentParser()
    help = "Use this argument to specify the user,default is 'root'"
    parse.add_argument("-l","--user",default = USER,help=help)

    help = "The ssh port,default is 22"
    parse.add_argument("-P","--port",default = PORT,help=help)

    help = "The host that you want to connect"
    parse.add_argument("-H","--host",nargs='*',default = HOST,help=help)

    help = "The file content multiple ip address you want to connect"
    parse.add_argument("-f","--file",default = "",help=help)

    help = "You can specify password to connect the host"
    parse.add_argument("-p","--passwd",default = "",help=help)

    help = "You can specify a priviate key file to connect the host"
    parse.add_argument("-i","--key",help=help)

    help = "The local file that you want to upload to the remote host(s):localdir remotedir"
    parse.add_argument("-U","--upload",default = "",help=help)

    help = "The remote file that you want to download to the local host:remotedir localdir" 
    parse.add_argument("-D","--download",default = "",help=help)

    help = "The program running timeout,default is 1(s)"
    parse.add_argument("-t","--timeout",default = TIMEOUT,help=help)

    help = "The command you want the host(s) to run"
    parse.add_argument("-c","--command",default = "",help=help)

    args = parse.parse_args()
    return args

if __name__ == '__main__':
    args = parser_args()
    env.user = args.user
    if args.host != []:
        IP_LIST = args.host
    if type(args.file).__name__ != "NoneType" and path.isfile('%s'%(args.file)) == True: 
        for line in open('%s'%(args.file),'r').readlines():
            IP_LIST.append(line.strip("\n"))
    if type(args.key).__name__  != "NoneType" and path.isfile(args.key) == True:
        env.key_filename = '%s' %(args.key)
    else:
        env.password =  '%s' %(args.passwd)
    IP_PORT=[]
    if len(IP_LIST) != 0:
        for i in IP_LIST:
            IP_PORT.append(i.strip()+":"+args.port)
    if args.command != '':
        @parallel
        def command():
             with settings(hide('warnings','running','stderr','stdout'),warn_only = True):
                out = sudo('%s;sleep %s' %(args.command,args.timeout))
                return out
        f = open('our_server.log','a')
        for ip in IP_PORT:
            env.host_string = ip
            start_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print "====================%s==============================" %(start_time)
            print "Execute command: \"%s\" at Host:%s" %(args.command,ip.split(':')[0])
            stdout=command()
            print stdout 
            end_time = datetime.datetime.now()
            time = "%s" %((end_time - datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')))
            print "=========执行时间：%s=========================" %(time.split(".")[0])











