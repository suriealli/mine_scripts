#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 提交后的处理
#===============================================================================
import os
import sys
path = os.path.dirname(os.path.realpath(__file__))
path = path[:path.find("PyCode") + 6]
if path not in sys.path: sys.path.append(path)
path = path.replace("PyCode", "PyHelp")
if path not in sys.path: sys.path.append(path)

import struct
import Environment
from Util import OutBuf
from Util.PY import Load
from Common.Message import AutoMessage
from ComplexServer.Log import AutoLog

OPEN_LONG_QI_QQ_WINDOW = '"C:\Program Files (x86)\Tencent\QQ\Bin\QQScLauncher.exe" /uin:2366057235 /quicklunch:2B75876A6186F5C03F6F662BE0FE3F94DC70E68121A7515408ACF5EC81C458E833A382CDD6B9939D'
LONG_QI_QQ_WINDOW_NAME = "longqishi"

def send_qq_msg(msg):
	try:
		import win32gui
		import win32con
		# 尝试打开窗口
		os.system(OPEN_LONG_QI_QQ_WINDOW)
		handle = win32gui.FindWindow(None, LONG_QI_QQ_WINDOW_NAME)
		if not handle:
			return
		# 先转成Unicode编码
		msg = msg.decode()
		for c in msg:
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
	except:
		pass

def get_user():
	try:
		with open(r"D:\Repositories\GameProject\hooks\author.txt") as f:
			return f.read()
	except:
		return "unknown"

def has_config():
	try:
		with open(r"D:\Repositories\GameProject\hooks\changed.txt") as f:
			changed = f.read()
			return changed.find("trunk/Config") >= 0;
	except:
		return False

if __name__ == "__main__":
	if has_config():
		Environment.HasLogic = True
		AutoMessage.SvnUp(False)
		AutoLog.SvnUp(False)
		with OutBuf.OutBuf_NoExcept() as out:
			Load.LoadPartModule("Global")
			Load.LoadPartModule("ComplexServer")
			Load.LoadPartModule("Game")
		result = out.get_value()
		if result.find("GE_EXC") >= 0 or result.find("Traceback") >= 0:
			send_qq_msg("%s's commit has except." % get_user())
			sys.stderr.write(result)
			sys.exit(1)
		else:
			sys.exit(0)
sys.exit(0)
