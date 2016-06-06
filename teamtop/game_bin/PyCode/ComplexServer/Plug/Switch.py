#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("ComplexServer.Plug.Switch")
#===============================================================================
# 插件开关模块
#===============================================================================
import cProcess
import cComplexServer
import Environment
import traceback
from World import Define

def InitPlug():
	'''
	初始化这个进程的插件
	'''
	# 设置打印Python堆栈函数
	from Util import Trace
	cProcess.SetStackWarnFun(Trace.StackWarn)
	# 设置环境中的各个值
	# 调用启动函数（根据进程类型）
	fun = globals()[cProcess.ProcessType]
	fun()

#def All():
#	# 标记个个功能
#	Environment.HasControl = True
#	Environment.HasDB = True
#	Environment.HasGateway = True
#	Environment.HasHttp = True
#	Environment.HasLogic = True
#	# 创建网络层
#	cComplexServer.CreateNetwork(10000, 3, 3)
#	cComplexServer.Listen(cProcess.ListenPort)
#	#设置接收客户端发送过来的消息缓存大小为1024 * 24，如果超过就会把客户端T掉
#	cComplexServer.SetConnectParam(10, 1024 * 24, 1000, 1024 * 8)
#	# 单进程服务要启动Python线程
#	cComplexServer.SetPyThread(True)
#	# 内网开启线程发送(暂时关闭了)
#	cComplexServer.SetSendModel(False)
#	# 开启HTTP工作
#	from ComplexServer.Plug.Http import HttpWork
#	HttpWork.StartWorkThread()
#	# 构建表并开启DB工作
#	from ComplexServer.Plug.DB import DBWork, RoleTable, SystemTable, LogTable
#	RoleTable.BuildTable()
#	SystemTable.BuildTable()
#	LogTable.BuildTable()
#	# 处理合服数据
#	from ComplexServer.Plug.DB import DBMerge
#	try:
#		DBMerge.DoMerge()
#	except:
#		from Util import Trace
#		traceback.print_exc()
#		Trace.StackWarn("swith All error in domerge.")
#		cProcess.Crash()
#	DBWork.StartWorkThread()
#	# 设置可接受客户端连接
#	from Common.Connect import Who
#	from ComplexServer import Connect
#	Connect.RegICanWho(Who.enWho_Client_)

def C():
	# 标记个个功能
	Environment.HasControl = True
	# 创建网络层
	cComplexServer.CreateNetwork(10000, 3, 0)
	cComplexServer.Listen(cProcess.ListenPort)
	# 有Http服务要启动Python线程
	cComplexServer.SetPyThread(True)
	# 开启HTTP工作
	from ComplexServer.Plug.Http import HttpWork
	HttpWork.StartWorkThread()
	# 设置可接受逻辑进程连接
	from Common.Connect import Who
	from ComplexServer import Connect
	Connect.RegICanWho(Who.enWho_Control_)
	# 设置为控制服务
	from ComplexServer.Plug.Control import ControlProxy
	ControlProxy.IAMControlServer()

def D():
	# 标记个个功能
	Environment.HasDB = True
	# 创建网络层
	cComplexServer.CreateNetwork(10000, 3, 0)
	cComplexServer.Listen(cProcess.ListenPort)
	# 有数据库服务要启动Python线程
	cComplexServer.SetPyThread(True)
	# 构建表并开启DB工作
	from ComplexServer.Plug.DB import DBWork, DBProxy, RoleTable, SystemTable, LogTable
	RoleTable.BuildTable()
	SystemTable.BuildTable()
	LogTable.BuildTable()
	# 处理合服数据
	from ComplexServer.Plug.DB import DBMerge
	try:
		DBMerge.DoMerge()
	except:
		from Util import Trace
		traceback.print_exc()
		Trace.StackWarn("swith D error in domerge.")
		cProcess.Crash()
	
	DBWork.StartWorkThread()
	# 设置为数据库服务
	DBProxy.IAMDBServer()
	# 设置可接受逻辑进程端连接
	from Common.Connect import Who
	from ComplexServer import Connect
	Connect.RegICanWho(Who.enWho_Logic_)

def GHL():
	# 标记个个功能
	Environment.HasGateway = True
	Environment.HasHttp = True
	Environment.HasLogic = True
	# 创建网络层
	cComplexServer.CreateNetwork(10000, 3, 3)
	cComplexServer.Listen(cProcess.ListenPort)
	cComplexServer.SetConnectParam(10, 1024 * 8, 1000, 1024 * 8)
	# 有Http服务要启动Python线程
	cComplexServer.SetPyThread(True)
	if Environment.IsCross:
		#跨服开启
		cComplexServer.SetSendModel(True)
	else:
		# 有可能有大量客户端连接，需要开启线程发送(暂时关闭了，发消息延后有可能导致玩家登录消息发送不全)
		cComplexServer.SetSendModel(False)
	# 开启HTTP工作
	from ComplexServer.Plug.Http import HttpWork
	if Environment.IsCross:
		HttpWork.HTTP_THREAD_NUM = 8
	HttpWork.StartWorkThread()
	# 设置可接受客户端连接、逻辑进程主动连接
	from Common.Connect import Who
	from ComplexServer import Connect
	Connect.RegICanWho(Who.enWho_Client_)
	Connect.RegICanWho(Who.enWho_Logic)
	Connect.RegICanWho(Who.enWho_Control)
	# 获取连接信息
	from ComplexServer.Plug.DB import DBHelp
	c_process_info, d_process_info, ghl_process_info, merge_d_process_infos = DBHelp.GetStandardZoneConnectByID(cProcess.ProcessID)
	# 断言下
	assert cProcess.ProcessID == ghl_process_info[0]
	assert Environment.IP == ghl_process_info[1]
	assert cProcess.ListenPort == ghl_process_info[2]
	# 构建DB代理
	from ComplexServer.Plug.DB import DBProxy
	DBProxy.NetMethod()
	DBProxy.ConnectDBServer(None, d_process_info)
	# 记录合服数量
	global MergeZoneCount
	MergeZoneCount = len(merge_d_process_infos)
	for merge_d_process_info in merge_d_process_infos:
		DBProxy.ConnectDBServer(None, merge_d_process_info)
		LocalServerIDs.add(merge_d_process_info[0])
	#取出最大的进程ID
	global MaxProcessId
	MaxProcessId = max(LocalServerIDs)
	
	# 如果是跨服，则还要连接其他的DBServer
	if cProcess.ProcessID in Define.CrossWorlds:
		extend_process_infos = DBHelp.GetCrossZoneConnectByID(cProcess.ProcessID)
		for process_info in extend_process_infos:
			DBProxy.ConnectDBServer(None, process_info)
	# 构建ControlProxy
	from ComplexServer.Plug.Control import ControlProxy
	ControlProxy.NetMethod(*c_process_info)

if "_HasLoad" not in dir():
	MergeZoneCount = 0
	LocalServerIDs = set([cProcess.ProcessID])
	MaxProcessId = cProcess.ProcessID
	