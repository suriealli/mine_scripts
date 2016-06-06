#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 游戏脚本的初始化模块
#==============================================================================
import sys
import datetime
import cProcess
import cDateTime
import cComplexServer
import Environment
import DynamicPath
from Util import Callback
from Util.PY import Load
from Util.File import ObjFile
from World import Language



# 是否记录启动服务器的时间
ShowInitCost = False
IsStopState = False

def InitScript():
	if ShowInitCost:
		from Util import Profile
		Profile.StratProfile()
	# 真正的初始化
	_InitScript()
	if ShowInitCost:
		Profile.DumpProfile("init")
		Profile.EndProfile()

def _InitScript():
	# 重定向定向IO
	RedirectOutFile(True)
	sys.stdout = cProcess
	sys.stderr = cProcess
	# 初始MySQLdb
	cComplexServer.InitMySQLdb()
	#载入服务器语言版本信息和跨服信息
	Environment.LoadLanguage()
	Environment.LoadCross()
	if Environment.Language != "default":
		#需要翻译包,按照语言版本读取对应的语言包
		Language.LoadLanguageConfigEX(Environment.Language)
	#Language.LoadLanguageConfigEX("english")
	# 第1步要设置时间,并且验证时间是单调递增的
	cDateTime.SetUnixTime(cDateTime.Seconds())
	gap, saveTime = ObjFile.GetObj(SaveTimeFilePath, (0, cDateTime.Now()))
	# 上次进程意外关闭，计算关闭时间
	if gap:
		saveTime = saveTime + datetime.timedelta(seconds = gap * 60)
	# 断言此时的时间晚于进程上次关闭的时间，保证进程的时间单调递增
	if saveTime > cDateTime.Now():
		if not Environment.IsWindows:
			print "GE_EXC, save time(%s) <= now(%s)" % (saveTime, cDateTime.Now())
	# 设置保存进程时间
	SaveProcessTime()
	cComplexServer.RegSaveCallFunction1(SaveProcessTime)
	# 载入脚本Global、Common
	Load.LoadPartModuleEx("Common")
	Load.LoadPartModuleEx("Global")
	# 计算插件环境
	from ComplexServer.Plug import Switch
	Switch.InitPlug()
	# 更新消息个日志文件
	from Common.Message import AutoMessage
	from ComplexServer.Log import AutoLog
	AutoMessage.SvnUp()
	AutoLog.SvnUp()
	# 载入脚本
	Load.LoadPartModuleEx("ComplexServer")
	if Environment.HasDB:
		Load.LoadPartModuleEx("DB")
	if Environment.HasLogic:
		Load.LoadPartModuleEx("Game")
	if Environment.HasControl:
		Load.LoadPartModuleEx("Control")
	# 提交新的日志和消息文件
	AutoMessage.SvnCommit()
	AutoLog.SvnCommit()
	
	if Environment.Language != "default":
		#需要翻译包,按照语言版本读取对应的语言包
		Language.LoadLanguageScriptEx(Environment.Language)
	#Language.LoadLanguageScriptEx("english")
	
	# 触发其他的初始化回调
	InitCallBack.CallAllFunctions()
	# 开启监控线程
	if not Environment.IsQQUnion:
		from ComplexServer import Watch
		Watch.StartWorkThread()
	# 启动完毕
	from Game.Role import Event
	#脚本载入完毕前只能注册事件不能触发事件
	Event.HasFinishLoad = True
	#脚本载入完毕，配置表读取完毕，这个事件可以处理配置表之间的依赖
	Event.TriggerEvent(Event.Eve_AfterLoadSucceed, 1, 1)
	print "RED", "GREEN", "BLUE", "<< %s %s Server Start At %s>>" % (cProcess.ProcessType, cProcess.ProcessID, cDateTime.Now())
	if Environment.IsWindows:
		import os
		os.system("title %s %s" % (cProcess.ProcessType, cProcess.ProcessID))
	#注册重定向触发(不要写在模块级下面，这个和服务器启动先后逻辑有关系)
	cComplexServer.RegAfterNewDayCallFunction(RedirectOutFile)
	
def SaveProcessTime():
	# 保存进程保存状态的时间和当前时间
	# 用于在进程异常关闭的时候计算关闭时间
	GPM1, _, _ = cComplexServer.GetSaveGapMinute()
	ObjFile.SaveObj(SaveTimeFilePath, (GPM1, cDateTime.Now()))

def FinalScript():
	# 触发器的的结束回调
	FinalCallBack.CallAllFunctions()
	# 此时一定要保存进程关闭的时间
	ObjFile.SaveObj(SaveTimeFilePath, (0, cDateTime.Now()))

def RedirectOutFile(isup = False):
	# Win环境下不输出到文件
	if Environment.IsWindows:
		return
	# 非逻辑模块不需要多次切换日志文件
	if (not isup) and (not Environment.HasLogic):
		return
	now = cDateTime.Now()
	file_path = "%s%s_%s_%s_%s_%s.log" % (DynamicPath.FilePath, cProcess.ProcessType, cProcess.ProcessID, now.year, now.month, now.day)
	cProcess.RedirectOutBuf(file_path)

if "_HasLoad" not in dir():
	SaveTimeFilePath = "savetime_%s_%s.txt" % (cProcess.ProcessType, cProcess.ProcessID)
	InitCallBack = Callback.LocalCallback()
	FinalCallBack = Callback.LocalCallback()
	
