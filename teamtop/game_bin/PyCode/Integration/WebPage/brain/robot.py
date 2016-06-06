#!/usr/bin/env python
#-*-coding:utf-8-*-
import os,sys,getopt,traceback

def reportAudit(msg):
	import requests
	import time,tool
	try:
		r=requests.get("http://ly.app100718848.twsapp.com:8008/audit/get?game=%s&operator=1&model=all&target=ftp&date_start=%s&date_end=%s&key=follow-my-own-soul"%(msg,tool.date(time.time()-86400),tool.date(time.time()-86400)))
	except:
		traceback.print_exc()
def uploadAudit(msg):
	import requests
	import time,tool
	try:
		r=requests.get("http://ly.app100718848.twsapp.com:8008/audit/get?game=%s&operator=1&model=all&target=ftp&date_start=%s&date_end=%s&key=follow-my-own-soul&step=upload"%(msg,tool.date(time.time()-86400),tool.date(time.time()-86400)))
	except:
		traceback.print_exc()
def loopNotice(msg):
	import requests
	r=requests.get('http://%s/notice/loop'%msg)
	
if __name__=="__main__":
	try:
		opts,args=getopt.getopt(sys.argv[1:],"a:e:")#action
		action=''
		game=""
		for op,value in opts:
			if op=='-a':
				action=value
			if op=='-e':
				game=value
		if action!='':
			eval(action+'("%s")'%game)
	except:
		traceback.print_exc()
		pass
