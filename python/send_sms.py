#!/usr/bin/python2.7 
#coding:utf-8
import sys
import pycurl
import urllib
 
phone_NO = sys.argv[1]
message = sys.argv[2]
if phone_NO == "" or message == "":
    sys.exit("账号为空或消息为空")

phone_list = phone_NO.split(",")

if phone_list != "":
    for i in phone_list:
        print i

