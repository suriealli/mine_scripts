#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("ComplexServer.InitEx")
#===============================================================================
# 特殊初始化(服务器启动命令参数中进程ID是 0 就会触发这个函数，构建启动服务器脚本)
#===============================================================================
def InitScript(process_type, process_id, listen_port):
	import AutoStart
	import BuildStart
	print process_type, process_id, listen_port
	if process_type == "A":
		AutoStart.auto_start()
	elif process_type == "B":
		# 用于在没MySQLdb的机器上构建启动脚本
		BuildStart.Build()
