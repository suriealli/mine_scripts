#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#=========================================================================
# 机器设备
#=========================================================================
from Integration import AutoHTML
from Integration.WebPage.User import Permission
import os
import urllib
from glob import glob

# 根目录
#rootpath = os.path.abspath("./../../File")
rootpath = os.path.abspath("/data/games/GS/File")


class File(object):

	"""文件类"""

	def __init__(self, pathname):
		self.pathname = pathname
		self.basename = os.path.basename(self.pathname)
		self.directory = os.path.dirname(self.pathname)
		self.size = os.path.getsize(self.pathname)

	def getCountOfTraceback(self):
		with open(self.pathname, "r") as f:
			tb_count = f.read().count("Traceback")
		return tb_count

	def getSizeInKB(self):
		return (self.size / 1024)

	def geturl(self):
		return urllib.urlencode({'filepath': self.pathname})


class Directory(object):

	'''目录类'''

	def __init__(self, pathname):
		self.pathname = pathname
		self.basename = os.path.basename(self.pathname)
		self.dirname = os.path.dirname(self.pathname)

	def getBranches(self):
		'''获取目录里的子目录的列表'''
		namelist = glob("%s/*" % self.pathname)
		return [Directory(eachname) for eachname in namelist if os.path.isdir(eachname)]

	def getFiles(self, wildcard="*.log"):
		'''获取目录里的文件的列表'''
		namelist = glob("%s/%s" % (self.pathname, wildcard))
		return [File(eachname) for eachname in namelist if os.path.isfile(eachname)]

	def gethtml_box1(self):
		query = urllib.urlencode({'pathname': self.pathname})
		linkurl = "%s?%s" % (AutoHTML.GetURL(browse), query)
		return '''<td><a href="%s">%s</a></td>''' % (linkurl,
													 self.basename)

	def geturl(self):
		query = urllib.urlencode({'chdir': self.pathname})
		return "?%s" % query


def ShowFile(request):
	'''【数据与工具】--日志文件'''
	data = {}
	data["rootpath"] = rootpath
	# 分支
	if request.method == "GET":
		if "task" not in request.GET:
			# 普通方式进入页面
			data["browse"] = browse(request)
		else:
			task = AutoHTML.AsString(request.GET, "task")
			if task == "browse":
				data["browse"] = browse(request)
			if task == "scan":
				data["scan"] = scan(request)
	elif request.method == "POST":
		task = AutoHTML.AsString(request.POST, "task")
		if task == "delete":
			data["delete"] = delete(request)
			data["browse"] = browse(request)
	return data


def browse(request):
	browse_context = {}
	path = rootpath
	if request.method == "GET":
		if "chdir" in request.GET:
			pathname = os.path.abspath(
				AutoHTML.AsString(request.GET, "chdir"))
			if os.path.isdir(pathname) and pathname.startswith(rootpath):
				path = pathname
	elif request.method == "POST":
		pathname = os.path.abspath(AutoHTML.AsString(request.POST, "chdir"))
		if os.path.isdir(pathname) and pathname.startswith(rootpath):
			path = pathname
	currentdir = Directory(path)
	browse_context['currentdir'] = currentdir
	# 如果不是根目录，则显示"返回上级目录"的链接
	if currentdir.pathname != rootpath:
		pardir = os.path.abspath(
			os.path.join(currentdir.pathname, os.path.pardir))
		query = urllib.urlencode({'chdir': pardir})
		browse_context['query'] = query
	return browse_context


def delete(request):
	delete_context = {}
	filepath = AutoHTML.AsList(request.POST, "filepath")
	successlist = []
	faillist = []
	try:
		for path in filepath:
			path = os.path.abspath(path)
			if os.path.isfile(path) and os.path.split(path)[0].startswith(rootpath):
				os.remove(path)
				successlist.append(path)
			else:
				faillist.append(path)
	except:
		pass
	delete_context["success"] = successlist
	delete_context["fail"] = faillist
	return delete_context


class Artist(object):

	"""艺术家类。文本着色"""

	def __init__(self):
		# color (正则表达式，R，G，B，html元素class名)
		self.colors = [
			(r'''File(?= "(\w|/|\.|_|-)+", line \d+, in )''',
			 0, 154, 217, "\g<0>", "c1"),
			(r"\d+:\d+:\d+(?= Traceback \(most recent call last\))",
			 214, 31, 21, "\n■\g<0>", "time"),
			(r"Traceback (?=\(most recent call last\))",
			 236, 72, 64, "\g<0>", "c2"),
			(r'''(?<=GE_EXC) \d+-\d+-\d+ \d+:\d+:\d+''',
			 0, 0, 0, "\g<0>", "exctime"),
			("GE_EXC", 127, 212, 21, "GE_EXC", "c3"),
			(r'''(\w+Error: ).*''', 0, 0, 155, r"\g<0>", "bb"),
			(r"\w+Error:", 0, 0, 255, "\g<0>", "c4"),
			(r"line(?= \d*,)", 0, 130, 255, "line", "c5"),
			(r"\S+\.\S+\(\)", 0, 0, 0, "\g<0>", "c6")
		]

	def paint(self, text):
		import re
		for color in self.colors:
			alterstr = '<span class="%s">%s</span>' % (color[5], color[4])
			text = re.sub(color[0], alterstr, text)
		return text


def scan(request):
	scan_context = {}
	filepath = os.path.abspath(AutoHTML.AsString(request.GET, "filepath"))
	if os.path.isfile(filepath) and os.path.split(filepath)[0].startswith(rootpath):
		with open(filepath, "r") as f:
			text = f.read()
		Davinci = Artist()
		scan_context["text"] = Davinci.paint(text)
		scan_context["artist"] = Davinci
	return scan_context

def syncClient(request):
	get={}
	get['confirm']=AutoHTML.AsString(request.GET,'confirm')
	data={}
	if get['confirm']:
		f=os.popen('ssh root@10.190.171.181 -p36000 /bin/bash /data/admin/localjob/prsync_WEB.sh')
		data['result'] = f.read().replace("\n",'<br>') #result.replace('\n','')
	return data

def changeClientLocation(request):
	import me
	get={}
	data={}
	get['location']=me.G(request,"location")
	get['confirm']=me.G(request,'confirm')
	if not get['location']:
		get['location']="cdn"
	if get['confirm']:
		if get['location'] not in ['cdn','cvm']:
			return {"tips":"Fuck!"}
		f=os.popen('/data/admin/centre/setrespath/setrespath.sh %s'%(get['location']))
		data['result'] = f.read().replace("\n",'<br>') #result.replace('\n','')
	return data

Permission.reg_develop(ShowFile)
Permission.reg_develop(syncClient)
