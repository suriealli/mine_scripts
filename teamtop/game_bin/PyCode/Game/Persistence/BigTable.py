#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Persistence.BigTable")
#===============================================================================
# 大表
#===============================================================================
import cProcess
import cDateTime
import cComplexServer
import Environment
from Common import Define
from ComplexServer import Init
from ComplexServer.Plug.DB import DBProxy, SystemTable
from Game.Persistence import SerialLoad, Base

if "_HasLoad" not in dir():
	ALL_TABLES = {}
	AllLoadReturn = False


def CheckAllLoadReturn():
	global AllLoadReturn
	for bt in ALL_TABLES.itervalues():
		if bt.returnDB is False:
			AllLoadReturn = False
			return False
	AllLoadReturn = True
	return True

def ForceLoadPersistence():
	for bt in ALL_TABLES.itervalues():
		if bt.returnDB is False:
			bt.LoadData()




class BigTable(object):
	def __init__(self, name, maxLine, afterLoadFun):
		# 确保名字唯一
		if name in ALL_TABLES:
			print "GE_EXC, repeat big table name(%s)" % name
			return
		ALL_TABLES[name] = self
		self.name = name
		# Web环境，不载入数据
		if Environment.HasWeb:
			return
		# 非逻辑插件，不载入
		if not Environment.HasLogic:
			print "GE_EXC, create big table(%s) without logic" % name
			return
		self.name = name
		# 每一次载入的行数
		self.maxLine = maxLine
		self.afterLoadFun = afterLoadFun
		# 获取主键
		self.pri = SystemTable.GetPRIByName(name)
		table = SystemTable.GetTableByName(name)
		# 表中字段不能是自增长的
		assert not table.HasAutoIncrement()
		# 表中必须有主键
		assert self.pri
		# 注意这里一定要list
		self.columns = table.GetColumnNames()
		# 计算传输频道
		self.channel = len(ALL_TABLES)
		# 设置未返回数据
		self.returnDB = False
		self.loadCount = 0
		# 返回的数据
		self.datas = {}
		# 改变过的Key
		self.changes = set()
		# 删除过的Key
		self.deletes = set()
		
		self.data_md = {}
		# 注意，这样要三注册以解决服务端进程启动先后的问题
		self.has_connect = False
		Init.InitCallBack.RegCallbackFunction(self.OnInit)
		DBProxy.ConnectDBServerCallBack.RegCallbackFunction(self.OnConnectDBServer)
		cComplexServer.RegTick(10, self.OnTime)
		# 注册前保存数据【每隔一定时间、服务器关闭前】 20分钟一次
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
		@param keys:主键列表
		'''
		# DB还不能访问
		if not DBProxy.CanDBVisit(cProcess.ProcessID):
			return
		# 已经载入过了，不要重复载入（这种情况出现在服务器之间断线重连下的时候）
		if self.returnDB:
			return
		if (not is_request) and Define.SERIAL_LOAD:
			SerialLoad.request_load_big_table(self.name)
			return
		self.loadCount += 1
		# 开始载入数据
		DBProxy.WAIT_TIME = 600
		# 主要，这里载入的时候指定0，串行载入
		DBProxy.DBVisit(cProcess.ProcessID, 0, "LoadBTData", self.name, self.OnLoadData, self.loadCount)
		DBProxy.WAIT_TIME = 60
	
	def OnLoadData(self, result, regparam):
		'''
		载入数据返回
		@param result:数据行
		@param regparam:载入次数
		'''
		# 如果载入的次数不是当前等待的载入次数，则忽视之
		if self.loadCount != regparam:
			print "GE_EXC, big table(%s) OnLoadData loadCount(%s) != regparam(%s)" % (self.name, self.loadCount, regparam)
			return
		if result is None:
			print "GE_EXC, big table (%s) OnLoadData result is None" % self.name
			if self.loadCount < 4:
				#如果前面3次没载入成功，自返回的时候马上再尝试载入
				self.LoadData()
			return
		# 获取表定义
		table = SystemTable.GetTableByName(self.name)
		# 获取主键索引
		keyIdx = table.GetColumnIndex(self.pri)
		# 获取列名列表
		names = table.GetColumnNames()
		# 遍历结果集
		SD = self.datas
		for row in result:
			# 获取主键
			key = row[keyIdx]
			# 构建索引字典
			value = {}
			for idx, name in enumerate(names):
				value[name] = row[idx]
			# 构建内存数据结构
			SD[key] = value
		# 标记载入完成
		self.returnDB = True
		CheckAllLoadReturn()
		if Define.SERIAL_LOAD:
			SerialLoad.success_load_big_table(self.name)
		# 触发载入回调
		if self.afterLoadFun:
			self.afterLoadFun()
		print "BLUE, big table(%s) load data(%s) at %s" % (self.name, len(self.datas), cDateTime.Now())
		#====================================================
		#内网检查数据正确性
		if Environment.IsWindows:
			for key, value in self.datas.iteritems():
				self.data_md[key] = Base.DataToMd5(value)
		#====================================================
		
	def SaveData(self):
		'''
		持久化数据
		'''
		# 如果没有载入回来，并且尝试载入次数小于10次，则再次载入
		if self.returnDB is False:
			#前3次是载入时自返回的时候马上再次载入
			if 3 < self.loadCount < 10:
				print "GE_EXC, reload bigtable(%s) %s times" % (self.name, self.loadCount)
				self.LoadData()
			return
		# 通知数据库删除已经删除的部分
		if self.deletes:
			DBProxy.DBBigVisit(cProcess.ProcessID,  self.channel, "DelBTData", (self.name, self.deletes))
			#====================================================
			#内网检查数据正确性
			if Environment.IsWindows:
				for key in self.deletes:
					if key in self.data_md:
						del self.data_md[key]
			#====================================================
			
			self.deletes.clear()
		#====================================================
		#内网检查数据正确性
		if Environment.IsWindows:
			for key, value in self.datas.iteritems():
				now_md5 = Base.DataToMd5(value)
				if key in self.changes:
					self.data_md[key] = now_md5
					continue
				if self.data_md.get(key) != now_md5:
					print "GE_EXC, bigtable (%s)  key (%s) change but not set haschange " % (self.name, key)
		#====================================================
		
		# 通知数据库修改已经修改的部分（分段传输）
		if self.changes:
			self._SaveData(self.changes)
			self.changes.clear()
	
	def _SaveData(self, keys):
		'''
		修改一段主键数据
		@param keys:
		'''
		rows = []
		# 将字典形式还原成Tuple形式
		SDG = self.datas.get
		RSA = rows.append
		SC = self.columns
		for key in keys:
			value = SDG(key, None)
			if value is None:
				continue
			row = []
			RA = row.append
			for name in SC:
				RA(value[name])
			RSA(tuple(row))
		# 通知数据库修改
		DBProxy.DBBigVisit(cProcess.ProcessID, self.channel, "SaveBTData", (self.name, rows))
		
		
		
	def SetKeyValue(self, key, value):
		'''
		设置一个Key、Value对
		@param key:主键值
		@param value:一个字典，对于数据库中表的定义
		'''
		# 断言数据完整
		assert self.returnDB
		self.datas[key] = value
		self.deletes.discard(key)
		self.changes.add(key)
	
	def SetValue(self, value):
		'''
		设置一个Value
		@param value:一个字典，对于数据库中表的定义
		'''
		# 断言数据完整
		assert self.returnDB
		self.SetKeyValue(value[self.pri], value)
	
	def DelKey(self, key):
		'''
		删除一个Key
		@param key:主键值
		'''
		# 断言数据完整
		assert self.returnDB
		datas = self.datas
		if key in datas: del datas[key]
		self.changes.discard(key)
		self.deletes.add(key)
		
	
	def HasChangeKey(self, key):
		'''
		标记一个key改变了
		@param key:
		'''
		assert self.returnDB
		assert key not in self.deletes
		self.changes.add(key)
	
	
	def GetData(self):
		# 断言数据完整
		assert self.returnDB
		return self.datas
	
	def GetValue(self, key, defual = None):
		# 断言数据完整
		assert self.returnDB
		return self.datas.get(key, defual)

