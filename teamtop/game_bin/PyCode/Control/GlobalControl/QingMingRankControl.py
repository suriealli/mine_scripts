#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Control.GlobalControl.QingMingRankControl")
#===============================================================================
# 清明消费排行 control
#===============================================================================
import time
import datetime
import cDateTime
import cComplexServer
import DynamicPath
import Environment
from Util.File import TabFile
from Common.Message import PyMessage
from Common.Other import GlobalDataDefine, GlobalPrompt
from Control import ProcessMgr
from ComplexServer.Plug.Control import ControlProxy
from ComplexServer.API import GlobalHttp
from ComplexServer.Log import AutoLog
from Game.Role.Mail import EnumMail

if "_HasLoad" not in dir():
	RankCache_1 = []
	RankCache_2 = []
	RankCache_3 = []
	RankCache_4 = []
	RankCache_5 = []
	
	RankCache_old_1 = []
	RankCache_old_2 = []
	RankCache_old_3 = []
	RankCache_old_4 = []
	RankCache_old_5 = []
	
	#逻辑进程排行榜缓存数据{服务器区域类型 : {服务器Id: 前30名数据列表}}
	LoginRankAll_Dict = {1 : {}, 2 : {}, 3 : {}, 4 : {}, 5:{}}
	
	#总共的逻辑进程
	TotalLogicCnt = 0
	
	#逻辑进程区域类型
	LogicType_Dict = {}
	
	#数据载入是否成功
	ReturnDB = False
	ReturnIndexset = set()
	
	IS_START = False
	
	CFILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	CFILE_FOLDER_PATH.AppendPath("CircularActive")
	
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("QingMing")
	
	#魅力排行 排行版奖励字典  {(index,serverType):QingMingKuaFuRankConfig,}
	QingMingKuaFuRank_Dict = {}
	#区间对应的排行榜奖励索引 {rankInterval:index,} 
	QingMingKuaFuRankToIndex_Dict = {}
	
class QingMingRankActiveConfig(TabFile.TabLine):
	FilePath = CFILE_FOLDER_PATH.FilePath("QingMingRankActive.txt")
	def __init__(self):
		self.activeName = str
		self.startTime = self.GetDatetimeByString
		self.endTime = self.GetDatetimeByString
	
	def init_active(self):
		#当前日期时间
		nowDate = cDateTime.Now()
		#开始时间戳
		beginTime = int(time.mktime((self.startTime).timetuple()))
		#结束时间戳
		endTime = int(time.mktime((self.endTime).timetuple()))
		#当前时间戳
		nowTime = int(time.mktime(datetime.datetime(cDateTime.Year(), cDateTime.Month(), cDateTime.Day(), cDateTime.Hour(), cDateTime.Minute(), cDateTime.Second()).timetuple()))
		
		if self.startTime <= nowDate < self.endTime:
			#在开始和结束时间戳之间, 激活
			OpenQingMingRank(None, endTime)
			cComplexServer.RegTick(endTime - nowTime + 60, CloseQingMingRank)
		elif nowDate < self.startTime:
			#在开始时间戳之前
			cComplexServer.RegTick(beginTime - nowTime, OpenQingMingRank, endTime)
			cComplexServer.RegTick(endTime - nowTime + 60, CloseQingMingRank)

def LoadQingMingRankActiveConfig():
	for cfg in QingMingRankActiveConfig.ToClassType(False):
		if cfg.startTime > cfg.endTime:
			print "GE_EXC, startTime > endTime in QingMingRankActive"
			return
		cfg.init_active()
		
class QingMingKuaFuRankConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("QingMingKuaFuRank.txt")
	def __init__(self):
		self.index = int					#排名奖励索引
		self.rankInterval = eval			#排名区间
		self.serverType = int				#服务器类型
		self.needValue = int				#占位最低消费值
		self.reward = eval					#奖励
	
def LoadQingMingKuaFuRankConfig():
	global QingMingKuaFuRank_Dict
	global QingMingKuaFuRankToIndex_Dict
	
	for cfg in QingMingKuaFuRankConfig.ToClassType(False):
		if (cfg.index, cfg.serverType) in QingMingKuaFuRank_Dict:
			print "GE_EXC, repeat (index : %s, serverType : %s) in QingMingKuaFuRank_Dict" % (cfg.index, cfg.serverType)
			continue
		#排名区间 -- > 排名索引
		if cfg.rankInterval not in QingMingKuaFuRankToIndex_Dict:
			QingMingKuaFuRankToIndex_Dict[cfg.rankInterval] = cfg.index
		QingMingKuaFuRank_Dict[(cfg.index, cfg.serverType)] = cfg

def GetRankCfgByRankAndType(rank, serverType):
	'''
	返回排名rank对应的排名index
	'''
	retIndex = 0
	for rankInterval, index in QingMingKuaFuRankToIndex_Dict.iteritems():
		rankDown , rankUp = rankInterval
		if rankDown <= rank and rank <= rankUp:
			retIndex = index
	
	rankCfg = QingMingKuaFuRank_Dict.get((retIndex,serverType))
	return rankCfg
	
def OpenQingMingRank(callArgv, regparam):
	#开启魅力排行
	global IS_START
	if IS_START:
		print "GE_EXC, QingMingRank is already open"
		return
	IS_START = True

def CloseQingMingRank(callArgv, regparam):
	#结束魅力排行
	global IS_START
	if not IS_START:
		print "GE_EXC, QingMingRank is already close"
		return
	
	#清理排行榜数据
	global RankCache_1, RankCache_2, RankCache_3, RankCache_4, RankCache_5
	RankCache_1, RankCache_2, RankCache_3, RankCache_4, RankCache_5 = [], [], [], [], []
	global RankCache_old_1, RankCache_old_2, RankCache_old_3, RankCache_old_4, RankCache_old_5
	RankCache_old_1, RankCache_old_2, RankCache_old_3, RankCache_old_4, RankCache_old_5 = [], [], [], [], []
	
	global LoginRankAll_Dict, LogicType_Dict
	#清理逻辑进程排行榜缓存数据{服务器区域类型 : {服务器Id: 前30名数据列表}}
	LoginRankAll_Dict = {1 : {}, 2 : {}, 3 : {}, 4 : {}, 5 : {}}
	#清理逻辑进程区域类型
	LogicType_Dict = {}
	
	IS_START = False

def AfterNewMinute():
	'''
	'''
	if not IS_START:
		#活动没有开启
		return
	
	nowMinute = cDateTime.Minute()
	nowHour = cDateTime.Hour()
	
	if nowMinute not in (0, 30, 58):
		#0, 30, 58这三个时间点可能触发向逻辑进程请求数据
		return
	if nowMinute == 58 and nowHour != 23:
		#58分的时候只有是23点才会向逻辑进程请求数据
		return
	
	global ReturnDB
	if ReturnDB is False:
		print "GE_EXC, QingMingRankControl AfterNewHour error not ReturnDB"
		#数据没有载回, 尝试再次载入
		InitGetRankEx()
		return
	
	if nowHour == 0 and nowMinute == 0:
		#0点0分的时候只发奖，操作数据库数据，逻辑进程自己把今天的数据拷贝到“昨天”的数据里面
		NewDayRewardRoles()
	else:
		#向逻辑进程请求数据,并且进行排序，写入数据库，把最新的排序更新到逻辑进程
		RequestLogicRank()

def RequestLogicRank():
	#向所有的逻辑进程获取排行榜数据
	global TotalLogicCnt
	TotalLogicCnt = len(ProcessMgr.ControlProcesssSessions)
	for sessionid, cp in ProcessMgr.ControlProcesssSessions.iteritems():
		if cp.processid >= 30000:
			#跨服服务器不处理
			TotalLogicCnt -= 1
			continue
		ControlProxy.SendLogicMsgAndBack(sessionid, PyMessage.Control_RequestLogicQingMingRank, None, LogicBackRank, sessionid)


def LogicBackRank(callargv, regparam):
	#逻辑进程返回或者自返回
	global TotalLogicCnt
	TotalLogicCnt -= 1
	if callargv:
		global LogicType_Dict, LoginRankAll_Dict
		processId, serverType, logicranklist = callargv
		LogicType_Dict[processId] = serverType
		rankDict = LoginRankAll_Dict.get(serverType)
		if not rankDict:
			LoginRankAll_Dict[serverType] = rankDict = {} 
		rankDict[processId] = logicranklist

	if TotalLogicCnt == 0:
		#所有的逻辑进程已经返回了排行榜,对排行榜进行排序,然后更新到数据库
		SortAndUpdataRank()
	elif TotalLogicCnt < 0:
		print "GE_EXC, error in QingMingRankControl RequestBack (%s)" % TotalLogicCnt
	
def SortAndUpdataRank():
	#更新数据库中的排行榜数据
	global RankCache_1, RankCache_2, RankCache_3, RankCache_4, RankCache_5
	days = cDateTime.Days()
	RankCache_1 = []
	ranDict = LoginRankAll_Dict.get(1, {})
	for l in ranDict.values():
		RankCache_1.extend(l)
		
	if RankCache_1:
		RankCache_1.sort(key = lambda it:(it[0], it[1]), reverse = True)
		RankCache_1 = RankCache_1[:100]
		GlobalHttp.SetGlobalData(GlobalDataDefine.QingMingRankDataKey_1, (days, RankCache_1))

	RankCache_2 = []
	ranDict = LoginRankAll_Dict.get(2, {})
	for l in ranDict.values():
		RankCache_2.extend(l)
	if RankCache_2:
		RankCache_2.sort(key = lambda it:(it[0], it[1]), reverse = True)
		RankCache_2 = RankCache_2[:100]
		GlobalHttp.SetGlobalData(GlobalDataDefine.QingMingRankDataKey_2, (days, RankCache_2))

	RankCache_3 = []
	ranDict = LoginRankAll_Dict.get(3, {})
	for l in ranDict.values():
		RankCache_3.extend(l)
	if RankCache_3:
		RankCache_3.sort(key = lambda it:(it[0], it[1]), reverse = True)
		RankCache_3 = RankCache_3[:100]
		GlobalHttp.SetGlobalData(GlobalDataDefine.QingMingRankDataKey_3, (days, RankCache_3))
	
	RankCache_4 = []
	ranDict = LoginRankAll_Dict.get(4, {})
	for l in ranDict.values():
		RankCache_4.extend(l)
	if RankCache_4:
		RankCache_4.sort(key = lambda it:(it[0], it[1]), reverse = True)
		RankCache_4 = RankCache_4[:100]
		GlobalHttp.SetGlobalData(GlobalDataDefine.QingMingRankDataKey_4, (days, RankCache_4))
		
	RankCache_5 = []
	ranDict = LoginRankAll_Dict.get(5, {})
	for l in ranDict.values():
		RankCache_5.extend(l)
		
	if RankCache_5:
		RankCache_5.sort(key = lambda it:(it[0], it[1]), reverse = True)
		RankCache_5 = RankCache_5[:100]
		GlobalHttp.SetGlobalData(GlobalDataDefine.QingMingRankDataKey_5, (days, RankCache_5))
	
	#同步数据给所有的逻辑进程(当天数据)
	SyncAllLoginToday()

def NewDayRewardRoles():
	#发邮件对排行榜上面的玩家发奖
	global LoginRankAll_Dict
	#清理一天的排行榜缓存
	LoginRankAll_Dict =  {1 : {}, 2 : {}, 3 : {}, 4 : {}, 5: {}}
	global RankCache_1, RankCache_2, RankCache_3, RankCache_4, RankCache_5
	global RankCache_old_1, RankCache_old_2, RankCache_old_3, RankCache_old_4, RankCache_old_5
	
	#替换昨天的跨服排行榜
	RankCache_old_1 = RankCache_1
	RankCache_old_2 = RankCache_2
	RankCache_old_3 = RankCache_3
	RankCache_old_4 = RankCache_4
	RankCache_old_5 = RankCache_5
	
	#清理今天的跨服排行榜
	RankCache_1 = []
	RankCache_2 = []
	RankCache_3 = []
	RankCache_4 = []
	RankCache_5 = []
	
	days = cDateTime.Days()
	
	#更新跨服数据到数据库中
	GlobalHttp.SetGlobalData(GlobalDataDefine.QingMingRankDataKey_old_1, (days - 1, RankCache_old_1))
	GlobalHttp.SetGlobalData(GlobalDataDefine.QingMingRankDataKey_old_2, (days - 1, RankCache_old_2))
	GlobalHttp.SetGlobalData(GlobalDataDefine.QingMingRankDataKey_old_3, (days - 1, RankCache_old_3))
	GlobalHttp.SetGlobalData(GlobalDataDefine.QingMingRankDataKey_old_4, (days - 1, RankCache_old_4))
	GlobalHttp.SetGlobalData(GlobalDataDefine.QingMingRankDataKey_old_5, (days - 1, RankCache_old_5))
	
	GlobalHttp.SetGlobalData(GlobalDataDefine.QingMingRankDataKey_1, (days, RankCache_1))
	GlobalHttp.SetGlobalData(GlobalDataDefine.QingMingRankDataKey_2, (days, RankCache_2))
	GlobalHttp.SetGlobalData(GlobalDataDefine.QingMingRankDataKey_3, (days, RankCache_3))
	GlobalHttp.SetGlobalData(GlobalDataDefine.QingMingRankDataKey_4, (days, RankCache_4))
	GlobalHttp.SetGlobalData(GlobalDataDefine.QingMingRankDataKey_5, (days, RankCache_5))
	
	#第一区域服务器
	RewardRolesByServerType(RankCache_old_1, 1)
	
	#第二区域服务器
	RewardRolesByServerType(RankCache_old_2, 2)
	
	#第三区域服务器
	RewardRolesByServerType(RankCache_old_3, 3)
	
	#第四区域服务器
	RewardRolesByServerType(RankCache_old_4, 4)
	
	#第五区域服务器
	RewardRolesByServerType(RankCache_old_5, 5)
	
def RewardRolesByServerType(rankData, serverType):
	'''
	根据排行数据 和 服务器类型 结算
	'''
	tmpRankDict = {}	#{roleId:rank}
	tmpRank = 1			#初始排名
	maxRankLen = 100	#排行榜最大个数
	
	for rank in rankData:
		if tmpRank > maxRankLen:
			#超过排行榜最大个数了
			continue
		
		#先拿到当前排名需要的积分配置
		cfg = GetRankCfgByRankAndType(tmpRank, serverType)
		if not cfg:
			print 'GE_EXC, QingMingRankControl RewardRolesByServerType::AfterNewHour can not find rank %s cfg' % tmpRank
			continue
		
		while rank[0] < cfg.needValue:
			#如果当前的积分小于需要的积分, 排名往后加
			tmpRank += 1
			if tmpRank > maxRankLen:
				break
			#获取下一个排名的配置
			cfg = GetRankCfgByRankAndType(tmpRank, serverType)
			if not cfg:
				print 'GE_EXC, QingMingRankControl RewardRolesByServerType::AfterNewHour can not find rank %s cfg' % tmpRank
				continue
		
		if tmpRank > maxRankLen:
			#跳出for循环
			break
		
		if rank[0] < cfg.needValue:
			print 'GE_EXC,QingMingRankControl RewardRolesByServerType:: AfterNewHour error'
			continue
		
		tmpRankDict[rank[1]] = tmpRank
		#完了排名+1
		tmpRank += 1
	
	maildatas = []	
	transaction = AutoLog.traQingMingRankMailReward
	for roleid, rank in tmpRankDict.iteritems():
		rolemaildata = (roleid, GlobalPrompt.QingMingRank_Title, GlobalPrompt.QingMingRank_Sender, GlobalPrompt.QingMingRank_Content % rank, transaction, GetRankMailReward(rank, serverType))
		maildatas.append(rolemaildata)
	#发送邮件奖励
	GlobalHttp.SendRoleMail(maildatas)
	
def GetRankMailReward(rank, serverType):
	#组合一个邮件奖励字典
	mailData = {}
	
	#排名 --> 排名区间 --> 奖励索引
	global QingMingKuaFuRankToIndex_Dict
	index = 0
	for (begin, end), rewardIndex in QingMingKuaFuRankToIndex_Dict.iteritems():
		if (begin == end) and (rank == begin):
			#begin == end
			index = rewardIndex
			break
		elif (begin != end) and (begin <= rank <= end):
			#begin != end
			index = rewardIndex
			break
	else:
		print "GE_EXC, QingMingRankControl GetRankMailReward can not find index by rank (%s)" % rank
		return
	
	#(奖励索引, 服务器类型) --> 奖励
	cfg = QingMingKuaFuRank_Dict.get((index, serverType))
	if not cfg:
		print "GE_EXC, QingMingRankControl GetRankMailReward can not find reward by rank (%s) serverType (%s)" % (rank, serverType)
		return
	
	#目前只有物品奖励
	if cfg.reward:
		mailData[EnumMail.EnumItemsKey] = cfg.reward
	return mailData
###############################################################################
def InitGetRankEx():
	index = 1
	key = GlobalDataDefine.QingMingRankDataKey_1
	oldkey = GlobalDataDefine.QingMingRankDataKey_old_1
	GlobalHttp.GetGlobalDataByKeys([key, oldkey], OnGetRankBackEx, (index, key, oldkey))
	
	index = 2
	key = GlobalDataDefine.QingMingRankDataKey_2
	oldkey = GlobalDataDefine.QingMingRankDataKey_old_2
	GlobalHttp.GetGlobalDataByKeys([key, oldkey], OnGetRankBackEx, (index, key, oldkey))

	index = 3
	key = GlobalDataDefine.QingMingRankDataKey_3
	oldkey = GlobalDataDefine.QingMingRankDataKey_old_3
	GlobalHttp.GetGlobalDataByKeys([key, oldkey], OnGetRankBackEx, (index, key, oldkey))

	index = 4
	key = GlobalDataDefine.QingMingRankDataKey_4
	oldkey = GlobalDataDefine.QingMingRankDataKey_old_4
	GlobalHttp.GetGlobalDataByKeys([key, oldkey], OnGetRankBackEx, (index, key, oldkey))

	index = 5
	key = GlobalDataDefine.QingMingRankDataKey_5
	oldkey = GlobalDataDefine.QingMingRankDataKey_old_5
	GlobalHttp.GetGlobalDataByKeys([key, oldkey], OnGetRankBackEx, (index, key, oldkey))


def OnGetRankBackEx(response, regparam):
	#数据返回了
	if response is None:
		#自返回
		return
	
	index, key, oldkey = regparam
	
	#分析和处理数据
	datadict = response
	days = cDateTime.Days()
	Checkdata(datadict, index, days, key, oldkey)
	
	global ReturnIndexset
	ReturnIndexset.add(index)

	#已经载入成功了
	global ReturnDB
	if len(ReturnIndexset) >= 5:
		ReturnDB = True
		#同步数据给所有的逻辑进程
		SyncAllLogin()

def SetRankData(pType, nowRank, oldRank):
	#设置缓存数据
	global RankCache_1, RankCache_2, RankCache_3, RankCache_4, RankCache_5
	global RankCache_old_1, RankCache_old_2, RankCache_old_3, RankCache_old_4, RankCache_old_5
	
	#重新排序
	nowRank.sort(key = lambda it:it[0], reverse = True)
	oldRank.sort(key = lambda it:it[0], reverse = True)
	
	if pType == 1:
		RankCache_1 = nowRank
		RankCache_old_1 = oldRank
	elif pType == 2:
		RankCache_2 = nowRank
		RankCache_old_2 = oldRank
	elif pType == 3:
		RankCache_3 = nowRank
		RankCache_old_3 = oldRank
	elif pType == 4:
		RankCache_4 = nowRank
		RankCache_old_4 = oldRank
	elif pType == 5:
		RankCache_5 = nowRank
		RankCache_old_5 = oldRank
		
	
def Checkdata(datadict, pType, nowdays, nowKey, oldKey):
	#检查和分析数据库返回的数据
	nowRank = []
	oldRank = []
	data = datadict.get(nowKey)
	olddata = datadict.get(oldKey)

	if data:
		d, rankdata = data
		if d == nowdays:
			#确定是今天的数据
			nowRank = rankdata
		elif d > nowdays:
			#天数有问题
			if not Environment.IsDevelop:
				print "GE_EXC, QingMingRankControl day error in OnGetRankBack"
			return
		elif d == nowdays - 1:
			#昨天的数据？
			oldRank = rankdata
			#数据库里面的数据有点旧了，更新一下
			GlobalHttp.SetGlobalData(nowKey, (nowdays, []))
			GlobalHttp.SetGlobalData(oldKey, (nowdays - 1, oldRank))
			#设置当前缓存数据
			SetRankData(pType, [], oldRank)
			return
		else:
			# 已经相差2天了，清理数据?
			GlobalHttp.SetGlobalData(nowKey, (nowdays, []))
			GlobalHttp.SetGlobalData(oldKey, (nowdays - 1, []))
			return

	if olddata:
		oldday, oldrankdata = olddata
		if oldday == nowdays - 1:
			#天数准确
			oldRank = oldrankdata
		elif oldday >= nowdays:
			if not Environment.IsDevelop:
				print "GE_EXC,QingMingRankControl old day error in OnGetRankBack"
		else:
			#旧数据太旧了，直接清理
			GlobalHttp.SetGlobalData(oldKey, (nowdays - 1, []))
	SetRankData(pType, nowRank, oldRank)

def SyncAllLogin():
	#同步数据给所有的逻辑进程(今天和昨天)
	global LogicType_Dict
	for processId, pType in LogicType_Dict.iteritems():
		cp = ProcessMgr.ControlProcesssIds.get(processId)
		if not cp:
			if not Environment.IsDevelop:
				print "GE_EXC, QingMingRankControl SyncAllLogin not process sessionid (%s)" % processId
			continue
		sessionid = cp.session_id
		if pType == 1:
			ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdataQingMingRankToLogic, (RankCache_1, RankCache_old_1))
		elif pType == 2:
			ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdataQingMingRankToLogic, (RankCache_2, RankCache_old_2))
		elif pType == 3:
			ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdataQingMingRankToLogic, (RankCache_3, RankCache_old_3))
		elif pType == 4:
			ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdataQingMingRankToLogic, (RankCache_4, RankCache_old_4))
		elif pType == 5:
			ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdataQingMingRankToLogic, (RankCache_5, RankCache_old_5))
		else:
			print "GE_EXC, QingMingRankControl SyncAllLogin error pType (%s)" % pType

def SyncAllLoginToday():
	#同步当天最新的排行榜给所有的逻辑进程
	global LogicType_Dict
	for processId, pType in LogicType_Dict.iteritems():
		cp = ProcessMgr.ControlProcesssIds.get(processId)
		if not cp:
			if not Environment.IsDevelop:
				print "GE_EXC, QingMingRankControl SyncAllLoginToday not process sessionid (%s)" % processId
			continue
		sessionid = cp.session_id
		if pType == 1:
			ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdataQingMingRankToLogic_T, RankCache_1)
		elif pType == 2:
			ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdataQingMingRankToLogic_T, RankCache_2)
		elif pType == 3:
			ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdataQingMingRankToLogic_T, RankCache_3)
		elif pType == 4:
			ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdataQingMingRankToLogic_T, RankCache_4)
		elif pType == 5:
			ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdataQingMingRankToLogic_T, RankCache_5)
		else:
			print "GE_EXC,QingMingRankControl SyncAllLogin error pType (%s)" % pType

def LoginRequestRank(sessionid, msg):
	'''
	#逻辑进程主动请求跨服排行榜数据
	@param sessionid:
	@param msg:(进程ID， 进程区域类型)
	'''
	global ReturnDB,  LogicType_Dict
	#先记录逻辑进程的区域类型
	processId, pType, rank = msg
	LoginRankAll_Dict[pType][processId] =  rank
	
	LogicType_Dict[processId] = pType
	
	if not ReturnDB:
		#控制进程当前还没有从DB载回数据，等待数据载回来再发过去
		return

	#根据类型发送数据
	if pType == 1:
		ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdataQingMingRankToLogic, (RankCache_1, RankCache_old_1))
	elif pType == 2:
		ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdataQingMingRankToLogic, (RankCache_2, RankCache_old_2))
	elif pType == 3:
		ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdataQingMingRankToLogic, (RankCache_3, RankCache_old_3))
	elif pType == 4:
		ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdataQingMingRankToLogic, (RankCache_4, RankCache_old_4))
	elif pType == 5:
		ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdataQingMingRankToLogic, (RankCache_5, RankCache_old_5))
	else:
		print "GE_EXC, QingMingRankControl error pType (%s) in LoginRequestRank" % pType

if "_HasLoad" not in dir():
	if Environment.HasControl:
		LoadQingMingRankActiveConfig()
		LoadQingMingKuaFuRankConfig()
		InitGetRankEx()
		
		cComplexServer.RegAfterNewMinuteCallFunction(AfterNewMinute)
		cComplexServer.RegDistribute(PyMessage.Control_GetQingMingRank, LoginRequestRank)