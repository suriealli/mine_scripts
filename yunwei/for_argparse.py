#!/usr/bin/python2.7
#coding:utf8
from fabric.api import *
from os import path
from re import findall
from sys import argv
from fabric.context_managers import hide
from time import sleep
import sys
import argparse
#default set
USER='root'
HOST,IP_LIST=[],[]
PORT='22'
PRI_KEy,PASSWORD,CMD,uSRC,uDST,dSRC,dDST='','','','','','',''
TIMEOUT=1

def parser_args():
#    Help = """    USAGE:
#    -u [user]       Use this argument to specify the user,default is 'root'
#    -H [host]       The host that you want to connect
##    -f [file]       The file content multiple ip address you want to connect
#    -P [port]       The ssh port,default is 22
#    -p [passwd|file]   You can specify password or a priviate key file to connect the host
#    -c [command]    The command you want the host(s) to run
#    -U [src,dst]    The local file that you want to upload to the remote host(s)
#    -D [src,dst]    The remote file that you want to download to the local host
##    -t [timeout]    The program running timeout,default is 1(s)
#    -h              Print this help screen"""
    parse = argparse.ArgumentParser()
    help = "The user used to connect!"
    parse.add_argument("-u","--user",default = USER)
    parse.add_argument("-p","--port",default = PORT)
    parse.add_argument("-H","--host",default = HOST)
    parse.add_argument("-f","--file",default = "")
    parse.add_argument("-P","--passwd",default = "")
    parse.add_argument("-c","--command",default = "")
    parse.add_argument("-U","--upload",default = "")
    parse.add_argument("-D","--download",default = "")
    parse.add_argument("-t","--timeout",default = TIMEOUT)

    args = parse.parse_args()
    return args

if __name__ == '__main__':
    args = parser_args()
    print args.user
    print args.port
