#!/usr/bin/env python
# -*- coding:UTF-8 -*-
import os
import sys
from Tool.GM import GMCMD
path = os.path.dirname(os.path.realpath(__file__))
path = path[:path.find("PyCode") + 6]
if path not in sys.path: sys.path.append(path)
path = path.replace("PyCode", "PyHelp")
if path not in sys.path: sys.path.append(path)
#===============================================================================
# 启动服务器
#===============================================================================
import time
import signal
import subprocess
import BuildStart
import DynamicPath 

PROCESSS = []
class Process(object):
	def __init__(self, ptype, pid, port):
		self.ptype = ptype
		self.pid = pid
		self.port = port
		self.process = subprocess.Popen(args = [DynamicPath.BinPath + "ComplexServer.exe", ptype, str(pid), str(port)],
						stdin = subprocess.PIPE,
						cwd = DynamicPath.BinPath,
						creationflags = subprocess.CREATE_NEW_PROCESS_GROUP)
		PROCESSS.append(self)

def force_kill_all():
	print os.system("TASKKILL /F /IM ComplexServer.exe")

def create_all():
	for ptype, pid, port, _, _, in BuildStart.GetProcessInfo():
		Process(ptype, pid, port)

def kill_all():
	global PROCESSS
	for process in PROCESSS:
		process.process.kill()
	PROCESSS = []

def reload_ghl():
	for process in PROCESSS:
		if process.ptype != "GHL":
			continue
		gm = GMCMD.GMConnect("127.0.0.1", process.port, True)
		gm.iamgm()
		gm.gmcommand("ReloadAll()")

def ctrl_c(num, frame):
	if num != 2:
		return
	cmd = raw_input(">>")
	if cmd.endswith("\r\n"):
		cmd = cmd[:-2]
	elif cmd.endswith("\n"):
		cmd = cmd[:-1]
	if cmd == "q":
		kill_all()
		force_kill_all()
		sys.exit(0)
	elif cmd == "c":
		kill_all()
		create_all()
	elif cmd == "r":
		reload_ghl()
	else:
		print cmd
	time.sleep(36000)

def auto_start():
	signal.signal(signal.SIGINT, ctrl_c)
	create_all()
	time.sleep(36000)

if __name__ == "__main__":
	auto_start()
