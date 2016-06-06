#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Control.GlobalControl.BraveHeroControl")
#===============================================================================
# 勇者英雄坛控制模块
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
	LoginRankAll_Dict = {1 : {}, 2 : {}, 3 : {}, 4 : {}, 5 : {}}
	
	#总共的逻辑进程
	TotalLogicCnt = 0
	
	#逻辑进程区域类型
	LogicType_Dict = {}
	
	#数据载入是否成功
	ReturnDB = False
	ReturnIndexset = set()
	
	BraveHeroIsOpen = False
	
	CFILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	CFILE_FOLDER_PATH.AppendPath("CircularActive")
	
	BFILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	BFILE_FOLDER_PATH.AppendPath("BraveHero")
	
	#勇者英雄坛
	BraveHero_Dict = {}
	#勇者英雄坛排行榜字典 
	BraveHeroRank_Dict = {}
	#区间对应的排行榜奖励索引
	BraveHeroRankToIndex_Dict = {}
	
class BraveHeroActiveConfig(TabFile.TabLine):
	FilePath = CFILE_FOLDER_PATH.FilePath("BraveHeroActive.txt")
	def __init__(self):
		self.activeID = int					#活动ID
		self.beginTime = eval				#开始时间
		self.endTime = eval					#结束时间
	
	def Active(self):
		#当前时间
		nowDate = (cDateTime.Year(), cDateTime.Month(), cDateTime.Day(), cDateTime.Hour(), cDateTime.Minute(), cDateTime.Second())
		#开始时间戳
		beginTime = int(time.mktime(datetime.datetime(*self.beginTime).timetuple()))
		#结束时间戳
		endTime = int(time.mktime(datetime.datetime(*self.endTime).timetuple()))
		#当前时间戳
		nowTime = int(time.mktime(datetime.datetime(cDateTime.Year(), cDateTime.Month(), cDateTime.Day(), cDateTime.Hour(), cDateTime.Minute(), cDateTime.Second()).timetuple()))
		
		if self.beginTime <= nowDate < self.endTime:
			#在开始和结束时间戳之间, 激活
			OpenBraveHero(None, self.activeID)
			cComplexServer.RegTick(endTime - nowTime + 60, CloseBraveHero)
		elif nowDate < self.beginTime:
			#在开始时间戳之前
			cComplexServer.RegTick(beginTime - nowTime, OpenBraveHero, self.activeID)
			cComplexServer.RegTick(endTime - nowTime + 60, CloseBraveHero)
		
class BraveHeroRankConfig(TabFile.TabLine):
	FilePath = BFILE_FOLDER_PATH.FilePath("BraveHeroRank.txt")
	def __init__(self):
		self.index = int					#排名奖励索引
		self.rankInterval = eval			#排名区间
		self.serverType = int				#服务器类型
		self.reward = eval					#奖励
	
def LoadBraveHeroActiveConfig():
	global BraveHero_Dict
	
	for cfg in BraveHeroActiveConfig.ToClassType(False):
		if cfg.beginTime > cfg.endTime:
			print "GE_EXC, beginTime > endTime in BraveHeroActive"
			return
		BraveHero_Dict[cfg.activeID] = cfg
	
	BraveHeroActive()
	
def LoadBraveHeroRankConfig():
	global BraveHeroRank_Dict
	global BraveHeroRankToIndex_Dict
	
	for BHR in BraveHeroRankConfig.ToClassType(False):
		if (BHR.index, BHR.serverType) in BraveHeroRank_Dict:
			print "GE_EXC, repeat (index : %s, serverType : %s) in BraveHeroRank_Dict" % (BHR.index, BHR.serverType)
			continue
		#排名区间 -- > 排名索引
		if BHR.rankInterval not in BraveHeroRankToIndex_Dict:
			BraveHeroRankToIndex_Dict[BHR.rankInterval] = BHR.index
		BraveHeroRank_Dict[(BHR.index, BHR.serverType)] = BHR
	
def OpenBraveHero(callArgv, regparam):
	#开启勇者英雄坛
	global BraveHeroIsOpen
	if BraveHeroIsOpen:
		print "GE_EXC, BraveHero is already open"
		return
	BraveHeroIsOpen = True

def CloseBraveHero(callArgv, regparam):
	#结束勇者英雄坛
	global BraveHeroIsOpen
	if not BraveHeroIsOpen:
		print "GE_EXC, BraveHero is already close"
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
	
	BraveHeroIsOpen = False

def IsStart():
	#判断勇者英雄坛活动是否开启
	global BraveHeroIsOpen
	return BraveHeroIsOpen
	
def AfterNewHour():
	#每一个整点向所有的逻辑进程请求每一个服务器的前30名玩家数据，等待回调并且记录数据
	#如果有某些逻辑进程没有返回或者其他原因导致了这个回调是自回调的。这个时候，就会使用上一个小时
	#的旧数据代替这个一个服的数据。
	
	#所有的回调都完毕后，触发对这些玩家数据排序出前100名。并且http请求更新到数据库
	#（缺数据清理规则，数据中可能要存储天数的时间戳，清理天数 - 2 以后的数据 （因为是保存2天的数据））
	if not IsStart():
		#活动没有开启
		return
	
	nowHour = cDateTime.Hour()
	global ReturnDB
	if ReturnDB is False:
		print "GE_EXC, BraveHeroControl AfterNewHour error not ReturnDB"
		#数据没有载回, 尝试再次载入
		InitGetRankEx()
		return
	
	if nowHour == 0:
		#0点的时候只发奖，操作数据库数据，逻辑进程自己把今天的数据拷贝到“昨天”的数据里面
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
		ControlProxy.SendLogicMsgAndBack(sessionid, PyMessage.Control_RequestLogicBraveHeroRank, None, LogicBackRank, sessionid)


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
		print "GE_EXC, error in BraveHeroControl RequestBack (%s)" % TotalLogicCnt
	
def SortAndUpdataRank():
	#更新数据库中的排行榜数据
	global RankCache_1, RankCache_2, RankCache_3, RankCache_4, RankCache_5
	days = cDateTime.Days()
	RankCache_1 = []
	ranDict = LoginRankAll_Dict.get(1, {})
	for l in ranDict.values():
		RankCache_1.extend(l)
		
	if RankCache_1:
		RankCache_1.sort(key = lambda it:it[0], reverse = True)
		RankCache_1 = RankCache_1[:100]
		GlobalHttp.SetGlobalData(GlobalDataDefine.BraveHeroDataKey_1, (days, RankCache_1))

	RankCache_2 = []
	ranDict = LoginRankAll_Dict.get(2, {})
	for l in ranDict.values():
		RankCache_2.extend(l)
	if RankCache_2:
		RankCache_2.sort(key = lambda it:it[0], reverse = True)
		RankCache_2 = RankCache_2[:100]
		GlobalHttp.SetGlobalData(GlobalDataDefine.BraveHeroDataKey_2, (days, RankCache_2))

	RankCache_3 = []
	ranDict = LoginRankAll_Dict.get(3, {})
	for l in ranDict.values():
		RankCache_3.extend(l)
	if RankCache_3:
		RankCache_3.sort(key = lambda it:it[0], reverse = True)
		RankCache_3 = RankCache_3[:100]
		GlobalHttp.SetGlobalData(GlobalDataDefine.BraveHeroDataKey_3, (days, RankCache_3))
	
	RankCache_4 = []
	ranDict = LoginRankAll_Dict.get(4, {})
	for l in ranDict.values():
		RankCache_4.extend(l)
	if RankCache_4:
		RankCache_4.sort(key = lambda it:it[0], reverse = True)
		RankCache_4 = RankCache_4[:100]
		GlobalHttp.SetGlobalData(GlobalDataDefine.BraveHeroDataKey_4, (days, RankCache_4))
	
	RankCache_5 = []
	ranDict = LoginRankAll_Dict.get(5, {})
	for l in ranDict.values():
		RankCache_5.extend(l)
	if RankCache_5:
		RankCache_5.sort(key = lambda it:it[0], reverse = True)
		RankCache_5 = RankCache_5[:100]
		GlobalHttp.SetGlobalData(GlobalDataDefine.BraveHeroDataKey_5, (days, RankCache_5))
	
	#同步数据给所有的逻辑进程(当天数据)
	SyncAllLoginToday()

def NewDayRewardRoles():
	#发邮件对排行榜上面的玩家发奖
	global LoginRankAll_Dict
	#清理一天的排行榜缓存
	LoginRankAll_Dict =  {1 : {}, 2 : {}, 3 : {}, 4 : {}, 5 : {}}
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
	GlobalHttp.SetGlobalData(GlobalDataDefine.BraveHeroDataKey_old_1, (days - 1, RankCache_old_1))
	GlobalHttp.SetGlobalData(GlobalDataDefine.BraveHeroDataKey_old_2, (days - 1, RankCache_old_2))
	GlobalHttp.SetGlobalData(GlobalDataDefine.BraveHeroDataKey_old_3, (days - 1, RankCache_old_3))
	GlobalHttp.SetGlobalData(GlobalDataDefine.BraveHeroDataKey_old_4, (days - 1, RankCache_old_4))
	GlobalHttp.SetGlobalData(GlobalDataDefine.BraveHeroDataKey_old_5, (days - 1, RankCache_old_5))
	
	GlobalHttp.SetGlobalData(GlobalDataDefine.BraveHeroDataKey_1, (days, RankCache_1))
	GlobalHttp.SetGlobalData(GlobalDataDefine.BraveHeroDataKey_2, (days, RankCache_2))
	GlobalHttp.SetGlobalData(GlobalDataDefine.BraveHeroDataKey_3, (days, RankCache_3))
	GlobalHttp.SetGlobalData(GlobalDataDefine.BraveHeroDataKey_4, (days, RankCache_4))
	GlobalHttp.SetGlobalData(GlobalDataDefine.BraveHeroDataKey_5, (days, RankCache_5))
	
	#邮件奖励
	transaction = AutoLog.traBraveHeroMailReward
	
	#第一区域服务器
	maildatas = []
	for index, rd in enumerate(RankCache_old_1):
		rank = index + 1
		roleid = rd[1]
		rolemaildata = (roleid, GlobalPrompt.BraveHero_Title, GlobalPrompt.BraveHero_Sender, GlobalPrompt.BraveHero_Content % rank, transaction, GetRankMailReward(rank, 1))
		maildatas.append(rolemaildata)
	#发送邮件奖励
	GlobalHttp.SendRoleMail(maildatas)
	maildatas = []
	
	#第二区域服务器
	for index, rd in enumerate(RankCache_old_2):
		rank = index + 1
		roleid = rd[1]
		rolemaildata = (roleid, GlobalPrompt.BraveHero_Title, GlobalPrompt.BraveHero_Sender, GlobalPrompt.BraveHero_Content % rank, transaction, GetRankMailReward(rank, 2))
		maildatas.append(rolemaildata)
	#发送邮件奖励
	GlobalHttp.SendRoleMail(maildatas)
	maildatas = []
	
	#第三区域服务器
	for index, rd in enumerate(RankCache_old_3):
		rank = index + 1
		roleid = rd[1]
		rolemaildata = (roleid, GlobalPrompt.BraveHero_Title, GlobalPrompt.BraveHero_Sender, GlobalPrompt.BraveHero_Content % rank, transaction, GetRankMailReward(rank, 3))
		maildatas.append(rolemaildata)
	#发送邮件奖励
	GlobalHttp.SendRoleMail(maildatas)
	maildatas = []
	
	#第四区域服务器
	for index, rd in enumerate(RankCache_old_4):
		rank = index + 1
		roleid = rd[1]
		rolemaildata = (roleid, GlobalPrompt.BraveHero_Title, GlobalPrompt.BraveHero_Sender, GlobalPrompt.BraveHero_Content % rank, transaction, GetRankMailReward(rank, 4))
		maildatas.append(rolemaildata)
	#发送邮件奖励
	GlobalHttp.SendRoleMail(maildatas)
	maildatas = []
	
	#第五区域服务器
	for index, rd in enumerate(RankCache_old_5):
		rank = index + 1
		roleid = rd[1]
		rolemaildata = (roleid, GlobalPrompt.BraveHero_Title, GlobalPrompt.BraveHero_Sender, GlobalPrompt.BraveHero_Content % rank, transaction, GetRankMailReward(rank, 5))
		maildatas.append(rolemaildata)
	#发送邮件奖励
	GlobalHttp.SendRoleMail(maildatas)
	maildatas = []
	
	print 'BLUE, BraveHeroControl rank, region 1:%s, region 2:%s, region 3:%s, region 4:%s, region 5:%s' % (RankCache_old_1, RankCache_old_2, RankCache_old_3, RankCache_old_4, RankCache_old_5)
	
def GetRankMailReward(rank, serverType):
	#组合一个邮件奖励字典
	mailData = {}
	
	#排名 --> 排名区间 --> 奖励索引
	global BraveHeroRankToIndex_Dict
	index = 0
	for (begin, end), rewardIndex in BraveHeroRankToIndex_Dict.iteritems():
		if (begin == end) and (rank == begin):
			#begin == end
			index = rewardIndex
			break
		elif (begin != end) and (begin <= rank <= end):
			#begin != end
			index = rewardIndex
			break
	else:
		print "GE_EXC, GetRankMailReward can not find index by rank (%s)" % rank
		return
	
	#(奖励索引, 服务器类型) --> 奖励
	cfg = BraveHeroRank_Dict.get((index, serverType))
	if not cfg:
		print "GE_EXC, GetRankMailReward can not find reward by rank (%s) serverType (%s)" % (rank, serverType)
		return
	
	#目前只有物品奖励
	if cfg.reward:
		mailData[EnumMail.EnumItemsKey] = cfg.reward
	return mailData
###############################################################################
def InitGetRank():
	#向数据库请求载入排行榜数据
	#载入排行榜数据
	#----数据太大了，换成下面的那个----
	GlobalHttp.GetGlobalDataByKeys([GlobalDataDefine.BraveHeroDataKey_1, GlobalDataDefine.BraveHeroDataKey_2, GlobalDataDefine.BraveHeroDataKey_3, GlobalDataDefine.BraveHeroDataKey_4, GlobalDataDefine.BraveHeroDataKey_5,\
								GlobalDataDefine.BraveHeroDataKey_old_1, GlobalDataDefine.BraveHeroDataKey_old_2, GlobalDataDefine.BraveHeroDataKey_old_3, GlobalDataDefine.BraveHeroDataKey_old_4, GlobalDataDefine.BraveHeroDataKey_old_5],\
								 OnGetRankBack, None)


def InitGetRankEx():
	index = 1
	key = GlobalDataDefine.BraveHeroDataKey_1
	oldkey = GlobalDataDefine.BraveHeroDataKey_old_1
	GlobalHttp.GetGlobalDataByKeys([key, oldkey], OnGetRankBackEx, (index, key, oldkey))
	
	index = 2
	key = GlobalDataDefine.BraveHeroDataKey_2
	oldkey = GlobalDataDefine.BraveHeroDataKey_old_2
	GlobalHttp.GetGlobalDataByKeys([key, oldkey], OnGetRankBackEx, (index, key, oldkey))

	index = 3
	key = GlobalDataDefine.BraveHeroDataKey_3
	oldkey = GlobalDataDefine.BraveHeroDataKey_old_3
	GlobalHttp.GetGlobalDataByKeys([key, oldkey], OnGetRankBackEx, (index, key, oldkey))

	index = 4
	key = GlobalDataDefine.BraveHeroDataKey_4
	oldkey = GlobalDataDefine.BraveHeroDataKey_old_4
	GlobalHttp.GetGlobalDataByKeys([key, oldkey], OnGetRankBackEx, (index, key, oldkey))
	
	index = 5
	key = GlobalDataDefine.BraveHeroDataKey_5
	oldkey = GlobalDataDefine.BraveHeroDataKey_old_5
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
				print "GE_EXC, day error in OnGetRankBack"
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
				print "GE_EXC, old day error in OnGetRankBack"
		else:
			#旧数据太旧了，直接清理
			GlobalHttp.SetGlobalData(oldKey, (nowdays - 1, []))
	SetRankData(pType, nowRank, oldRank)

def OnGetRankBack(response, regparam):
	#数据返回了
	if response is None:
		#自返回
		return
	
	#分析和处理数据
	datadict = response
	days = cDateTime.Days()
	Checkdata(datadict, 1, days, GlobalDataDefine.BraveHeroDataKey_1, GlobalDataDefine.BraveHeroDataKey_old_1)
	Checkdata(datadict, 2, days, GlobalDataDefine.BraveHeroDataKey_2, GlobalDataDefine.BraveHeroDataKey_old_2)
	Checkdata(datadict, 3, days, GlobalDataDefine.BraveHeroDataKey_3, GlobalDataDefine.BraveHeroDataKey_old_3)
	Checkdata(datadict, 4, days, GlobalDataDefine.BraveHeroDataKey_4, GlobalDataDefine.BraveHeroDataKey_old_4)
	Checkdata(datadict, 5, days, GlobalDataDefine.BraveHeroDataKey_5, GlobalDataDefine.BraveHeroDataKey_old_5)
	

	#已经载入成功了
	global ReturnDB
	ReturnDB = True
	
	#同步数据给所有的逻辑进程
	SyncAllLogin()

def SyncAllLogin():
	#同步数据给所有的逻辑进程(今天和昨天)
	global LogicType_Dict
	for processId, pType in LogicType_Dict.iteritems():
		cp = ProcessMgr.ControlProcesssIds.get(processId)
		if not cp:
			if not Environment.IsDevelop:
				print "GE_EXC, SyncAllLogin not process sessionid (%s)" % processId
			continue
		sessionid = cp.session_id
		if pType == 1:
			ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdataBraveHeroRankToLogic, (RankCache_1, RankCache_old_1))
		elif pType == 2:
			ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdataBraveHeroRankToLogic, (RankCache_2, RankCache_old_2))
		elif pType == 3:
			ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdataBraveHeroRankToLogic, (RankCache_3, RankCache_old_3))
		elif pType == 4:
			ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdataBraveHeroRankToLogic, (RankCache_4, RankCache_old_4))
		elif pType == 5:
			ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdataBraveHeroRankToLogic, (RankCache_5, RankCache_old_5))
		else:
			print "GE_EXC, SyncAllLogin error pType (%s)" % pType

def SyncAllLoginToday():
	#同步当天最新的排行榜给所有的逻辑进程
	global LogicType_Dict
	for processId, pType in LogicType_Dict.iteritems():
		cp = ProcessMgr.ControlProcesssIds.get(processId)
		if not cp:
			if not Environment.IsDevelop:
				print "GE_EXC, SyncAllLoginToday not process sessionid (%s)" % processId
			continue
		sessionid = cp.session_id
		if pType == 1:
			ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdataBraveHeroRankToLogic_T, RankCache_1)
		elif pType == 2:
			ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdataBraveHeroRankToLogic_T, RankCache_2)
		elif pType == 3:
			ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdataBraveHeroRankToLogic_T, RankCache_3)
		elif pType == 4:
			ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdataBraveHeroRankToLogic_T, RankCache_4)
		elif pType == 5:
			ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdataBraveHeroRankToLogic_T, RankCache_5)
		else:
			print "GE_EXC, SyncAllLogin error pType (%s)" % pType

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
		ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdataBraveHeroRankToLogic, (RankCache_1, RankCache_old_1))
	elif pType == 2:
		ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdataBraveHeroRankToLogic, (RankCache_2, RankCache_old_2))
	elif pType == 3:
		ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdataBraveHeroRankToLogic, (RankCache_3, RankCache_old_3))
	elif pType == 4:
		ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdataBraveHeroRankToLogic, (RankCache_4, RankCache_old_4))
	elif pType == 5:
		ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdataBraveHeroRankToLogic, (RankCache_5, RankCache_old_5))
	else:
		print "GE_EXC, error pType (%s) in LoginRequestRank" % pType

def BraveHeroActive():
	#尝试激活勇者英雄坛
	for cfg in BraveHero_Dict.itervalues():
		cfg.Active()

if "_HasLoad" not in dir():
	if Environment.HasControl:
		LoadBraveHeroActiveConfig()
		LoadBraveHeroRankConfig()
		InitGetRankEx()
		cComplexServer.RegAfterNewHourCallFunction(AfterNewHour)
		cComplexServer.RegDistribute(PyMessage.Control_GetBraveHeroRank, LoginRequestRank)
		
	