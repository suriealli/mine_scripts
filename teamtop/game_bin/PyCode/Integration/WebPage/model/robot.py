#!/usr/bin/env python
#-*-coding:utf-8-*-
import os,sys,getopt

def loopNotice():
	import urllib2
	urllib2.urlopen('http://localhost:8008/model/server/loopNotice?key=lostnote')
	
def getLatestData():
	import urllib2
	urllib2.urlopen('http://localhost:8008/model/data/manageAllData?step=get&key=lostnote&auto=13')

def checkLatestData():
	import urllib2
	urllib2.urlopen('http://localhost:8008/model/data/manageAllData?step=get&key=lostnote&suto=31&check=true')
if __name__=="__main__":
	opts,args=getopt.getopt(sys.argv[1:],"a:")#action
	action=''
	for op,value in opts:
		if op=='-a':
			action=value
	if action!='':
		eval(action+'()')
		
