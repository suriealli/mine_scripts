#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 提交前的检测
#===============================================================================
import os
import sys
path = os.path.dirname(os.path.realpath(__file__))
path = path[:path.find("PyCode") + 6]
if path not in sys.path: sys.path.append(path)
path = path.replace("PyCode", "PyHelp")
if path not in sys.path: sys.path.append(path)

import urllib
import Environment
from Util import OutBuf
from Util.PY import Load
from Common.Message import AutoMessage
from ComplexServer.Log import AutoLog

iptoname ={
"192.168.1.206":"杨鸿鹏",
"192.168.3.139":"王跃智",
"192.168.1.85":"左冬冬",
"192.168.1.82":"詹宇轩",
"192.168.5.16":"方继伟",
"192.168.6.21":"冯均浩",
"192.168.4.157":"林斌",
"192.168.5.236":"黄伟奇",
"192.168.5.81":"朱墨",
"192.168.1.105":"高亮亮",
}

tips = "提交时，服务器检测有异常与报错！ From -- 【%s】。 (建议提交前先启动服务器检测一下)"

def GetName():
	return iptoname.get(Environment.IP, Environment.IP)

def send_http(b = False):
	try:
		get = {"zone_id":1, "text": tips % GetName()}
		url = "http://banben1.app100718848.twsapp.com:8008/Tool/Warn/AddWarn/?" + urllib.urlencode(get)
		urllib.urlopen(url)
	except:
		if b:
			import traceback
			traceback.print_exc()

if __name__ == "__main__":
	Environment.HasLogic = True
	AutoMessage.SvnUp(False)
	AutoLog.SvnUp(False)
	with OutBuf.OutBuf_NoExcept() as out:
		Load.LoadPartModule("Global")
		Load.LoadPartModule("ComplexServer")
		Load.LoadPartModule("Game")
	
	result = out.get_value()
	out.pprint(result)
	
	if result.find("GE_EXC") >= 0 or result.find("Traceback") >= 0:
		send_http()
		sys.stderr.write(result)
		sys.exit(1)
	else:
		sys.exit(0)
