#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 服务器警告
#===============================================================================
import os
import sys

reload(sys)
getattr(sys, "setdefaultencoding")("UTF-8")
path = os.path.dirname(os.path.realpath(__file__))
path = path[:path.find("PyCode") + 6]
if path not in sys.path: sys.path.append(path)
path = path.replace("PyCode", "PyHelp")
if path not in sys.path: sys.path.append(path)

import glob
import time
import struct
import urllib
import urllib2
import datetime
import platform
import traceback
import DynamicPath


#各个版本的配置(name, (addwarnIp, port),(getwarnIp, port))
EnvDict = {"qq":("【腾讯】警告", ("10.207.149.29", 8008), ("banben1.app100718848.twsapp.com", 8008)),
		"qu":("【联盟】警告", ("10.207.141.155", 8000), ("quanju2.app100718848.twsapp.com", 8000)),
		"ft":("【繁体】警告", ("192.168.11.111", 8008), ("220.130.123.111", 8008)),
		"na":("【北美】警告", ("172.31.39.96", 8008), ("54.201.126.154", 8008)),
		"kgg":("【北美kgg】警告", ("kgg-global.legendknight.com", 8000), ("kgg-global.legendknight.com", 8000)),
		#"xp":("【北美xp伦敦】警告", ("na101xp-global.101xp.com", 8008), ("na101xp-global.101xp.com", 8008)),
		#"xpuse":("【北美xp东部】警告", ("na101xp-use-global.101xp.com", 8008), ("na101xp-use-global.101xp.com", 8008)),
		#"xpusw":("【北美xp西部】警告", ("na101xp-usw-global.101xp.com", 8008), ("na101xp-usw-global.101xp.com", 8008)),
		"rumsk":("【俄罗斯(莫)】警告", ("msk-ver.srv.dragonknight.ru", 8008), ("msk-ver.srv.dragonknight.ru", 8008)),
		"rusp":("【俄罗斯(社交版)】警告", ("sp-global.srv.dragonknight.ru", 8008), ("sp-global.srv.dragonknight.ru", 8008)),
		"ruxp":("【俄罗斯(101xp)】警告", ("xp-global-srv.101xp.com", 8008), ("xp-global-srv.101xp.com", 8008)),
		"tk":("【土耳其】警告", ("beta01.salagame.com", 8008), ("beta01.salagame.com", 8008)),
		"fr":("【法语】警告", ("dkfr-ver.cdd.opogame.com", 8008), ("dkfr-ver.cdd.opogame.com", 8008)),}

AddWarnUrl = None
#QQWindow_Handle = '"C:\Program Files (x86)\Tencent\TM\Bin\QQScLauncher.exe" /uin:3138968600 /quicklunch:6368201A0F27997D9FFCB2DA9099141C5365A432A4A483E3E5ACDEE34E2E9382BD4C96831CF785EA'
#QQWindow_Handle = '"C:\Program Files\Tencent\TM\Bin\QQScLauncher.exe" /uin:3138968600 /quicklunch:750046BA5F4A058507DFAECA32E75BE5F10B975F5211F0CF83A50F44BC4814D47FDA4113FE4BC232'
QQWindow_Handle = '"C:\Program Files (x86)\Tencent\TM\Bin\QQScLauncher.exe" /uin:3138968600 /quicklunch:61E5C508D24067B894102C8AE62969E590312632D7FAE65D19949C9E88516F187D3B7FFB3A6B5CB7'
QQWindow_Handle = '"D:\Program Files (x86)\Tencent\TM\Bin\QQScLauncher.exe" /uin:3161490549 /quicklunch:4882E129F7F23B307E58BA6BF856866C8EB0992A9524413A059BD8C05F3675876B7A44EDF9AE6F1D'
QQWindow_Name = "GameCenter"

#http://banben1.app100718848.twsapp.com:8008/Tool/Warn/GetWarn/?cnt=200

#内网地址就可以了,因为是直接在Linux机器上面运行的脚本
AddWarn_Http = "http://%s:%s/Tool/Warn/AddWarn/?"
#下面两个需要提供外网地址,这个是运行在108上面访问后台的地址，必须是外网地址
GetWarn_Http = "http://%s:%s/Tool/Warn/GetWarn/?cnt=200"
GetWarn_More_Http = "还有%%s条-http://%s:%s/Tool/Warn/GetWarnEx/?tkey=%%s\n"
WarnMsg = "%s : 区ID:%%s 时间:%%s"


GetWarnDict = {}

def InitAddWarnUrl(env):
	#linux运行
	global AddWarnUrl, EnvDict
	if env.startswith("tw") or env.startswith("ft"):
		AddWarnUrl = AddWarn_Http % EnvDict["ft"][1]
		return True
	for key, data in EnvDict.iteritems():
		if env.startswith(key):
			AddWarnUrl = AddWarn_Http % data[1]
			return True
	return False
	
def InitGetWarnUrl():
	#windows
	global GetWarnDict, EnvDict, WarnMsg
	for key, data in EnvDict.iteritems():
		getWarn_url = GetWarn_Http % data[2]
		getWarn_More_url = GetWarn_More_Http % data[2]
		GetWarnDict[key] = (WarnMsg % data[0], getWarn_url, getWarn_More_url)



#===============================================================================
# 在Linux上，扫描警告并通过HTTP发送
#===============================================================================
class CheckInfo(object):
	def __init__(self, file_name):
		self.file_path = DynamicPath.FilePath + file_name
	
	def __enter__(self):
		try:
			with open(self.file_path) as f:
				self.data = eval(f.read())
		except:
			self.data = {}
		return self
	
	def __exit__(self, _type, _value, _traceback):
		try:
			with open(self.file_path, "w") as f:
				f.write(repr(self.data))
		except:
			traceback.print_exc()
		return False
	
	def find_warn(self):
		two_month_ago = datetime.datetime.now() - datetime.timedelta(days = 60)
		for file_path in glob.glob(DynamicPath.FilePath + "*.log"):
			# 计算创建时间
			lis = file_path[len(DynamicPath.FilePath):-4].split("_")
			zone_id = 0
			file_time = None
			if lis[0] == "MainStack":
				zone_id = int(lis[2])
				file_time = datetime.datetime(int(lis[3]), int(lis[4]), int(lis[5]))
			else:
				zone_id = int(lis[1])
				file_time = datetime.datetime(int(lis[2]), int(lis[3]), int(lis[4]))
			# 60天以前的日志删除之
			if file_time < two_month_ago:
				# 删除文件
				os.remove(file_path)
				# 删除记录
				if file_path in self.data:
					del self.data[file_path]
				continue
			# 文件没有新的长度，不用处理
			stat = os.stat(file_path)
			if stat.st_size <= self.data.get(file_path, 0):
				continue
			
			self.find_warn_one(zone_id, file_path)
	
	def find_warn_one(self, zone_id, file_path):
		print "find_warn_one", zone_id, file_path
		with open(file_path) as f:
			# 设置开始扫描位置
			f.seek(self.data.get(file_path, 0))
			# 开始扫描之
			trace_back = []
			btraceback = False
			for line in f:
				if line.find("GE_EXC") >= 0:
					self.send_http(zone_id, line)
					continue
				if line.find("Traceback") >= 0:
					btraceback = True
					trace_back.append(line)
					continue
				if btraceback:
					trace_back.append(line)
					if line.find("Error") >= 0:
						self.send_http(zone_id, "".join(trace_back))
						trace_back =[]
						btraceback = False
			# 记录扫描位置
			self.data[file_path] = f.tell()
	
	def send_http(self, zone_id, text):
		# 屏蔽特殊的(不屏蔽了)
#		if text.find("C++ obj is NULL") >= 0:
#			return
		get = {"zone_id":zone_id, "text":text}
		global AddWarnUrl
		url = AddWarnUrl + urllib.urlencode(get)
		try:
			urllib.urlopen(url)
		except:
			traceback.print_exc()

def LoopLinux():
	try:
		with CheckInfo("check_file_dict.txt") as cf:
			cf.find_warn()
	except:
		traceback.print_exc()

#===============================================================================
# 在Windows机器上，从HTTP获取警告通过QQ发送
#===============================================================================
# 直接发送
def SendQQMsg1(handle, msg):
	import win32gui
	import win32con
	# 先转成Unicode编码
	for c in msg:
		# 特殊处理换行
		if c == '\n':
			win32gui.SendMessage(handle, win32con.WM_KEYDOWN, ord(c))
			win32gui.SendMessage(handle, win32con.WM_KEYUP, ord(c))
			time.sleep(1)
			continue
		# 模拟发送
		win32gui.SendMessage(handle, win32con.WM_CHAR, ord(c), 0)
	# 发送回车
	win32gui.SendMessage(handle, win32con.WM_KEYDOWN, win32con.VK_RETURN)
	win32gui.SendMessage(handle, win32con.WM_KEYUP, win32con.VK_RETURN)

# 尝试转码
def SendQQMsg2(handle, msg):
	import win32gui
	import win32con
	# 先转成Unicode编码
	msg = msg.decode()
	for c in msg:
		# 特殊处理换行
		if c == '\n':
			win32gui.SendMessage(handle, win32con.WM_KEYDOWN, ord(c))
			win32gui.SendMessage(handle, win32con.WM_KEYUP, ord(c))
			time.sleep(1)
			continue
		# 在转化为GBK编码
		c = c.encode("GBK")
		# 填充为4字节
		c = c.ljust(4, '\0')
		# 转为整数
		c = struct.unpack("I", c)[0]
		# 模拟输入法发送
		win32gui.SendMessage(handle, win32con.WM_IME_CHAR, c, 0)
	# 发送回车
	win32gui.SendMessage(handle, win32con.WM_KEYDOWN, win32con.VK_RETURN)
	win32gui.SendMessage(handle, win32con.WM_KEYUP, win32con.VK_RETURN)

# 尝试转码
def SendQQMsg3(handle, msg):
	import win32gui
	import win32con
	# 先转成Unicode编码
	msg = msg.decode()
	for c in msg:
		# 特殊处理换行
		if c == '\n':
			win32gui.SendMessage(handle, win32con.WM_KEYDOWN, ord(c))
			win32gui.SendMessage(handle, win32con.WM_KEYUP, ord(c))
			time.sleep(1)
			continue
		# 在转化为GBK编码
		c = c.encode("GBK")
		# 反转
		l = list(c)
		l.reverse()
		c = "".join(l)
		# 填充为4字节
		c = c.ljust(4, '\0')
		# 转为整数
		c = struct.unpack("I", c)[0]
		# 模拟输入法发送
		win32gui.SendMessage(handle, win32con.WM_IME_CHAR, c, 0)
	# 发送回车
	win32gui.SendMessage(handle, win32con.WM_KEYDOWN, win32con.VK_RETURN)
	win32gui.SendMessage(handle, win32con.WM_KEYUP, win32con.VK_RETURN)
########################################################################################

def SendQQMsg(msgs):
	import win32gui
	global QQWindow_Handle, QQWindow_Name
	# 尝试打开窗口
	os.system(QQWindow_Handle)
	# 获取窗口句柄
	for _ in xrange(3):
		handle = win32gui.FindWindow(None, QQWindow_Name)
		if handle: break
		time.sleep(1)
	# 检测handle
	if not handle:
		print "SendQQMsg not handle", QQWindow_Handle, QQWindow_Name
		return
	# 发送消息
	for msg in msgs:
		SendQQMsg3(handle, msg)
		# 休息下
		time.sleep(2)

def SendWarn(evn, getwarnurls):
	# 获取警告,发送到QQ上面
	warnmsg, getwarnurl, getwarnmoreurl = getwarnurls
	body = eval(urllib2.urlopen(getwarnurl, None, 10).read())
	print datetime.datetime.now(), len(body), evn
	if not body:
		return
	# 警告分类
	key_cnt = {}
	key_text = {}
	for _, zone_id, key, recv_time, text in body:
		if key in key_cnt:
			key_cnt[key] = key_cnt[key] + 1
		else:
			key_cnt[key] = 1
			key_text[key] = (zone_id, recv_time, text)
	# 组合警告
	msgs = []
	for key, cnt in key_cnt.iteritems():
		msg = []
		zone_id, rect_time, text = key_text[key]
		msg.append(warnmsg % (zone_id, rect_time))
		if cnt > 1:
			msg.append(getwarnmoreurl % (cnt, key))
		msg.append(str(text))
		msgs.append("\n".join(msg))
	# 发送
	SendQQMsg(msgs)
	return msgs


def LoopWindowsQQ():
	SendQQMsg(["QQWarn Start...."])
	global GetWarnDict
	while 1:
		try:
			hasWarn = False
			print "SendWarn Loop", datetime.datetime.now(), len(GetWarnDict)
			for env, getwarnurls in GetWarnDict.iteritems():
				try:
					print "SendWarn Start env", env
					if SendWarn(env, getwarnurls):
						time.sleep(5)
						hasWarn = True
					print "SendWarn Ok", datetime.datetime.now(), hasWarn
				except:
					print "Send Warn error", env
					traceback.print_exc()
			if hasWarn is False:
				time.sleep(60)
		except:
			print "LOOP has except, print", datetime.datetime.now()
			traceback.print_exc()
			time.sleep(30)
			print "SLEEP END, ", datetime.datetime.now()



if __name__ == "__main__":
	if platform.system() == "Windows":
		InitGetWarnUrl()
		LoopWindowsQQ()
	else:
		import Environment
		evn = Environment.ReadConfig()
		#初始化环境
		InitAddWarnUrl(evn)
		LoopLinux()

