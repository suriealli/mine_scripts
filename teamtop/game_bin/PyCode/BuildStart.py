#!/usr/bin/env python
# -*- coding:UTF-8 -*-
import os
import sys
path = os.path.dirname(os.path.realpath(__file__))
path = path[:path.find("PyCode") + 6]
if path not in sys.path: sys.path.append(path)
path = path.replace("PyCode", "PyHelp")
if path not in sys.path: sys.path.append(path)
#===============================================================================
# 构建启动脚本
#===============================================================================
import Environment
import DynamicPath
from World import Define
from ThirdLib import PinYin

def GetProcessInfo():
	from ComplexServer.Plug.DB import DBHelp
	from Integration.Help import WorldHelp
	l = []
	con = DBHelp.ConnectGlobalWeb()
	with con as cur:
		cur.execute("select name from computer where ip = %s;", Environment.IP)
		result = cur.fetchall()
		if not result:
			print "GE_EXC, not this ip ProcessInfo in GetProcessInfo"
			return []
		name = result[0][0]
		cur.execute("select ptype, pid, port, work_zid from process where computer_name = %s;", name)
		for ptype, pid, port, work_zid in cur.fetchall():
			l.append((ptype, pid, port, work_zid, WorldHelp.GetZoneNameByZID(cur, work_zid)))
		return l

def GetProcessLanguage(pid):
	from ComplexServer.Plug.DB import DBHelp
	con = DBHelp.ConnectGlobalWeb()
	with con as cur:
		cur.execute("select language from zone where zid = %s;", pid)
		result = cur.fetchall()
		if not result:
			return None
		return result[0][0]

def BuildWindow():
	# 删除所有的自动启动脚本
	os.system("del %sauto*" % DynamicPath.ScriptPath)
	from Integration.Help import WorldHelp
	script_files = []
	zones = {}
	process_info = GetProcessInfo()
	for ptype, pid, port, work_zid, work_zone_name in process_info:
		# 控制进程特殊启动
		if Define.IsControlProcessKey(ptype):
			file_name = "auto_start_control_%s.bat" % pid
			script_files.append(file_name)
			# 构建启动控制进程的脚本
			with open(DynamicPath.ScriptPath + file_name, "w") as f:
				print >>f, "cd .."
				print >>f, "cd Bin"
				print >>f, "start ComplexServer.exe", ptype, pid, port
				print >>f, "cd .."
				print >>f, "cd Script"
		# 按照区分类
		else:
			zone_info = zones.get(work_zid)
			if zone_info is None:
				zones[work_zid] = zone_info = (work_zone_name, [])
			zone_info[1].append((ptype, pid, port))
	# 按区构建启动进程的脚本
	PinYin.Load()
	for zid, zone_info in zones.iteritems():
		zone_name, process_info = zone_info
		process_info.sort(key=lambda t:t[0], cmp=WorldHelp.CmpProcessKey)
		file_name = "auto_start_%s[%s].bat" % (zid, "_".join(PinYin.GetPinYin(zone_name)))
		script_files.append(file_name)
		with open(DynamicPath.ScriptPath + file_name, "w") as f:
			print >>f, "cd .."
			print >>f, "cd Bin"
			for ptype, pid, port in process_info:
				print >>f, "start ComplexServer.exe", ptype, pid, port
			print >>f, "cd .."
			print >>f, "cd Script"
	# 构建全部的启动脚本
	with open(DynamicPath.ScriptPath + "auto_start.bat", "w") as f:
		for file_name in script_files:
			print >>f, "call", file_name
	PinYin.Release()

def BuildLinux():
	# 删除所有的自动启动脚本
	os.system("rm -rf %sauto*" % DynamicPath.ScriptPath)
	from Integration.Help import WorldHelp
	script_files = []
	zones = {}
	process_info = GetProcessInfo()
	for ptype, pid, port, work_zid, work_zone_name in process_info:
		# 控制进程特殊启动
		if Define.IsControlProcessKey(ptype):
			file_name = "auto_start_control_%s.sh" % pid
			script_files.append(file_name)
			# 构建启动控制进程的脚本
			with open(DynamicPath.ScriptPath + file_name, "w") as f:
				print>>f, "ulimit -c unlimited"
				print>>f, "ulimit -n 10240"
				print>>f, "export PYTHONHOME=%s" % DynamicPath.PythonHome
				print >>f, "cd .."
				print >>f, "cd Bin"
				print >>f, "./ComplexServer", ptype, pid, port, "&> /dev/null < /dev/null &"
				print >>f, "cd .."
				print >>f, "cd Script"
		# 按照区分类
		else:
			zone_info = zones.get(work_zid)
			if zone_info is None:
				zones[work_zid] = zone_info = (work_zone_name, [])
			zone_info[1].append((ptype, pid, port))
	# 按区构建启动进程的脚本
	PinYin.Load()
	for zid, zone_info in zones.iteritems():
		zone_name, process_info = zone_info
		process_info.sort(key=lambda t:t[0], cmp=WorldHelp.CmpProcessKey)
		file_name = "auto_start_%s[%s].sh" % (zid, "_".join(PinYin.GetPinYin(zone_name)))
		script_files.append(file_name)
		with open(DynamicPath.ScriptPath + file_name, "w") as f:
			print>>f, "ulimit -c unlimited"
			print>>f, "ulimit -n 10240"
			print>>f, "export PYTHONHOME=%s" % DynamicPath.PythonHome
			print >>f, "cd .."
			print >>f, "cd Bin"
			for ptype, pid, port in process_info:
				# 这里要注意下，要将默认的3流定位到空设备，否则可能导致shell不能返回
				print >>f, "./ComplexServer", ptype, pid, port, "&> /dev/null < /dev/null &"
			print >>f, "cd .."
			print >>f, "cd Script"
	# 构建全部的启动脚本
	with open(DynamicPath.ScriptPath + "auto_restart.sh", "w") as f:
		print>>f, "pkill -f 'ComplexServer'"
		for file_name in script_files:
			print >>f, "sh", file_name, "&"
	PinYin.Release()

def Build():
	if Environment.IsWindows:
		BuildWindow()
	else:
		BuildLinux()

if __name__ == "__main__":
	Build()
	print "Build End."

