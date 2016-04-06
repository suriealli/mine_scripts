#!/usr/bin/python2.7 
#coding:utf-8
import sys
import pycurl
import urllib
import StringIO
if len(sys.argv) <3:
    sys.exit("账号为空或消息为空")
phone_NO = sys.argv[1]
message = sys.argv[2]
#phone_NO = "13660666049"
#message = "Just Test"

url = 'http://222.73.117.158/msg/HttpBatchSendSM?'
phone_list = phone_NO.split(",")
post_data = {}
if phone_list != "":
    for per_NO in phone_list:
        data = "[验证码]:%s" %message
        post_data['account'] = "quxuan"
        post_data['pswd'] =  "NVFA7wACv9QdzX5N"
        post_data['mobile'] = per_NO
        post_data['msg'] = data
        crl = pycurl.Curl()
        crl.setopt(pycurl.VERBOSE,1)
        crl.setopt(pycurl.FOLLOWLOCATION, 1)
        crl.setopt(pycurl.MAXREDIRS, 5)
        
        crl.setopt(pycurl.CONNECTTIMEOUT, 30)
        crl.setopt(pycurl.TIMEOUT, 60)
        crl.setopt(pycurl.HTTPPROXYTUNNEL,1)
        crl.fp = StringIO.StringIO()
        crl.setopt(pycurl.USERAGENT, "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)")
        crl.setopt(crl.POSTFIELDS,urllib.urlencode(post_data))
        crl.setopt(crl.WRITEFUNCTION, crl.fp.write)
        crl.setopt(pycurl.URL, url)
        crl.perform()
