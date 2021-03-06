#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

#####################################################
# learn from: mayulin – mayulin@cy2009.com
# Author: suriealli
# Last modified: 2011-04-28 12:27
# Filename: pyssh.py
#####################################################

from fabric.api import *
from os import path
from re import findall
from sys import argv
from fabric.context_managers import hide
from time import sleep
import sys

#default set
USER='root'
HOST,IP_LIST=[],[]
PORT='22'
PRI_KEy,PASSWORD,CMD,uSRC,uDST,dSRC,dDST='','','','','','',''
timeout=1



for i in range(1,len(argv)+1):
    if argv[i-1] == '-h' or len(argv) == 1:
        print '''         USAGE:
        -u [user]       Use this argument to specify the user,default is 'root'
        -H [host]       The host that you want to connect
        -f [file]       The file content multiple ip address you want to connect
        -P [port]       The ssh port,default is 22
        -p [passwd|file]   You can specify password or a priviate key file to connect the host
        -c [command]    The command you want the host(s) to run
        -U [src,dst]    The local file that you want to upload to the remote host(s)
        -D [src,dst]    The remote file that you want to download to the local host
        -t [timeout]    The program running timeout,default is 1(s)
        -h              Print this help screen'''

    if argv[i-1] == '-u':
        USER = argv[i]
        env.user = '%s' %(USER)
    else:
        env.user = '%s' %(USER)
    
    if argv[i-1] == '-H':
        arg = findall('(\d+\.\d+\.\d+\.\d+|\s+\.{3,4})',argv[i])#\s+\.{3,4}尚未理解
        for j in arg:
            if type(j).__name__ != 'NoneType':
                HOST.append(j)
            else:
                print 'The Host IP input ERROR!!'
                sys.exit()
    if argv[i-1] == '-P':
        PORT = argv[i]
    if argv[i-1] == '-f':
        if path.isfile('%s'%(argv[i])) == True:
            IP_LIST = open('%s'%(argv[i]),'r').readlines()
    if argv[i-1] == '-p':
        if path.isfile(argv[i]) == True:
            PRI_KEY = argv[i]
            env.key_filename = '%s' %(PRI_KEY)
        else:
            PASSWORD = argv[i]
            env.password = '%s'%(PASSWORD)
    if argv[i-1] == '-c':
        CMD=argv[i]
    if argv[i-1] == '-t':
        if argv[i].isdigit() == False:
            print 'sleep time ERROR!'
            sys.exit()
        timeout = argc[i]
    SLP = 'sleep %s'%(timeout)
    if argv[i-1] == '-U':
        x=src=argv[i].split(',')
        uSRC=x[0]
        uDST=x[1]
    if argv[i-1] == '-D':
        y=src=argv[i].split(',')
        dSRC=y[0]
        dDST=y[1]
else:
    IP_PORT=[]
    if len(IP_LIST) != 0:
        for k in IP_LIST:
            IP_PORT.append(k.strip()+':'+PORT)
    if len(HOST) != 0:
        for k in HOST:
            IP_PORT.append(k.strip()+':'+PORT)
if CMD != '':
    @parallel
    def command():
        with settings(hide('warnings','running','stderr','stdout'),warn_only=True):
#        with hide('running'):
            out=sudo('%s;%s' %(CMD,SLP))
            return out
    for ip in IP_PORT:
        env.host_string = ip
        print "============================================================"
        print "Execute command: \"%s\" at Host:%s" %(CMD,ip.split(':')[0]) 
        stdout=command()
        print stdout
        print "============================================================"
if uSRC and uDST != '':
    @parallel
    def upload():
#        with settings(warn_only=True):
        with hide('running'):
            put('%s' %(uSRC),'%s'%(uDST))
    for ip in IP_PORT:
        env.host_string = ip
        print "============================================================"
        print "Upload local file: \"%s\" to Host: %s\"%s\""%(uSRC,ip.split(':')[0],uDST)
        upload()
        print "============================================================"

if dSRC and dDST != '':
    @parallel
    def download():
        with hide('running'):
            get('%s' %(dSRC),'%s' %(dDST))
    for ip in IP_PORT:
        env.host_string=ip
        print "============================================================"
        print "Download remote file: \"%s\" from Host: %s\"%s\""%(dSRC,ip.split(':')[0],dDST)
        download()
        print "============================================================"


