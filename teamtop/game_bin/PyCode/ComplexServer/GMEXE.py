#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("ComplexServer.GMEXE")
#===============================================================================
# GM命令执行模块
#===============================================================================
import sys
import datetime
import traceback
import cDateTime
import cComplexServer
from Common.Connect import Who
from Common.Message import PyMessage
from ComplexServer import Connect
from ComplexServer.Log import AutoLog
from ThirdLib import PrintHelp
from Util import Profile, OutBuf
from Util.PY import Reload




# 定义其他模块的函数
pprint = PrintHelp.pprint
StratProfile = Profile.StratProfile
EndProfile = Profile.EndProfile
DumpProfile = Profile.DumpProfile
ShowProfile = Profile.ShowProfile
DumpAndShowProfile = Profile.DumpAndShowProfile
DumpStats = Profile.DumpStats
ShowReturn = Profile.ShowReturn
ClearReturn = Profile.ClearReturn

if "_HasLoad" not in dir():
	DISABLE_FUN = {}
	
	CannotTotimeServerIP = ["192.168.8.108", "192.168.8.167"]
# 执行GM指令的输出缓冲


def OnGMRequest(sessionid, msg):
	import Environment
	# 权限检查
	cinfo = Connect.ConnectDict[sessionid]
	if cinfo["who"] != Who.enWho_GM_:
		return
	# 上下文环境
	localdict = cinfo.get("localdict", {})
	# 执行之
	with AutoLog.AutoTransaction(AutoLog.traGM):
		# 只记录逻辑进程的GM日志
		if Environment.HasLogic:
			AutoLog.LogBase(AutoLog.SystemID, AutoLog.eveGM, msg)
		with OutBuf.OutBuf() as GF:
			try:
				exec(msg, globals(), localdict)
			except:
				traceback.print_exc()
			outerr = GF.get_value()
			GF.pprint(msg)
			GF.pprint("\n")
			GF.pprint(outerr)
			cComplexServer.SendPyMsg(sessionid, PyMessage.GM_Response, outerr)

def XRLAM(startswith, insteadData = False):
	'''
	安全重载一个模块
	@param startswith:模块匹配
	@param insteadData:是否替换数据
	'''
	hasReload = False
	for module in sys.modules.values():
		# 空模块不能reload
		if not module:
			continue
		# 不在指定目录下，不要reload
		if startswith.endswith("*"):
			if not module.__name__.startswith(startswith[:-1]):
				continue
		else:
			if not module.__name__ == startswith:
				continue
		# init模块不要重载
		if module.__name__.endswith("__init__"):
			continue
		# 自身不能reload
		if module.__name__ in (__name__, Reload.__name__):
			continue
		Reload.Reload(module, insteadData)
		# 标记重载了
		hasReload = True
		# 清空被关闭的函数
		if module.__name__ in DISABLE_FUN: del DISABLE_FUN[module.__name__]
		# 打印下重载的模块
		print module.__name__
	if hasReload is False:
		print "GE_EXC can't find module to reload by startswith(%s)." % startswith

def ReloadAll():
	'''重载所有改变过的模块'''
	from Util.PY import Load
	for module_name, module in sys.modules.items():
		module_time = Load.MODULE_FILE_TIME.get(module_name)
		if module_time is None:
			continue
		modify_time = Load.GetModuleModifyTime(module)
		if module_time == modify_time:
			continue
		Reload.Reload(module, False)
		Load.MODULE_FILE_TIME[module_name] = modify_time
		print "***** auto reload", module_name

def UniversalFunction(*argv, **kwgv):
	'''
	万能函数
	'''
	pass

def DisableFunction(moduleName, funName):
	'''
	禁用一个函数，就是把这个函数替换成一个空函数
	@param moduleName:模块名
	@param funName:函数名
	'''
	global DISABLE_FUN
	# 查找模块
	module = sys.modules.get(moduleName)
	if not module:
		print "GE_EXC, not module(%s) on DisableFunction" % moduleName
		return
	# 查找函数
	fun = getattr(module, funName, None)
	if not fun:
		print "GE_EXC, not module(%s).fun(%s) on DisableFunction" % (moduleName, funName)
		return
	# 替换函数
	fun.func_code = UniversalFunction.func_code
	fun.func_defaults = UniversalFunction.func_defaults
	fun.func_doc = UniversalFunction.func_defaults
	# 记录之
	funs = DISABLE_FUN.setdefault(moduleName, set())
	funs.add(funName)
	print "GE_EXC, disable module(%s).fun(%s)" % (moduleName, funName)

def ShowDisableFunction():
	'''
	打印被禁止的函数信息
	'''
	global DISABLE_FUN
	for modulename, funs in DISABLE_FUN.iteritems():
		print modulename
		for funname in funs:
			print "-->", funname

def Now():
	'''
	显示当前时间
	'''
	print cDateTime.Now()
	print cDateTime.Seconds()
	print cDateTime.Days()

def ToTime(hour = 0, minute = 0, second = 0, force = False):
	'''
	修改时间
	@param hour:时
	@param minute:分
	@param second:秒
	'''
	import Environment
	if force is False and not Environment.IsDevelop:
		print "GE_EXC, ToTime must in IsDevelop Environment"
		return
	
	if not Environment.IsDevelop:
		import cProcess
		from World import Define
		if cProcess.ProcessID not in Define.TestWorldIDs:
			print "GE_EXC, 正式服不能totime啊！"
			return
	
	global CannotTotimeServerIP
	if Environment.IP in CannotTotimeServerIP and force is False:
		print "GE_EXC, 108不能随便修改时间"
		return
	now = cDateTime.Now().time()
	to = datetime.time(hour, minute, second)
	if now > to:
		print "now(%s) > to(%s)" % (now, to)
		return
	inc = (to.hour - now.hour) * 3600 + (to.minute - now.minute) * 60 + to.second - now.second
	cDateTime.SetUnixTime(cDateTime.Seconds() + inc)
	from ComplexServer.Time import Cron
	Cron.OnInit()
	ToRole()
	print "now(%s) to(%s) inc(%s)" % (now, to, inc)

def ToDateTime(year, month, day, hour = 0, minute = 0, second = 0):
	'''
	修改时间
	@param year:年
	@param month:月
	@param day:日
	@param hour:时
	@param minute:分
	@param second:秒
	'''
	now = cDateTime.Now()
	to = datetime.datetime(year, month, day, hour, minute, second)
	if now > to:
		print "now(%s) > to(%s)" % (now, to)
		return
	dtl = (to - now)
	cDateTime.SetUnixTime(cDateTime.Seconds() + dtl.total_seconds())
	from ComplexServer.Time import Cron
	Cron.OnInit()
	ToRole()
	print "now(%s) to(%s) inc(%s)" % (now, to, dtl.total_seconds())

def ToSecond(second):
	'''
	快速过多少秒
	@param second:
	'''
	now = cDateTime.Now()
	cDateTime.SetUnixTime(cDateTime.Seconds() + second)
	from ComplexServer.Time import Cron
	Cron.OnInit()
	ToRole()
	print "now(%s) inc(%s)" % (now, second)

def ToRole():
	import cRoleMgr
	from Game.Role import Debug
	for role in cRoleMgr.GetAllRole():
		role.SendObj(Debug.Logic_ToTime, cDateTime.Seconds())
	
	import Environment
	import cProcess
	from World import Define
	if not Environment.IsDevelop and cProcess.ProcessID in Define.TestWorldIDs:
		tips = "+++++服务器时间改变  执行了 ToTime相关的指令+++++"
		cRoleMgr.Msg(1, 0, tips)

def FastTime(y = 0, m = 0, d = 0, H = 0, M = 0, S = 0):
	if not y: y = cDateTime.Year()
	if not m: m = cDateTime.Month()
	if not d: d = cDateTime.Day()
	if not H: H = cDateTime.Hour()
	if not M: M = cDateTime.Minute()
	if not S: S = cDateTime.Second()
	from Util import Time
	cComplexServer.SetFastEndTime(Time.DateTime2UnitTime(datetime.datetime(y, m, d, H, M, S)))

def Kill():
	'''
	关闭进程
	'''
	from ComplexServer import Kill as K
	K.Kill()

def MD5():
	'''
	检测进程的MD5值
	'''
	import FileCheck
	print FileCheck.CheckWorkMachine()


def CheckDataLoadDB():
	'''
	检测持久化数据是否全部载入
	'''
	from Game.Persistence import BigTable, Base
	if BigTable.AllLoadReturn and Base.AllLoadReturn:
		print (BigTable.AllLoadReturn, Base.AllLoadReturn)
	else:
		print "暂时不能开放普通号，服务器没完全载入数据", BigTable.AllLoadReturn, Base.AllLoadReturn

def ForceLoadPersistence():
	'''
	强制载入所有未载入的持久化
	'''
	from Game.Persistence import BigTable, Base
	BigTable.ForceLoadPersistence()
	Base.ForceLoadPersistence()

def IsOpen():
	from Game import Login
	if Login.LimitLoginAccount:
		print "服务器还没开放--"
	else:
		print True



def PyMemory():
	'''
	打印Python内存
	'''
	import gc
	from Util import Memory
	from Util.File import TabFile
	from Game.Persistence import BigTable
	objs = gc.get_objects()
	d = {}
	maxdict = {}
	for obj in objs:
		if isinstance(obj, TabFile.TabLine):
			t = TabFile.TabLine
		else:
			t = type(obj)
		d[t] = d.get(t, 0) + sys.getsizeof(obj)
		
		if type(obj) in( type({}), type(set()), type([]), type(tuple)):
			if t in maxdict:
				if sys.getsizeof(maxdict[t]) < sys.getsizeof(obj):
					maxdict[t] = obj
			else:
				maxdict[t] = obj
		
	kv = d.items()
	kv.sort(key=lambda item:item[1])
	show = 0
	unshow = 0
	print "============== obj"
	for t, c in kv:
		if c < 8096:
			unshow += c
		else:
			show += c
			print t, c / 1024
	print "total = %s, show = %s, unshow = %s" % (len(objs), show / 1024, unshow / 1024)
	print "============== big table"
	for name, table in BigTable.ALL_TABLES.iteritems():
		print name, Memory.GetTotalMemorySize(table.datas) / 1024
	print "===================== max obj"
	for t, obj in maxdict.iteritems():
		print "t", t, sys.getsizeof(obj)

def GetAllRole():
	'''
	获取所有的
	'''
	import cRoleMgr
	return cRoleMgr.GetAllRole()

def GAR():
	import cRoleMgr
	return cRoleMgr.GetAllRole()

def GR(roleID):
	import cRoleMgr
	return cRoleMgr.FindRoleByRoleID(roleID)

def PRL(roleID):
	import cRoleMgr
	role = cRoleMgr.FindRoleByRoleID(roleID)
	if not role:
		print "not online"
	else:
		pprint(role.GetTempObj(0))
		
def GetRoleByRoleID(roleID):
	'''
	根据角色ID获取角色对象
	@param roleID:
	'''
	import cRoleMgr
	return cRoleMgr.FindRoleByRoleID(roleID)


def GetRoleByRoleName(roleName):
	'''
	根据角色名获取角色对象
	@param roleID:
	'''
	from Game.Role import RoleMgr
	roles  = RoleMgr.RoleName_Roles.get(roleName)
	if not roles:
		return None
	return list(roles)[0]


def GetRoleByIP(ip):
	'''
	根据IP地址获取角色对象
	@param roleID:
	'''
	import cRoleMgr
	for role in cRoleMgr.GetAllRole():
		if role.RemoteEndPoint() == ip:
			return role
	return None


if "_HasLoad" not in dir():
	cComplexServer.RegDistribute(PyMessage.GM_Request, OnGMRequest)
