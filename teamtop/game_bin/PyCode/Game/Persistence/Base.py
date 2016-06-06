#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Persistence.Base")
#===============================================================================
# 持久化数据基类
#===============================================================================
import datetime
import cProcess
import cDateTime
import cComplexServer
import Environment
from Common import Define
from ComplexServer import Init
from ComplexServer.Plug.DB import DBProxy
from Game.Persistence import SerialLoad
import cNetMessage

if "_HasLoad" not in dir():
	KeyDict = {}
	AllLoadReturn = False


def DataToMd5(data):
	cNetMessage.PackPyMsg(1, data)
	msg_string = cNetMessage.MsgToString()
	sun = 0
	xor = 0
	for c in msg_string:
		v = ord(c)
		sun += v
		xor ^= v
	return 2 ** 32 * sun + 2 ** 24 * xor + len(msg_string)

def CheckAllLoadReturn():
	global AllLoadReturn
	for d in KeyDict.itervalues():
		if d.returnDB is False:
			AllLoadReturn = False
			return False
	AllLoadReturn = True
	return True

def ForceLoadPersistence():
	for d in KeyDict.itervalues():
		if d.returnDB is False:
			d.LoadData()


def AsDatetime(arg):
	'''
	转化为datetime.datetime对象
	@param arg:参数
	'''
	if type(arg) == datetime.datetime:
		return arg
	else:
		return datetime.datetime(*arg)

class ObjBase(object):
	# 默认值的创建函数
	defualt_data_create = lambda : None
	def __init__(self, key, deadTime = (2038, 1, 1), afterLoadFun = None, beforeSaveFun = None, isSaveBig = True):
		# 过期了就不载入数据了
		if cDateTime.Now() > AsDatetime(deadTime):
			return
		# 确保Key唯一
		if key in KeyDict:
			print "GE_EXC, repeat persistence data key(%s)" % key
			return
		KeyDict[key] = self
		# 初始化数据
		self.key = key
		self.info = {}
		self.data = self.defualt_data_create()
		self.isSaveBig = isSaveBig
		# 初始化标识位
		self.returnDB = False
		self.changeFlag = False
		self.loadCount = 0
		self.afterLoadFun = afterLoadFun
		self.beforeSaveFun = beforeSaveFun
		
		self.data_md5 = None
		# Web环境，不载入数据
		if Environment.HasWeb:
			return
		# 只有逻辑插件，才载入数据
		if not Environment.HasLogic:
			print "GE_EXC, create persistence data(%s) without logic." % key
			return
		# 注意，这样要三注册以解决服务端进程启动先后的问题
		Init.InitCallBack.RegCallbackFunction(self.OnInit)
		DBProxy.ConnectDBServerCallBack.RegCallbackFunction(self.OnConnectDBServer)
		cComplexServer.RegTick(10, self.OnTime)
		# 注册前保存数据【每隔一定时间、服务器关闭前】
		cComplexServer.RegSaveCallFunction2(self.SaveData)
	
	def OnInit(self):
		'''
		当初始化脚本后
		'''
		if self.loadCount:
			return
		self.LoadData()
	
	def OnConnectDBServer(self, sessionid, dbid, ip, port):
		'''
		当连接上DBServer了
		'''
		# 不是主DBServer连接，不要载入数据
		if dbid != cProcess.ProcessID:
			return
		if self.loadCount:
			return
		self.LoadData()
	
	def OnTime(self, callargv, regparam):
		'''
		当启动一段时间了
		'''
		if self.loadCount:
			return
		self.LoadData()
	
	def LoadData(self, is_request = False):
		'''
		载入数据
		'''
		# DB还不能访问
		if not DBProxy.CanDBVisit(cProcess.ProcessID):
			return
		# 已经载入过了，不要重复载入（这种情况出现在服务器之间断线重连下的时候）
		if self.returnDB:
			return
		if (not is_request) and Define.SERIAL_LOAD:
			SerialLoad.request_load_persistence_data(self.key)
			return
		self.loadCount += 1
		DBProxy.WAIT_TIME = 600
		DBProxy.DBVisit(cProcess.ProcessID, 0, "LoadPerData", self.key, self.OnReturnFromDB, self.loadCount)
		DBProxy.WAIT_TIME = 60
	
	def OnReturnFromDB(self, result, regparam):
		'''
		当数据返回了
		@param result:返回结果
		@param regparam:注册参数
		'''
		# 如果载入的次数不是当前等待的载入次数，则忽视之
		if self.loadCount != regparam:
			print "GE_EXC, persistence(%s) loadCount(%s) != regparam(%s)" % (self.key, self.loadCount, regparam)
			return
		# 注意，鉴于服务器启动时不一定能够从服务器载入数据，这里一定要先判断自返回的情况
		if result is None:
			print "GE_EXC, persistence(%s) LoadData result is None" % self.key
			if self.loadCount < 4:
				#如果前面3次没载入成功，自返回的时候马上再尝试载入
				self.LoadData()
			return
		# 如果数据库中没数据，则result是(None, None), 否则解析数据之
		if result[0] is not None:
			self.info, self.data = result
		else:
			#生成一份在数据库里面
			self.changeFlag = True
		# 此时标记的确从数据库返回了
		self.returnDB = True
		CheckAllLoadReturn()
		if Define.SERIAL_LOAD:
			SerialLoad.success_load_persistence_data(self.key)
		# 如果有回调函数，调用之
		if self.afterLoadFun:
			self.afterLoadFun()
		
		#内网检查数据正确性
		if Environment.IsWindows:
			self.data_md5 = DataToMd5(self.data)
		
	def SaveData(self):
		'''
		保存数据
		'''
		# 如果没有载入回来，并且尝试载入次数小于10次，则再次载入
		if self.returnDB is False:
			if 3 < self.loadCount < 10:
				print "GE_EXC, reload persistence(%s) %s times" % (self.key, self.loadCount)
				self.LoadData()
			return
		# 没有改变过，就不要保存了
		if not self.changeFlag:
			if Environment.IsWindows:
				if self.data_md5 != DataToMd5(self.data):
					#flag没变，但是数据发生了改变，有地方没有设置haschange
					print "GE_EXC, (%s) persistence data error haschange forget" % self.key
			return
		if self.beforeSaveFun:
			self.beforeSaveFun()
		self._SaveDataToDB()
		self.changeFlag = False
		if Environment.IsWindows:
			self.data_md5 = DataToMd5(self.data)
	
	def _SaveDataToDB(self):
		#默认是存储大数据方式
		if self.isSaveBig is True:
			self.SaveBig()
		else:
			self.SaveNormal()
	
	def SaveBig(self):
		#大数据存储方式
		DBProxy.DBBigVisit(cProcess.ProcessID, None, "SavePerData", (self.key, self.info, self.data))
	
	def SaveNormal(self):
		#正常存储方式
		DBProxy.DBVisit(cProcess.ProcessID, None, "SavePerData", (self.key, self.info, self.data))
	
	
	def SetData(self, data):
		'''
		设置数据
		@param data:数据
		'''
		assert self.returnDB
		self.data = data
		self.changeFlag = True
	
	def GetData(self):
		'''
		获取数据
		'''
		assert self.returnDB
		return self.data
	
	def HasChange(self):
		self.changeFlag = True
